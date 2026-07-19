# SPDX-License-Identifier: Apache-2.0

"""Point decoder (spec §8–§15). Faithful port of go/codec/decode.go and
moddef-ts decode.ts, including §10.5 selector_ref case application with
fallback to the point's own transform."""

from __future__ import annotations

import struct
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
from fractions import Fraction

from moddef import schema
from moddef.codec.bytes import assemble, decode_uint, last_n, mask_for, sign_extend
from moddef.errors import DecodeError
from moddef.values import DecodedValue, Unavailable

# Cross-point data needed during decode: integer values of the points
# referenced by scale_ref / selector_ref (spec §10.4/§10.5).
CodecContext = Mapping[str, int]


def decode_point(
    p: schema.Point,
    regs: Sequence[int],
    ctx: CodecContext | None = None,
) -> DecodedValue:
    """Decode the registers for a point into a typed value."""
    m = p.mapping

    # Composed (mantissa * base^exponent) decodes from sub-mappings (§14).
    if p.storage_type == schema.StorageType.COMPOSED or m.HasField("composed"):
        return _decode_composed(p, regs)

    byte_big = m.byte_order != schema.ByteOrder.LITTLE_ENDIAN
    word_big = m.word_order != schema.WordOrder.WORD_LITTLE_ENDIAN
    data = assemble(regs, byte_big, word_big)

    # Flag sets: names of set bits (§13.2).
    if p.value_type.WhichOneof("kind") == "flags":
        return _decode_flags(data, p.value_type.flags)

    # Bit / register fields: decode each sub-field from the window (§13).
    if p.fields or p.bit_fields:
        return _decode_fields(p, data)

    st = p.storage_type

    # Strings / raw bytes (§15).
    if st in (schema.StorageType.STRING_ASCII, schema.StorageType.STRING_UTF8):
        return _decode_string(data, m.string_encoding if m.HasField("string_encoding") else None)
    if st == schema.StorageType.BYTES_RAW:
        return data

    # Floats decode straight from IEEE bytes.
    if st == schema.StorageType.IEEE754_F32:
        (f,) = struct.unpack(">f", last_n(data, 4))
        return _apply_float_scale(f, p)
    if st == schema.StorageType.IEEE754_F64:
        (f,) = struct.unpack(">d", last_n(data, 8))
        return _apply_float_scale(f, p)

    # Integer-backed value.
    bits = storage_bits(st, len(regs))
    raw = decode_uint(data) & mask_for(bits)

    # Sentinel / unavailable check on the masked raw integer (§8.4).
    for na in p.na_values:
        if (na.raw & mask_for(bits)) == raw:
            return Unavailable(na.meaning)

    if st == schema.StorageType.BCD:
        return _bcd_to_int(data)

    signed = is_signed(st)
    raw_int = sign_extend(raw, bits) if signed else raw

    prim = (
        p.value_type.primitive
        if p.value_type.WhichOneof("kind") == "primitive"
        else schema.PrimitiveType.PRIMITIVE_TYPE_UNSPECIFIED
    )

    if prim == schema.PrimitiveType.BOOL:
        return raw != 0
    if prim == schema.PrimitiveType.DATETIME:
        return _decode_datetime(raw, p)
    if prim in (
        schema.PrimitiveType.DECIMAL,
        schema.PrimitiveType.FLOAT32,
        schema.PrimitiveType.FLOAT64,
    ):
        return _apply_scale(raw_int if signed else raw, p, ctx)
    if prim in (schema.PrimitiveType.UINT32, schema.PrimitiveType.UINT64):
        return raw
    if prim in (schema.PrimitiveType.INT32, schema.PrimitiveType.INT64):
        return raw_int
    # No primitive declared (e.g. enum_ref) — return the raw integer; the
    # caller maps it via the referenced enum. Signed if the storage is.
    return raw_int if signed else raw


