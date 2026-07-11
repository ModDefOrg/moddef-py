"""pymodbus adapter: implements the moddef [`Transport`] protocol over a
pymodbus 3.x async client (spec §32.3). Install with `pip install
moddef[pymodbus]`.

- Constructors: [`PymodbusTransport.tcp`], [`PymodbusTransport.serial`]
  (RTU), or wrap any connected pymodbus async client directly.
- Reads are chunked to honor [`Options.max_read_words`] (Modbus caps a read
  at 125 registers; devices like the SDM630/EM24 need less — the same knob
  as the TS/Rust adapters).
- Every request runs under [`Options.timeout`] (`asyncio.timeout`).
- Modbus exception responses raise [`ModbusExceptionError`] carrying the
  device's exception code.

One in-flight request per transport: Modbus is a serial request/response
channel; concurrent access is a caller decision (e.g. an asyncio.Lock).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Sequence
from dataclasses import dataclass

from moddef.errors import ModDefError


@dataclass(frozen=True)
class Options:
    """Connection options shared by all constructors."""

    unit_id: int = 1
    timeout: float | None = 5.0
    max_read_words: int = 125

    def __post_init__(self) -> None:
        object.__setattr__(self, "max_read_words", max(1, min(self.max_read_words, 125)))


class ModbusExceptionError(ModDefError):
    """The device answered a Modbus exception (illegal address, busy, …)."""

    def __init__(self, exception_code: int) -> None:
        super().__init__(f"modbus exception (code {exception_code})")
        self.exception_code = exception_code


class ModbusTimeoutError(ModDefError):
    """[`Options.timeout`] elapsed before the device answered."""


class PymodbusTransport:
    """moddef Transport over a pymodbus async client."""

    def __init__(self, client, options: Options | None = None) -> None:
        self.client = client
        self.options = options or Options()

    @classmethod
    async def tcp(
        cls, host: str, port: int = 502, options: Options | None = None
    ) -> "PymodbusTransport":
        from pymodbus.client import AsyncModbusTcpClient

        options = options or Options()
        client = AsyncModbusTcpClient(host, port=port)
        await client.connect()
        return cls(client, options)

    @classmethod
    async def serial(
        cls,
        port: str,
        baudrate: int = 9600,
        options: Options | None = None,
        **serial_kwargs,
    ) -> "PymodbusTransport":
        """Modbus RTU over a serial port (parity/stopbits via serial_kwargs)."""
        from pymodbus.client import AsyncModbusSerialClient

        options = options or Options()
        client = AsyncModbusSerialClient(port, baudrate=baudrate, **serial_kwargs)
        await client.connect()
        return cls(client, options)

    def close(self) -> None:
        self.client.close()

    # --- Transport protocol -------------------------------------------------- #

    async def read_holding(self, offset: int, count: int) -> list[int]:
        out: list[int] = []
        for off, n in self._chunks(offset, count):
            rsp = await self._call(
                self.client.read_holding_registers(off, count=n, device_id=self.options.unit_id)
            )
            out.extend(rsp.registers[:n])
        return out

    async def read_input(self, offset: int, count: int) -> list[int]:
        out: list[int] = []
        for off, n in self._chunks(offset, count):
            rsp = await self._call(
                self.client.read_input_registers(off, count=n, device_id=self.options.unit_id)
            )
            out.extend(rsp.registers[:n])
        return out

    async def read_coils(self, offset: int, count: int) -> list[bool]:
        rsp = await self._call(
            self.client.read_coils(offset, count=count, device_id=self.options.unit_id)
        )
        return [bool(b) for b in rsp.bits[:count]]

    async def read_discrete(self, offset: int, count: int) -> list[bool]:
        rsp = await self._call(
            self.client.read_discrete_inputs(offset, count=count, device_id=self.options.unit_id)
        )
        return [bool(b) for b in rsp.bits[:count]]

    async def write_holding(self, offset: int, words: Sequence[int]) -> None:
        await self._call(
            self.client.write_registers(offset, list(words), device_id=self.options.unit_id)
        )

    async def write_coil(self, offset: int, on: bool) -> None:
        await self._call(self.client.write_coil(offset, on, device_id=self.options.unit_id))

    # --- internals ------------------------------------------------------------ #

    def _chunks(self, offset: int, count: int) -> list[tuple[int, int]]:
        step = self.options.max_read_words
        return [(offset + i, min(step, count - i)) for i in range(0, count, step)]

    async def _call(self, request: Awaitable):
        try:
            if self.options.timeout is not None:
                async with asyncio.timeout(self.options.timeout):
                    rsp = await request
            else:
                rsp = await request
        except TimeoutError as e:
            raise ModbusTimeoutError("modbus request timed out") from e
        if rsp.isError():
            raise ModbusExceptionError(getattr(rsp, "exception_code", 0))
        return rsp
