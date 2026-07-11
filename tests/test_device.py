"""Device facade tests (spec §32.4, §26) mirroring the TS/Rust suites:
point reads across spaces, measurand queries with ambiguity handling,
SunSpec discovery with ID-relative model offsets (§7.3), scale_ref
companion reads, and constrained writes."""

import json

import pytest

from moddef import (
    AmbiguousMeasurandError,
    Device,
    MeasurandNotSupportedError,
    MeasurandQuery,
    PointNotFoundError,
    Unavailable,
    WriteAccessError,
    WriteConstraintError,
    parse_document,
    schema,
)
from tests.mock_transport import MockTransport

METER_DOC = parse_document(
    json.dumps(
        {
            "docId": "test.meter",
            "version": "1.0.0",
            "devices": [
                {
                    "deviceId": "meter",
                    "vendor": "Test",
                    "model": "M1",
                    "blocks": [
                        {
                            "blockId": "live",
                            "space": "INPUT_REGISTER",
                            "startOffset": 0,
                            "lengthWords": 16,
                            "points": [
                                {
                                    "pointId": "voltage_l1",
                                    "access": "READ_ONLY",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "DECIMAL"},
                                    "unit": "V",
                                    "mapping": {"space": "INPUT_REGISTER", "offset": 0, "lengthWords": 1},
                                    "transform": {"scale": {"numerator": "1", "denominator": "10"}},
                                    "measurand": {"baseQuantity": "voltage", "phaseRef": "L1_N"},
                                },
                                {
                                    "pointId": "voltage_l2",
                                    "access": "READ_ONLY",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "DECIMAL"},
                                    "unit": "V",
                                    "mapping": {"space": "INPUT_REGISTER", "offset": 1, "lengthWords": 1},
                                    "transform": {"scale": {"numerator": "1", "denominator": "10"}},
                                    "measurand": {"baseQuantity": "voltage", "phaseRef": "L2_N"},
                                    "naValues": [{"raw": "65535", "meaning": "not_implemented"}],
                                },
                                {
                                    "pointId": "frequency",
                                    "access": "READ_ONLY",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "DECIMAL"},
                                    "unit": "Hz",
                                    "mapping": {"space": "INPUT_REGISTER", "offset": 2, "lengthWords": 1},
                                    "transform": {"scale": {"numerator": "1", "denominator": "100"}},
                                    "measurand": {"baseQuantity": "frequency"},
                                },
                            ],
                        },
                        {
                            "blockId": "settings",
                            "space": "HOLDING_REGISTER",
                            "startOffset": 0,
                            "lengthWords": 8,
                            "points": [
                                {
                                    "pointId": "stop_soc",
                                    "access": "READ_WRITE",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "DECIMAL"},
                                    "unit": "%",
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 0, "lengthWords": 1},
                                    "write": {
                                        "behavior": "DIRECT",
                                        "constraints": {
                                            "minValue": {"numerator": "0", "denominator": "1"},
                                            "maxValue": {"numerator": "100", "denominator": "1"},
                                            "step": {"numerator": "1", "denominator": "1"},
                                        },
                                    },
                                },
                                {
                                    "pointId": "mode",
                                    "access": "READ_WRITE",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "UINT32"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 1, "lengthWords": 1},
                                    "write": {"behavior": "DIRECT", "constraints": {"allowedValues": ["0", "1", "2"]}},
                                },
                                {
                                    "pointId": "setpoint_scaled",
                                    "access": "READ_WRITE",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "DECIMAL"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 2, "lengthWords": 1},
                                    "transform": {"scale": {"numerator": "1", "denominator": "10"}},
                                    "write": {"behavior": "DIRECT"},
                                },
                            ],
                        },
                    ],
                }
            ],
        }
    ),
    "json",
)


def make_device() -> tuple[Device, MockTransport]:
    m = MockTransport()
    return Device.create(METER_DOC, "meter", m), m


class TestPointReads:
    async def test_reads_and_scales_input_registers(self):
        dev, m = make_device()
        m.input[0] = 2305
        assert await dev.read_point("voltage_l1") == pytest.approx(230.5)

    async def test_sentinel_returns_unavailable(self):
        dev, m = make_device()
        m.input[1] = 0xFFFF
        assert await dev.read_point("voltage_l2") == Unavailable("not_implemented")

    async def test_unknown_point_raises(self):
        dev, _ = make_device()
        with pytest.raises(PointNotFoundError):
            await dev.read_point("nope")


