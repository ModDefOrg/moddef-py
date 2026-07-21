# SPDX-License-Identifier: Apache-2.0

"""Command executor tests (spec §11.7) mirroring the Go/TS suites: linear
step order, param/trigger writes, poll conditions on raw values with
timeout, length_ref-sized reads, chunked >1-PDU transfers, and result
assembly from bindings."""

import json

import pytest

from moddef import (
    CommandNotFoundError,
    Device,
    PollTimeoutError,
    RequiredParamMissingError,
    condition_met,
    parse_document,
    schema,
)
from tests.mock_transport import MockTransport

CMD_DOC = parse_document(
    json.dumps(
        {
            "docId": "test.commands",
            "version": "1.0.0",
            "devices": [
                {
                    "deviceId": "cmd-device",
                    "vendor": "Test",
                    "model": "CMD-1",
                    "blocks": [
                        {
                            "blockId": "job",
                            "space": "HOLDING_REGISTER",
                            "startOffset": 0,
                            "lengthWords": 1000,
                            "points": [
                                {
                                    "pointId": "control",
                                    "access": "COMMAND",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "UINT32"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 10, "lengthWords": 1},
                                    "write": {"behavior": "COMMAND_TRIGGER"},
                                },
                                {
                                    "pointId": "status",
                                    "access": "READ_ONLY",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "UINT32"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 11, "lengthWords": 1},
                                },
                                {
                                    "pointId": "busy_flags",
                                    "access": "READ_ONLY",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "UINT32"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 12, "lengthWords": 1},
                                },
                                {
                                    "pointId": "result_length",
                                    "access": "READ_ONLY",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "UINT32"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 20, "lengthWords": 1},
                                },
                                {
                                    "pointId": "result_data",
                                    "access": "READ_ONLY",
                                    "storageType": "BYTES_RAW",
                                    "valueType": {"primitive": "BYTES"},
                                    "mapping": {
                                        "space": "HOLDING_REGISTER",
                                        "offset": 21,
                                        "lengthWords": 8,
                                        "byteOrder": "BIG_ENDIAN",
                                        "wordOrder": "WORD_BIG_ENDIAN",
                                        "lengthRef": {"pointId": "result_length"},
                                    },
                                },
                                {
                                    "pointId": "blob",
                                    "access": "READ_ONLY",
                                    "storageType": "BYTES_RAW",
                                    "valueType": {"primitive": "BYTES"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 500, "lengthWords": 300},
                                },
                            ],
                        }
                    ],
                    "commands": [
                        {
                            "commandId": "run_job",
                            "params": [
                                {
                                    "field": "payload",
                                    "storageType": "BYTES_RAW",
                                    "valueType": {"primitive": "BYTES"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 0, "lengthWords": 4},
                                },
                                {
                                    "field": "mode",
                                    "storageType": "U16",
                                    "valueType": {"primitive": "UINT32"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 5, "lengthWords": 1},
                                    "required": True,
                                },
                            ],
                            "steps": [
                                {"name": "write_payload", "write": {"param": "payload"}},
                                {"name": "write_mode", "write": {"param": "mode"}},
                                {"name": "arm", "write": {"trigger": {"pointId": "control", "value": "1"}}},
                                {
                                    "name": "wait_not_busy",
                                    "poll": {
                                        "pointId": "busy_flags",
                                        "until": {"op": "MASK", "mask": "1", "value": "0"},
                                        "intervalMs": 2,
                                        "timeoutMs": 500,
                                    },
                                },
                                {
                                    "name": "wait_done",
                                    "poll": {
                                        "pointId": "status",
                                        "until": {"op": "EQ", "value": "0"},
                                        "intervalMs": 2,
                                        "timeoutMs": 500,
                                    },
                                },
                                {"name": "fetch_length", "read": {"pointId": "result_length", "into": "length"}},
                                {"name": "fetch_data", "read": {"pointId": "result_data", "into": "data"}},
                            ],
                            "results": [
                                {"field": "data", "from": "data", "valueType": {"primitive": "BYTES"}},
                                {"field": "length", "from": "length", "valueType": {"primitive": "UINT32"}},
                            ],
                        },
                        {
                            "commandId": "wait_forever",
                            "steps": [
                                {
                                    "name": "poll",
                                    "poll": {
                                        "pointId": "status",
                                        "until": {"op": "EQ", "value": "9"},
                                        "intervalMs": 2,
                                        "timeoutMs": 20,
                                    },
                                }
                            ],
                        },
                        {
                            "commandId": "xfer",
                            "params": [
                                {
                                    "field": "input",
                                    "storageType": "BYTES_RAW",
                                    "valueType": {"primitive": "BYTES"},
                                    "mapping": {"space": "HOLDING_REGISTER", "offset": 600, "lengthWords": 200},
                                    "required": True,
                                }
                            ],
                            "steps": [
                                {"name": "w", "write": {"param": "input"}},
                                {"name": "r", "read": {"pointId": "blob", "into": "blob"}},
                            ],
                            "results": [{"field": "blob", "from": "blob"}],
                        },
                    ],
                }
            ],
        }
    ),
    "json",
)


