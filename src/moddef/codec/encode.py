"""Point encoder (spec §10 inverse, §11.5). Port of go/codec/encode.go and
moddef-ts encode.ts: composed values, register-field structs, and
selector_ref remain read-oriented and are not supported for encode."""

from __future__ import annotations

import struct
from collections.abc import Sequence
from datetime import datetime
from fractions import Fraction

from moddef import schema
from moddef.codec.bytes import mask_for, pad_bytes, words_from_bytes, words_from_uint
from moddef.codec.decode import CodecContext, storage_bits
from moddef.errors import EncodeError

EncodableValue = float | int | bool | str | bytes | Sequence[str] | datetime


def point_words(p: schema.Point) -> int:
    """Register count to read/write for p (mapping length or storage width)."""
    if p.mapping.length_words:
        return p.mapping.length_words
    S = schema.StorageType
    st = p.storage_type
    if st in (S.U32, S.S32, S.IEEE754_F32, S.U24):
        return 2
    if st in (S.U48, S.S48):
        return 3
    if st in (S.U64, S.S64, S.IEEE754_F64):
        return 4
    return 1


def encode_point(
    p: schema.Point,
    value: EncodableValue,
    ctx: CodecContext | None = None,
) -> list[int]:
    """Serialize a typed value into register words per the point's mapping."""
    S = schema.StorageType
    st = p.storage_type
    m = p.mapping
    byte_big = m.byte_order != schema.ByteOrder.LITTLE_ENDIAN
    word_big = m.word_order != schema.WordOrder.WORD_LITTLE_ENDIAN
    n = point_words(p)

    if st == S.COMPOSED:
        raise EncodeError(p.point_id, "composed values are not writable")

    if st in (S.STRING_ASCII, S.STRING_UTF8):
        if not isinstance(value, str):
            raise EncodeError(p.point_id, f"string expects str, got {type(value).__name__}")
        return words_from_bytes(pad_bytes(value.encode("utf-8"), n * 2), byte_big, word_big)

    if st == S.BYTES_RAW:
        if not isinstance(value, (bytes, bytearray)):
            raise EncodeError(p.point_id, f"BYTES_RAW expects bytes, got {type(value).__name__}")
        return words_from_bytes(pad_bytes(bytes(value), n * 2), byte_big, word_big)

    if st == S.IEEE754_F32:
        return words_from_bytes(struct.pack(">f", float(value)), byte_big, word_big)
    if st == S.IEEE754_F64:
        return words_from_bytes(struct.pack(">d", float(value)), byte_big, word_big)

    bits = storage_bits(st, n)

    # §13.2 flag sets encode from a list of flag names.
    if p.value_type.WhichOneof("kind") == "flags":
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
            raise EncodeError(p.point_id, "flags expect a sequence of flag names")
        by_name = {name: bit for bit, name in p.value_type.flags.bits.items()}
        raw = 0
        for name in value:
            if name not in by_name:
                raise EncodeError(p.point_id, f"unknown flag: {name}")
            raw |= 1 << by_name[name]
        return words_from_uint(raw & mask_for(bits), n, byte_big, word_big)

    if p.fields or p.bit_fields:
        raise EncodeError(p.point_id, "packed field windows are read-oriented")

    prim = (
        p.value_type.primitive
        if p.value_type.WhichOneof("kind") == "primitive"
        else schema.PrimitiveType.PRIMITIVE_TYPE_UNSPECIFIED
    )

    if prim == schema.PrimitiveType.BOOL:
        raw = 1 if value else 0
    elif prim == schema.PrimitiveType.DATETIME:
        if not isinstance(value, datetime):
            raise EncodeError(p.point_id, "DATETIME expects datetime")
        ts = value.timestamp()
        raw = int(ts * 1000) if p.datetime.encoding == schema.DateTimeEncoding.EPOCH_MS else int(ts)
    elif prim in (
        schema.PrimitiveType.DECIMAL,
        schema.PrimitiveType.FLOAT32,
        schema.PrimitiveType.FLOAT64,
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise EncodeError(p.point_id, f"numeric point expects a number, got {type(value).__name__}")
        raw = _encode_scaled(value, p, ctx)
    elif isinstance(value, bool):
        raw = int(value)
    elif isinstance(value, (int, float)):
        raw = int(value)
    else:
        raise EncodeError(p.point_id, f"integer point expects a number, got {type(value).__name__}")

    if st == S.BCD:
        raw = _int_to_bcd(raw)

    return words_from_uint(raw & mask_for(bits), n, byte_big, word_big)


def _encode_scaled(value: float, p: schema.Point, ctx: CodecContext | None) -> int:
    """Inverse transform pipeline: raw = (value - offset) / scale."""
    # Exact decimal rational of the value (str() gives the shortest repr, so
    # typical engineering values like 230.1 stay exact — parity with TS).
    r = Fraction(str(value)) if isinstance(value, float) else Fraction(value)

    t = p.transform
    if t.HasField("offset") and t.offset.denominator != 0:
        r -= Fraction(t.offset.numerator, t.offset.denominator)
    if t.HasField("scale_ref"):
        sr = t.scale_ref
        sf = None if ctx is None else ctx.get(sr.point_id)
        if sf is None:
            raise EncodeError(p.point_id, f'scale_ref "{sr.point_id}" not resolved in context')
        if sr.mode == schema.ScaleMode.MULTIPLY:
            den = sr.denominator or 1
            r /= Fraction(sf, den)
        else:
            r /= Fraction(10) ** sf
    elif t.HasField("scale"):
        if t.scale.denominator == 0:
            raise EncodeError(p.point_id, "scale denominator is zero")
        r /= Fraction(t.scale.numerator, t.scale.denominator)

    return _round_half_away(r)


def _round_half_away(r: Fraction) -> int:
    """Round to nearest integer, half away from zero (matches Go ratRound)."""
    n, d = r.numerator, r.denominator
    if n >= 0:
        return (n + d // 2) // d
    return -((-n + d // 2) // d)


def _int_to_bcd(v: int) -> int:
    raw = 0
    shift = 0
    while v > 0:
        raw |= (v % 10) << shift
        shift += 4
        v //= 10
    return raw