def decode_point_raw(p: schema.Point, regs: Sequence[int]) -> tuple[int, int]:
    """Pre-scale integer view for callers that need exactness: (raw, bits)."""
    m = p.mapping
    byte_big = m.byte_order != schema.ByteOrder.LITTLE_ENDIAN
    word_big = m.word_order != schema.WordOrder.WORD_LITTLE_ENDIAN
    bits = storage_bits(p.storage_type, len(regs))
    raw = decode_uint(assemble(regs, byte_big, word_big)) & mask_for(bits)
    return raw, bits


def resolve_context(
    points: Iterable[schema.Point],
    regs_by_id: Mapping[str, Sequence[int]],
) -> dict[str, int]:
    """Decode every point that is a scale_ref/selector_ref target into ints."""
    wanted: set[str] = set()
    pts = list(points)
    for p in pts:
        if p.transform.HasField("scale_ref"):
            wanted.add(p.transform.scale_ref.point_id)
        if p.HasField("selector_ref"):
            wanted.add(p.selector_ref.point_id)
    ctx: dict[str, int] = {}
    for p in pts:
        if p.point_id in wanted and p.point_id in regs_by_id:
            v = decode_point(p, regs_by_id[p.point_id])
            if isinstance(v, bool):
                ctx[p.point_id] = int(v)
            elif isinstance(v, int):
                ctx[p.point_id] = v
            elif isinstance(v, float):
                ctx[p.point_id] = int(v)
    return ctx


def decode_all(
    points: Iterable[schema.Point],
    regs_by_id: Mapping[str, Sequence[int]],
) -> dict[str, DecodedValue]:
    """Decode several points, resolving refs among them first."""
    pts = list(points)
    ctx = resolve_context(pts, regs_by_id)
    return {
        p.point_id: decode_point(p, regs_by_id[p.point_id], ctx)
        for p in pts
        if p.point_id in regs_by_id
    }


# --- transform pipeline (§10) ------------------------------------------------ #


def _apply_scale(raw_int: int, p: schema.Point, ctx: CodecContext | None) -> float:
    r = Fraction(raw_int)

    # §10.5: value/scale/unit selected by another register; a matching case
    # replaces the point's own transform, otherwise fall through.
    if p.HasField("selector_ref"):
        key = None if ctx is None else ctx.get(p.selector_ref.point_id)
        if key is not None and key in p.selector_ref.cases:
            c = p.selector_ref.cases[key]
            if c.HasField("scale") and c.scale.denominator != 0:
                r *= Fraction(c.scale.numerator, c.scale.denominator)
            if c.HasField("offset") and c.offset.denominator != 0:
                r += Fraction(c.offset.numerator, c.offset.denominator)
            return float(r)

    t = p.transform
    if t.HasField("scale_ref"):
        sr = t.scale_ref
        sf = None if ctx is None else ctx.get(sr.point_id)
        if sf is None:
            raise DecodeError(p.point_id, f'scale_ref "{sr.point_id}" not resolved in context')
        if sr.mode == schema.ScaleMode.MULTIPLY:
            den = sr.denominator or 1
            r *= Fraction(sf, den)
        else:
            r *= Fraction(10) ** sf
    elif t.HasField("scale"):
        if t.scale.denominator == 0:
            raise DecodeError(p.point_id, "scale denominator is zero")
        r *= Fraction(t.scale.numerator, t.scale.denominator)

    if t.HasField("offset") and t.offset.denominator != 0:
        r += Fraction(t.offset.numerator, t.offset.denominator)
    return float(r)


def _apply_float_scale(f: float, p: schema.Point) -> float:
    t = p.transform
    if t.HasField("scale") and t.scale.denominator != 0:
        f = f * t.scale.numerator / t.scale.denominator
    if t.HasField("offset") and t.offset.denominator != 0:
        f += t.offset.numerator / t.offset.denominator
    return f