class CmdTransport(MockTransport):
    """MockTransport with per-offset successive reads and an ordered write log."""

    def __init__(self, size: int = 1024) -> None:
        super().__init__(size)
        self.seq: dict[int, list[int]] = {}
        self.writes: list[tuple[int, list[int]]] = []

    async def read_holding(self, offset: int, count: int) -> list[int]:
        vals = self.seq.get(offset)
        if vals:
            v = vals.pop(0) if len(vals) > 1 else vals[0]
            return [v]
        return await super().read_holding(offset, count)

    async def write_holding(self, offset: int, words) -> None:
        self.writes.append((offset, list(words)))
        await super().write_holding(offset, words)


def device(t: CmdTransport) -> Device:
    return Device.create(CMD_DOC, "cmd-device", t)


@pytest.mark.asyncio
async def test_run_command_full_cycle() -> None:
    t = CmdTransport()
    t.seq[12] = [1, 0]  # busy clears on the second poll
    t.seq[11] = [5, 0]  # status goes 0 on the second poll
    t.holding[20] = 2  # result_length: 2 of the 8-word window
    t.holding[21] = 0xDEAD
    t.holding[22] = 0xBEEF
    t.holding[23] = 0xFFFF  # beyond the live length; must not be included

    out = await device(t).run_command(
        "run_job", {"mode": 7, "payload": bytes([1, 2, 3, 4])}
    )

    # Step wire order: payload @0, mode @5, trigger @10.
    assert [w[0] for w in t.writes] == [0, 5, 10]
    assert t.writes[0][1] == [0x0102, 0x0304, 0, 0]
    assert t.writes[1][1] == [7]
    assert t.writes[2][1] == [1]

    # length_ref-sized read: 2 words -> 4 bytes, not the 8-word clamp.
    assert out["data"] == bytes([0xDE, 0xAD, 0xBE, 0xEF])
    assert out["length"] == 2


@pytest.mark.asyncio
async def test_read_point_honours_length_ref() -> None:
    t = CmdTransport()
    t.holding[20] = 3
    t.holding[21:24] = [0x0102, 0x0304, 0x0506]
    v = await device(t).read_point("result_data")
    assert v == bytes([1, 2, 3, 4, 5, 6])


@pytest.mark.asyncio
async def test_run_command_errors() -> None:
    t = CmdTransport()
    with pytest.raises(CommandNotFoundError):
        await device(t).run_command("nope")
    with pytest.raises(RequiredParamMissingError):
        await device(t).run_command("run_job", {"payload": b"\x01"})


@pytest.mark.asyncio
async def test_poll_timeout() -> None:
    t = CmdTransport()
    with pytest.raises(PollTimeoutError):
        await device(t).run_command("wait_forever")


@pytest.mark.asyncio
async def test_chunked_io() -> None:
    t = CmdTransport()
    out = await device(t).run_command("xfer", {"input": bytes(400)})
    # 200-word write in <=123-word chunks: 123 + 77; second at offset 600+123.
    assert [len(w[1]) for w in t.writes] == [123, 77]
    assert t.writes[1][0] == 600 + 123
    # 300-word read chunked but reassembled: 600 bytes.
    assert len(out["blob"]) == 600


def test_condition_ops() -> None:
    def cond(**kw):
        return schema.Condition(**kw)

    assert condition_met(cond(op=schema.ConditionOp.EQ, value=5), 5)
    assert not condition_met(cond(op=schema.ConditionOp.EQ, value=5), 4)
    assert condition_met(cond(op=schema.ConditionOp.NE, value=5), 4)
    assert not condition_met(cond(op=schema.ConditionOp.NE, value=5), 5)
    assert condition_met(cond(op=schema.ConditionOp.MASK, mask=0x0F, value=0x03), 0xF3)
    assert not condition_met(cond(op=schema.ConditionOp.MASK, mask=0x0F, value=0x03), 0xF4)
    assert condition_met(cond(op=schema.ConditionOp.RANGE, min=10, max=20), 15)
    assert not condition_met(cond(op=schema.ConditionOp.RANGE, min=10, max=20), 21)
    assert not condition_met(schema.Condition(), 0)
