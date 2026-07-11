"""Codec (spec §8–§15): pure functions over schema Points, kept in
behavioral lockstep with go/codec, moddef-ts, and moddef-rs (shared vector
suite in tests/test_codec.py)."""

from moddef.codec.decode import (
    CodecContext,
    decode_all,
    decode_point,
    decode_point_raw,
    is_signed,
    resolve_context,
    storage_bits,
)
from moddef.codec.encode import encode_point, point_words

__all__ = [
    "CodecContext",
    "decode_all",
    "decode_point",
    "decode_point_raw",
    "encode_point",
    "is_signed",
    "point_words",
    "resolve_context",
    "storage_bits",
]
