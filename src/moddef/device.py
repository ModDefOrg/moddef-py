"""Runtime device facade (spec §32.4): binds a Transport to one device
profile for point- and measurand-based reads/writes. Port of moddef-ts
`Device` / go/client/client.go.

SunSpec `model_relative_offset` is resolved against the model *ID register*
(offset 0 = model id, 1 = length, data at 2+) per spec §7.3 — the same
convention as the Go/TS/Rust clients and the profiles in devices/.

Shared limitation kept in lockstep: composed (multi-register
mantissa/exponent) points decode via the codec directly, not through the
facade.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from moddef import schema
from moddef.codec.decode import decode_point
from moddef.codec.encode import EncodableValue, encode_point, point_words
from moddef.errors import (
    AmbiguousMeasurandError,
    DeviceNotFoundError,
    MeasurandNotSupportedError,
    PointNotFoundError,
    UnsupportedMappingError,
    WriteAccessError,
    WriteConstraintError,
)
from moddef.measurand import MeasurandQuery, measurand_matches
from moddef.transport import Transport
from moddef.values import DecodedValue

# "SunS" marker as two big-endian 16-bit words.
_SUNS_MARKER = (0x5375, 0x6E53)


class Device:
    """The untyped runtime facade over one device profile."""

    def __init__(self, profile: schema.DeviceProfile, transport: Transport) -> None:
        self.profile = profile
        self.transport = transport
        self._points: dict[str, tuple[schema.Point, schema.RegisterBlock]] = {}
        self._order: list[schema.Point] = []
        self._model_base: dict[str, int] = {}
        for b in profile.blocks:
            for p in b.points:
                self._points[p.point_id] = (p, b)
                self._order.append(p)

    @classmethod
    def create(
        cls,
        doc: schema.ModDefDocument,
        device_id: str | None,
        transport: Transport,
    ) -> "Device":
        """Bind a transport to the named device profile in doc (or the only one)."""
        for d in doc.devices:
            if device_id is None or d.device_id == device_id:
                return cls(d, transport)
        raise DeviceNotFoundError(device_id or "(any)")

    # --- metadata (spec §32.1) -------------------------------------------- #

    def points(self) -> list[schema.Point]:
        return list(self._order)

    def point(self, point_id: str) -> tuple[schema.Point, schema.RegisterBlock]:
        try:
            return self._points[point_id]
        except KeyError:
            raise PointNotFoundError(point_id) from None

    # --- reads ------------------------------------------------------------- #

    async def read_point(self, point_id: str) -> DecodedValue:
        """Read and decode a single point by id."""
        p, _ = self.point(point_id)
        regs = await self._read_registers(p)
        ctx = await self._ref_context(p)
        return decode_point(p, regs, ctx)

    async def read_points(self, ids: Iterable[str]) -> dict[str, DecodedValue]:
        return {i: await self.read_point(i) for i in ids}

    async def read_measurand(self, q: MeasurandQuery) -> DecodedValue:
        """Read a point by its semantic measurand tuple (spec §26.1)."""
        matches = [
            p
            for p in self._order
            if p.HasField("measurand") and measurand_matches(p.measurand, q)
        ]
        if not matches:
            raise MeasurandNotSupportedError(q)
        if len(matches) > 1:
            raise AmbiguousMeasurandError(q, [p.point_id for p in matches])
        return await self.read_point(matches[0].point_id)

    # --- writes ------------------------------------------------------------ #

    async def write_point(self, point_id: str, value: EncodableValue) -> None:
        """Encode and write a value, validating access mode and §11.4 constraints."""
        p, blk = self.point(point_id)
        if p.access not in (
            schema.AccessMode.READ_WRITE,
            schema.AccessMode.WRITE_ONLY,
            schema.AccessMode.COMMAND,
        ):
            raise WriteAccessError(point_id, schema.AccessMode.Name(p.access))
        validate_constraints(p, value)

        space = self._space_of(p, blk)
        off = await self._offset_of(p, blk)

        if space == schema.AddressSpace.COIL:
            await self.transport.write_coil(off, value is True or value == 1)
            return
        if space != schema.AddressSpace.HOLDING_REGISTER:
            raise UnsupportedMappingError(
                point_id, f"cannot write address space {schema.AddressSpace.Name(space)}"
            )
        ctx = await self._ref_context(p)
        regs = encode_point(p, value, ctx)
        await self.transport.write_holding(off, regs)

    # --- internals ---------------------------------------------------------- #

    async def _ref_context(self, p: schema.Point) -> dict[str, int]:
        """Read the points referenced by p's scale_ref/selector_ref (§10.4/§10.5)."""
        ctx: dict[str, int] = {}
        ids: list[str] = []
        if p.transform.HasField("scale_ref"):
            ids.append(p.transform.scale_ref.point_id)
        if p.HasField("selector_ref"):
            ids.append(p.selector_ref.point_id)
        for rid in ids:
            rp, _ = self.point(rid)
            regs = await self._read_registers(rp)
            v = decode_point(rp, regs)
            if isinstance(v, bool):
                ctx[rid] = int(v)
            elif isinstance(v, (int, float)):
                ctx[rid] = int(v)
        return ctx

    def _space_of(self, p: schema.Point, blk: schema.RegisterBlock) -> int:
        s = p.mapping.space
        return blk.space if s == schema.AddressSpace.ADDRESS_SPACE_UNSPECIFIED else s

    async def _offset_of(self, p: schema.Point, blk: schema.RegisterBlock) -> int:
        if not p.HasField("mapping"):
            raise UnsupportedMappingError(p.point_id, "point has no mapping")
        if blk.HasField("discovery"):
            base = await self._resolve_model_base(blk)
            return base + p.mapping.model_relative_offset
        return p.mapping.offset

    async def _read_registers(self, p: schema.Point) -> Sequence[int]:
        if p.storage_type == schema.StorageType.COMPOSED:
            raise UnsupportedMappingError(
                p.point_id, "composed points are not read via the facade"
            )
        _, blk = self.point(p.point_id)
        space = self._space_of(p, blk)
        n = point_words(p)
        off = await self._offset_of(p, blk)
        return await self._read_space(space, off, n)

    async def _read_space(self, space: int, off: int, n: int) -> Sequence[int]:
        if space == schema.AddressSpace.HOLDING_REGISTER:
            return await self.transport.read_holding(off, n)
        if space == schema.AddressSpace.INPUT_REGISTER:
            return await self.transport.read_input(off, n)
        if space == schema.AddressSpace.COIL:
            bits = await self.transport.read_coils(off, 1)
            return [1 if bits[0] else 0]
        if space == schema.AddressSpace.DISCRETE_INPUT:
            bits = await self.transport.read_discrete(off, 1)
            return [1 if bits[0] else 0]
        raise UnsupportedMappingError("(block)", "unspecified address space")

    async def _resolve_model_base(self, blk: schema.RegisterBlock) -> int:
        """Probe discovery anchors for the SunS marker, walk the (model_id,
        length) chain, and return the register offset of the target model's
        ID register. Cached per block (spec §7.3)."""
        if blk.block_id in self._model_base:
            return self._model_base[blk.block_id]
        disc = blk.discovery
        if disc.kind != schema.DiscoveryKind.SUNSPEC:
            raise UnsupportedMappingError(blk.block_id, "unsupported discovery kind")
        space = blk.space
        candidates = list(disc.anchor_candidates) or [40000, 50000, 0]

        anchor = None
        for c in candidates:
            try:
                hdr = await self._read_space(space, c, 2)
            except Exception:
                continue  # devices answer exceptions off-anchor
            if tuple(hdr[:2]) == _SUNS_MARKER:
                anchor = c
                break
        if anchor is None:
            raise UnsupportedMappingError(
                blk.block_id, f"SunS marker not found at {candidates}"
            )

        # Walk model headers starting just after the marker.
        off = anchor + 2
        for _ in range(256):
            hdr = await self._read_space(space, off, 2)
            model_id, length = hdr[0], hdr[1]
            if model_id == 0xFFFF:
                break
            if model_id == disc.model_id:
                # Base is the model ID register (model_relative_offset 0, §7.3).
                self._model_base[blk.block_id] = off
                return off
            off += 2 + length
        raise UnsupportedMappingError(blk.block_id, f"SunSpec model {disc.model_id} not found")


