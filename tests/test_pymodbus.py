# SPDX-License-Identifier: Apache-2.0

"""Adapter integration test against an in-process pymodbus TCP server:
chunked reads honoring max_read_words, write paths, exception mapping, and
driving the Device facade end-to-end over real TCP."""

import asyncio
import json

import pytest

from moddef import Device, parse_document
from moddef.pymodbus import ModbusExceptionError, Options, PymodbusTransport

pymodbus_server = pytest.importorskip("pymodbus.server")

from pymodbus.server import ModbusTcpServer  # noqa: E402
from pymodbus.simulator import DataType, SimData, SimDevice  # noqa: E402


@pytest.fixture
async def server():
    """Ephemeral-port pymodbus TCP server; yields its port.

    Registers: holding 0..299 hold their own offset, input 0..63 hold 7;
    anything beyond answers a Modbus exception.
    """
    bits = [SimData(address=0, count=16, values=False, datatype=DataType.BITS)]
    holding = [SimData(address=0, values=list(range(300)), datatype=DataType.REGISTERS)]
    inputs = [SimData(address=0, values=[7] * 64, datatype=DataType.REGISTERS)]
    dev = SimDevice(id=1, simdata=(bits, bits, holding, inputs))
    srv = ModbusTcpServer(dev, address=("127.0.0.1", 0))
    await srv.serve_forever(background=True)
    port = srv.transport.sockets[0].getsockname()[1]
    yield port
    await srv.shutdown()


async def test_chunked_reads_writes_and_exceptions(server):
    port = server
    t = await PymodbusTransport.tcp("127.0.0.1", port, Options(max_read_words=100))

    # 250 words with max_read_words=100 → 3 requests, data intact.
    regs = await t.read_holding(10, 250)
    assert regs[0] == 10
    assert regs[249] == 259

    one = await t.read_input(63, 1)
    assert one == [7]

    await t.write_holding(5, [42, 43])
    assert await t.read_holding(5, 2) == [42, 43]

    # Out-of-range read surfaces the device's exception code.
    with pytest.raises(ModbusExceptionError):
        await t.read_holding(299, 4)
    t.close()


async def test_device_facade_over_tcp(server):
    port = server
    doc = parse_document(
        json.dumps(
            {
                "docId": "test.tcp",
                "version": "1.0.0",
                "devices": [
                    {
                        "deviceId": "meter",
                        "blocks": [
                            {
                                "blockId": "live",
                                "space": "HOLDING_REGISTER",
                                "lengthWords": 8,
                                "points": [
                                    {
                                        "pointId": "voltage",
                                        "access": "READ_WRITE",
                                        "storageType": "U16",
                                        "valueType": {"primitive": "DECIMAL"},
                                        "mapping": {"space": "HOLDING_REGISTER", "offset": 2, "lengthWords": 1},
                                        "transform": {"scale": {"numerator": "1", "denominator": "10"}},
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ),
        "json",
    )
    t = await PymodbusTransport.tcp("127.0.0.1", port, Options())
    dev = Device.create(doc, "meter", t)
    await dev.write_point("voltage", 230.5)
    assert await dev.read_point("voltage") == pytest.approx(230.5)
    t.close()