def _decode_composed(p: schema.Point, regs: Sequence[int]) -> float:
    if not p.mapping.HasField("composed"):
        raise DecodeError(p.point_id, "composed mapping missing")
    c = p.mapping.composed
    if c.base == 0:
        raise DecodeError(p.point_id, "composed base is zero")
    mant = _decode_sub_int(c.mantissa, regs)
    exp = _decode_sub_int(c.exponent, regs)
    r = Fraction(mant) * Fraction(c.base) ** exp
    return float(r)


def _decode_sub_int(m: schema.Mapping, regs: Sequence[int]) -> int:
    """Integer from a sub-mapping (word offset relative to the window).

    A bit window (bit_length > 0) selects [bit_offset, bit_offset+bit_length)
    of the assembled window and sign-extends from bit_length — the §14.2
    embedded decade exponent, where mantissa and exponent share a word (Iskra
    T5/T6, Eaton PXM). Signedness comes from the sub-mapping's storage_type;
    absent one, the value is signed (the pre-v0.5 behavior).
    """
    idx = m.offset
    n = m.length_words or 1
    if idx + n > len(regs):
        return 0
    byte_big = m.byte_order != schema.ByteOrder.LITTLE_ENDIAN
    word_big = m.word_order != schema.WordOrder.WORD_LITTLE_ENDIAN
    raw = decode_uint(assemble(regs[idx : idx + n], byte_big, word_big))

    st = m.storage_type
    bits = n * 16 if st == schema.StorageType.STORAGE_TYPE_UNSPECIFIED else storage_bits(st, n)
    if m.bit_length > 0:
        raw = (raw >> m.bit_offset) & mask_for(m.bit_length)
        bits = m.bit_length
    if st == schema.StorageType.STORAGE_TYPE_UNSPECIFIED or is_signed(st):
        return sign_extend(raw & mask_for(bits), bits)
    return raw & mask_for(bits)


def _decode_flags(data: bytes, fl: schema.FlagSet) -> list[str]:
    raw = decode_uint(data)
    return [fl.bits[bit] for bit in sorted(fl.bits) if raw & (1 << bit)]


def _decode_fields(p: schema.Point, data: bytes) -> dict[str, int]:
    raw = decode_uint(data)
    out: dict[str, int] = {}
    for f in list(p.bit_fields) + list(p.fields):
        out[f.field_id] = (raw >> f.bit_offset) & mask_for(f.bit_length)
    return out


def _decode_string(data: bytes, enc: schema.StringEncoding | None) -> str:
    end = len(data)
    if enc is not None and enc.termination == schema.Termination.NULL_TERMINATED:
        i = data.find(0)
        if i >= 0:
            end = i
    b = data[:end]
    if enc is not None:
        if enc.padding == schema.Padding.PADDING_NULL:
            b = b.rstrip(b"\x00")
        elif enc.padding == schema.Padding.PADDING_SPACE:
            b = b.rstrip(b" ")
    return b.decode("utf-8")


def _decode_datetime(raw: int, p: schema.Point) -> datetime:
    if p.datetime.encoding == schema.DateTimeEncoding.EPOCH_MS:
        return datetime.fromtimestamp(raw / 1000, tz=timezone.utc)
    # EPOCH_S and unspecified (matches the Go default branch).
    return datetime.fromtimestamp(raw, tz=timezone.utc)


# --- low-level helpers -------------------------------------------------------- #


def _bcd_to_int(data: bytes) -> int:
    v = 0
    for x in data:
        v = v * 100 + (x >> 4) * 10 + (x & 0x0F)
    return v


def storage_bits(st: int, words: int) -> int:
    S = schema.StorageType
    table = {
        S.BIT: 1,
        S.U16: 16,
        S.S16: 16,
        S.U24: 24,
        S.U32: 32,
        S.S32: 32,
        S.U48: 48,
        S.S48: 48,
        S.U64: 64,
        S.S64: 64,
    }
    if st in table:
        return table[st]
    if words <= 0:
        return 16
    return min(words * 16, 64)


def is_signed(st: int) -> bool:
    S = schema.StorageType
    return st in (S.S16, S.S32, S.S48, S.S64)