def validate_constraints(p: schema.Point, value: EncodableValue) -> None:
    """Validate a write value against WriteConstraints (spec §11.4)."""
    if not (p.HasField("write") and p.write.HasField("constraints")):
        return
    c = p.write.constraints
    num = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None

    if c.allowed_values:
        iv = round(num) if num is not None else None
        if iv is None or iv not in c.allowed_values:
            raise WriteConstraintError(
                p.point_id,
                "allowed_values",
                value,
                f"value {value!r} not in allowed_values {list(c.allowed_values)}",
            )
        return
    if num is None:
        return
    if c.HasField("min_value") and c.min_value.denominator != 0:
        lo = c.min_value.numerator / c.min_value.denominator
        if num < lo:
            raise WriteConstraintError(p.point_id, "min_value", value, f"value {num} below minimum {lo}")
    if c.HasField("max_value") and c.max_value.denominator != 0:
        hi = c.max_value.numerator / c.max_value.denominator
        if num > hi:
            raise WriteConstraintError(p.point_id, "max_value", value, f"value {num} above maximum {hi}")
    if c.HasField("step") and c.step.denominator != 0 and c.step.numerator != 0:
        step = c.step.numerator / c.step.denominator
        base = (
            c.min_value.numerator / c.min_value.denominator
            if c.HasField("min_value") and c.min_value.denominator != 0
            else 0.0
        )
        k = (num - base) / step
        if abs(k - round(k)) > 1e-9:
            raise WriteConstraintError(
                p.point_id, "step", value, f"value {num} is not a multiple of step {step}"
            )