class TestMeasurandQueries:
    async def test_unqualified_unique_match(self):
        dev, m = make_device()
        m.input[2] = 4999
        assert await dev.read_measurand(MeasurandQuery("frequency")) == pytest.approx(49.99)

    async def test_qualified_phase_match(self):
        dev, m = make_device()
        m.input[0] = 2301
        q = MeasurandQuery("voltage", phase_ref=schema.PhaseRef.L1_N)
        assert await dev.read_measurand(q) == pytest.approx(230.1)

    async def test_ambiguous_raises_with_ids(self):
        dev, _ = make_device()
        with pytest.raises(AmbiguousMeasurandError) as ei:
            await dev.read_measurand(MeasurandQuery("voltage"))
        assert ei.value.matches == ["voltage_l1", "voltage_l2"]

    async def test_unsupported_raises(self):
        dev, _ = make_device()
        with pytest.raises(MeasurandNotSupportedError):
            await dev.read_measurand(MeasurandQuery("battery_power"))


class TestConstrainedWrites:
    async def test_valid_write(self):
        dev, m = make_device()
        await dev.write_point("stop_soc", 80)
        assert m.holding[0] == 80

    async def test_rejects_out_of_range_and_off_step(self):
        dev, _ = make_device()
        for bad in (101, -1, 50.5):
            with pytest.raises(WriteConstraintError):
                await dev.write_point("stop_soc", bad)

    async def test_allowed_values(self):
        dev, m = make_device()
        await dev.write_point("mode", 2)
        assert m.holding[1] == 2
        with pytest.raises(WriteConstraintError):
            await dev.write_point("mode", 3)

    async def test_inverse_transform_on_write(self):
        dev, m = make_device()
        await dev.write_point("setpoint_scaled", 23.5)
        assert m.holding[2] == 235

    async def test_rejects_read_only(self):
        dev, _ = make_device()
        with pytest.raises(WriteAccessError):
            await dev.write_point("voltage_l1", 1)


SUNSPEC_DOC = parse_document(
    json.dumps(
        {
            "docId": "test.sunspec",
            "version": "1.0.0",
            "devices": [
                {
                    "deviceId": "inv",
                    "blocks": [
                        {
                            "blockId": "inverter",
                            "space": "HOLDING_REGISTER",
                            "startOffset": 40070,
                            "lengthWords": 50,
                            "discovery": {"kind": "SUNSPEC", "anchorCandidates": [0, 40000, 50000], "modelId": 103},
                            "points": [
                                {
                                    "pointId": "w_sf",
                                    "access": "READ_ONLY",
                                    "storageType": "S16",
                                    "valueType": {"primitive": "INT32"},
                                    "mapping": {"space": "HOLDING_REGISTER", "modelRelativeOffset": 15, "lengthWords": 1},
                                },
                                {
                                    "pointId": "ac_power",
                                    "access": "READ_ONLY",
                                    "storageType": "S16",
                                    "valueType": {"primitive": "DECIMAL"},
                                    "unit": "W",
                                    "mapping": {"space": "HOLDING_REGISTER", "modelRelativeOffset": 14, "lengthWords": 1},
                                    "transform": {"scaleRef": {"pointId": "w_sf", "mode": "POW10"}},
                                    "measurand": {"baseQuantity": "active_power"},
                                },
                            ],
                        }
                    ],
                }
            ],
        }
    ),
    "json",
)


async def test_sunspec_discovery_id_relative_offsets():
    m = MockTransport(size=41000)
    m.holding[40000] = 0x5375  # "Su"
    m.holding[40001] = 0x6E53  # "nS"
    m.holding[40002] = 1  #       model 1 header
    m.holding[40003] = 66
    m.holding[40070] = 103  #     model 103 header (= 40002 + 2 + 66)
    m.holding[40071] = 50
    # Canonical model 103: W at ID+14, W_SF at ID+15.
    m.holding[40070 + 14] = 2301
    m.holding[40070 + 15] = 0xFFFF  # sf = -1
    m.holding[40122] = 0xFFFF  #      end of chain

    dev = Device.create(SUNSPEC_DOC, "inv", m)
    assert await dev.read_point("ac_power") == pytest.approx(230.1)

    # Model base is cached: a second read must not re-probe the anchor.
    probes = m.read_log.count("H@40000x2")
    await dev.read_point("ac_power")
    assert m.read_log.count("H@40000x2") == probes

    # The measurand path resolves through discovery too.
    assert await dev.read_measurand(MeasurandQuery("active_power")) == pytest.approx(230.1)
