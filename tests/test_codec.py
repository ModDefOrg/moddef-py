# SPDX-License-Identifier: Apache-2.0

"""Codec unit vectors mirroring go/codec tests, moddef-ts codec.test.ts and
moddef-rs conformance/tests/codec.rs: integer widths, endianness, scaling,
refs, strings, BCD, flags, fields, datetime, sentinels, composed values,
and encode round-trips."""

from datetime import datetime, timezone

import pytest

from moddef import DecodeError, Unavailable, decode_all, decode_point, encode_point, resolve_context
from tests.helpers import point


class TestIntegerDecoding:
    def test_u16_with_scale(self):
        p = point(
            pointId="v",
            storageType="U16",
            valueType={"primitive": "DECIMAL"},
            mapping={"space": "HOLDING_REGISTER", "offset": 0, "lengthWords": 1},
            transform={"scale": {"numerator": "1", "denominator": "10"}},
        )
        assert decode_point(p, [2305]) == pytest.approx(230.5)

    def test_s16_negative_twos_complement(self):
        p = point(
            pointId="t",
            storageType="S16",
            valueType={"primitive": "DECIMAL"},
            mapping={"lengthWords": 1},
            transform={"scale": {"numerator": "1", "denominator": "10"}},
        )
        assert decode_point(p, [0xFFF6]) == pytest.approx(-1.0)

    def test_u32_word_orders(self):
        big = point(
            pointId="e",
            storageType="U32",
            valueType={"primitive": "UINT32"},
            mapping={"lengthWords": 2, "byteOrder": "BIG_ENDIAN", "wordOrder": "WORD_BIG_ENDIAN"},
        )
        assert decode_point(big, [0x0001, 0x86A0]) == 100000

        little = point(
            pointId="e2",
            storageType="U32",
            valueType={"primitive": "UINT32"},
            mapping={"lengthWords": 2, "byteOrder": "BIG_ENDIAN", "wordOrder": "WORD_LITTLE_ENDIAN"},
        )
        assert decode_point(little, [0x86A0, 0x0001]) == 100000

    def test_u64(self):
        p = point(
            pointId="acc",
            storageType="U64",
            valueType={"primitive": "UINT64"},
            mapping={"lengthWords": 4},
        )
        assert decode_point(p, [0, 1, 0, 0]) == 4294967296

    def test_s48_sign_extension(self):
        p = point(
            pointId="n",
            storageType="S48",
            valueType={"primitive": "INT64"},
            mapping={"lengthWords": 3},
        )
        assert decode_point(p, [0xFFFF, 0xFFFF, 0xFFFE]) == -2

    def test_enum_backed_returns_raw(self):
        p = point(
            pointId="mode",
            storageType="U16",
            valueType={"enumRef": {"typeId": "work_mode"}},
            mapping={"lengthWords": 1},
        )
        assert decode_point(p, [5]) == 5


def test_ieee754_f32():
    # 230.5f = 0x43668000
    p = point(
        pointId="v",
        storageType="IEEE754_F32",
        valueType={"primitive": "FLOAT32"},
        mapping={"lengthWords": 2},
    )
    assert decode_point(p, [0x4366, 0x8000]) == pytest.approx(230.5, abs=1e-4)


class TestSentinels:
    def test_u16_ffff_unavailable(self):
        p = point(
            pointId="a",
            storageType="U16",
            valueType={"primitive": "DECIMAL"},
            mapping={"lengthWords": 1},
            naValues=[{"raw": "65535", "meaning": "not_implemented"}],
        )
        v = decode_point(p, [0xFFFF])
        assert v == Unavailable("not_implemented")
        assert not isinstance(decode_point(p, [0xFFFE]), Unavailable)

    def test_s16_sentinel_matches_masked_raw(self):
        p = point(
            pointId="a",
            storageType="S16",
            valueType={"primitive": "DECIMAL"},
            mapping={"lengthWords": 1},
            naValues=[{"raw": "32768"}],
        )
        assert isinstance(decode_point(p, [0x8000]), Unavailable)
        assert not isinstance(decode_point(p, [0x7FFF]), Unavailable)


