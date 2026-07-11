"""Register/byte assembly honoring byte order within a word and word order
across words (spec §9). Mirrors go/codec and the TS/Rust byte helpers."""

from __future__ import annotations

from collections.abc import Sequence


def assemble(regs: Sequence[int], byte_big: bool, word_big: bool) -> bytes:
    """Normalize registers into a big-endian byte stream."""
    n = len(regs)
    out = bytearray(n * 2)
    for i in range(n * 2):
        w = i // 2
        reg = regs[w if word_big else n - 1 - w] & 0xFFFF
        hi = (i % 2 == 0) if byte_big else (i % 2 == 1)
        out[i] = (reg >> 8) & 0xFF if hi else reg & 0xFF
    return bytes(out)


def decode_uint(b: bytes) -> int:
    """Big-endian unsigned integer of the byte stream (arbitrary width)."""
    return int.from_bytes(b, "big")


def words_from_uint(raw: int, n_words: int, byte_big: bool, word_big: bool) -> list[int]:
    """Split an unsigned integer into registers (inverse of assemble+decode)."""
    b = (raw & mask_for(n_words * 16)).to_bytes(n_words * 2, "big")
    return words_from_bytes(b, byte_big, word_big)


def words_from_bytes(b: bytes, byte_big: bool, word_big: bool) -> list[int]:
    """Write a normalized big-endian byte stream into registers."""
    n = (len(b) + 1) // 2
    regs = [0] * n
    for i in range(n * 2):
        byte = b[i] if i < len(b) else 0
        w = i // 2
        reg = w if word_big else n - 1 - w
        hi = (i % 2 == 0) if byte_big else (i % 2 == 1)
        regs[reg] |= (byte << 8) if hi else byte
    return regs


def pad_bytes(b: bytes, total: int) -> bytes:
    """Zero-pad (or truncate) to exactly `total` bytes."""
    if len(b) >= total:
        return b[:total]
    return b + bytes(total - len(b))


def last_n(b: bytes, n: int) -> bytes:
    return b[-n:] if len(b) > n else b


def mask_for(bits: int) -> int:
    return (1 << bits) - 1


def sign_extend(v: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return v - (1 << bits) if v & sign else v