class TestStringsBcdFlagsFields:
    def test_fixed_length_space_padded_ascii(self):
        p = point(
            pointId="sn",
            storageType="STRING_ASCII",
            valueType={"primitive": "STRING"},
            mapping={
                "lengthWords": 3,
                "stringEncoding": {"charset": "ASCII", "padding": "PADDING_SPACE", "termination": "FIXED_LENGTH"},
            },
        )
        # "AB12  "
        assert decode_point(p, [0x4142, 0x3132, 0x2020]) == "AB12"

    def test_bcd_digits(self):
        p = point(
            pointId="b",
            storageType="BCD",
            valueType={"primitive": "DECIMAL"},
            mapping={"lengthWords": 1},
        )
        assert decode_point(p, [0x1234]) == 1234

    def test_flag_set_names(self):
        p = point(
            pointId="alarms",
            storageType="U16",
            valueType={"flags": {"bits": {"0": "over_voltage", "2": "over_temp", "7": "door_open"}}},
            mapping={"lengthWords": 1},
        )
        assert decode_point(p, [0b10000101]) == ["over_voltage", "over_temp", "door_open"]
        assert decode_point(p, [0]) == []

    def test_register_fields_packed_hour_minute(self):
        p = point(
            pointId="slot",
            storageType="U16",
            valueType={"primitive": "UINT32"},
            fields=[
                {"fieldId": "hour", "bitOffset": 8, "bitLength": 8},
                {"fieldId": "minute", "bitOffset": 0, "bitLength": 8},
            ],
            mapping={"lengthWords": 1},
        )
        assert decode_point(p, [(21 << 8) | 45]) == {"hour": 21, "minute": 45}


def test_datetime_epoch_seconds():
    p = point(
        pointId="rtc",
        storageType="U32",
        valueType={"primitive": "DATETIME"},
        datetime={"encoding": "EPOCH_S", "width": "U32"},
        mapping={"lengthWords": 2},
    )
    v = decode_point(p, [0x6543, 0x2100])
    assert v == datetime.fromtimestamp(0x65432100, tz=timezone.utc)


class TestScaleRef:
    W = point(
        pointId="w",
        storageType="S16",
        valueType={"primitive": "DECIMAL"},
        mapping={"lengthWords": 1},
        transform={"scaleRef": {"pointId": "w_sf", "mode": "POW10"}},
    )

    def test_pow10(self):
        assert decode_point(self.W, [2301], {"w_sf": -1}) == pytest.approx(230.1)
        assert decode_point(self.W, [15], {"w_sf": 2}) == 1500

    def test_missing_ref_raises(self):
        with pytest.raises(DecodeError, match="scale_ref"):
            decode_point(self.W, [2301], {})

    def test_resolve_context_and_decode_all(self):
        sf = point(
            pointId="w_sf",
            storageType="S16",
            valueType={"primitive": "INT32"},
            mapping={"lengthWords": 1},
        )
        regs = {"w_sf": [0xFFFF], "w": [2301]}
        out = decode_all([sf, self.W], regs)
        assert out["w"] == pytest.approx(230.1)
        assert resolve_context([sf, self.W], regs) == {"w_sf": -1}


def test_composed_mantissa_exponent():
    p = point(
        pointId="pwr",
        storageType="COMPOSED",
        valueType={"primitive": "DECIMAL"},
        mapping={
            "lengthWords": 2,
            "composed": {
                "kind": "MANTISSA_EXPONENT",
                "base": "10",
                "mantissa": {"offset": 0, "lengthWords": 1},
                "exponent": {"offset": 1, "lengthWords": 1},
            },
        },
    )
    assert decode_point(p, [1500, 0xFFFF]) == pytest.approx(150.0)  # 1500 * 10^-1


def _embedded_composed(mantissa_storage, words=2, mantissa_bits=24):
    """§14.2 same-word mantissa/exponent point (embedded decade exponent)."""
    sub = {
        "offset": 0,
        "lengthWords": words,
        "byteOrder": "BIG_ENDIAN",
        "wordOrder": "WORD_BIG_ENDIAN",
    }
    return point(
        pointId="p",
        storageType="COMPOSED",
        valueType={"primitive": "DECIMAL"},
        mapping={
            "lengthWords": words,
            "composed": {
                "kind": "MANTISSA_EXPONENT",
                "base": "10",
                "mantissa": {**sub, "storageType": mantissa_storage,
                             "bitOffset": 0, "bitLength": mantissa_bits},
                "exponent": {**sub, "storageType": "S16",
                             "bitOffset": mantissa_bits, "bitLength": 8},
            },
        },
    )


def test_composed_embedded_exponent_iskra_t6():
    # FD 01 E2 40: exponent 0xFD = -3, mantissa 0x01E240 = 123456 -> 123.456.
    p = _embedded_composed("S32")
    assert decode_point(p, [0xFD01, 0xE240]) == pytest.approx(123.456)
    # Negative mantissa: -123456 = 0xFE1DC0 in 24-bit two's complement.
    assert decode_point(p, [0xFDFE, 0x1DC0]) == pytest.approx(-123.456)


def test_composed_embedded_unsigned_mantissa_iskra_t5():
    # Unsigned mantissa: a set bit 23 must not sign-extend.
    p = _embedded_composed("U32")
    assert decode_point(p, [0x0080, 0x0000]) == pytest.approx(8388608)


def test_composed_embedded_56bit_mantissa_eaton_pxm():
    # Eaton PXM GENERAL FORMAT: 8-bit exponent + 56-bit mantissa in 4 words.
    p = _embedded_composed("U64", words=4, mantissa_bits=56)
    # 123456789 * 10^-1 = 12345678.9
    assert decode_point(p, [0xFF00, 0x0000, 0x075B, 0xCD15]) == pytest.approx(12345678.9)


class TestEncodeRoundTrips:
    def test_scaled_u16(self):
        p = point(
            pointId="sp",
            storageType="U16",
            valueType={"primitive": "DECIMAL"},
            mapping={"lengthWords": 1},
            transform={"scale": {"numerator": "1", "denominator": "10"}},
        )
        regs = encode_point(p, 230.5)
        assert regs == [2305]
        assert decode_point(p, regs) == pytest.approx(230.5)

    def test_negative_offset_transform(self):
        # value = raw*0.1 - 1 (Growatt EPS power factor style)
        p = point(
            pointId="pf",
            storageType="U16",
            valueType={"primitive": "DECIMAL"},
            mapping={"lengthWords": 1},
            transform={
                "scale": {"numerator": "1", "denominator": "10"},
                "offset": {"numerator": "-1", "denominator": "1"},
            },
        )
        assert decode_point(p, [15]) == pytest.approx(0.5)
        assert encode_point(p, 0.5) == [15]

    def test_scale_ref_encode_divides(self):
        p = point(
            pointId="w",
            storageType="S16",
            valueType={"primitive": "DECIMAL"},
            mapping={"lengthWords": 1},
            transform={"scaleRef": {"pointId": "w_sf", "mode": "POW10"}},
        )
        assert encode_point(p, 230.1, {"w_sf": -1}) == [2301]

    def test_string_flags_bool_datetime_f32(self):
        s = point(
            pointId="s",
            storageType="STRING_ASCII",
            valueType={"primitive": "STRING"},
            mapping={
                "lengthWords": 2,
                "stringEncoding": {"charset": "ASCII", "padding": "PADDING_NULL", "termination": "FIXED_LENGTH"},
            },
        )
        assert decode_point(s, encode_point(s, "Hi!")) == "Hi!"

        fl = point(
            pointId="f",
            storageType="U16",
            valueType={"flags": {"bits": {"1": "a", "3": "b"}}},
            mapping={"lengthWords": 1},
        )
        assert decode_point(fl, encode_point(fl, ["b"])) == ["b"]

        b = point(
            pointId="b",
            storageType="U16",
            valueType={"primitive": "BOOL"},
            mapping={"lengthWords": 1},
        )
        assert decode_point(b, encode_point(b, True)) is True

        dt = point(
            pointId="d",
            storageType="U32",
            valueType={"primitive": "DATETIME"},
            datetime={"encoding": "EPOCH_S", "width": "U32"},
            mapping={"lengthWords": 2},
        )
        when = datetime.fromtimestamp(1700000000, tz=timezone.utc)
        assert decode_point(dt, encode_point(dt, when)) == when

        f32 = point(
            pointId="f32",
            storageType="IEEE754_F32",
            valueType={"primitive": "FLOAT32"},
            mapping={"lengthWords": 2},
        )
        assert decode_point(f32, encode_point(f32, 230.5)) == pytest.approx(230.5, abs=1e-4)

    def test_s16_negative_encode(self):
        p = point(
            pointId="t",
            storageType="S16",
            valueType={"primitive": "DECIMAL"},
            mapping={"lengthWords": 1},
            transform={"scale": {"numerator": "1", "denominator": "10"}},
        )
        assert encode_point(p, -1.0) == [0xFFF6]


def test_selector_ref_cases():
    p = point(
        pointId="energy",
        storageType="U32",
        valueType={"primitive": "DECIMAL"},
        mapping={"lengthWords": 2},
        selectorRef={
            "pointId": "fmt",
            "cases": {
                "0": {"scale": {"numerator": "1", "denominator": "1000"}, "unit": "kWh"},
                "1": {"scale": {"numerator": "1", "denominator": "1"}, "unit": "kWh"},
            },
        },
    )
    assert decode_point(p, [0, 5000], {"fmt": 0}) == pytest.approx(5.0)
    assert decode_point(p, [0, 5000], {"fmt": 1}) == 5000
