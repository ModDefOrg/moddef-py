"""In-memory transport for facade tests; reads beyond the configured size
fail like a device answering a Modbus exception (used to skip discovery
anchors)."""

from __future__ import annotations


class OutOfRangeError(Exception):
    pass


class MockTransport:
    def __init__(self, size: int = 64) -> None:
        self.holding = [0] * size
        self.input = [0] * size
        self.coils = [False] * size
        self.discrete = [False] * size
        self.read_log: list[str] = []

    def _window(self, bank: list, offset: int, count: int) -> list:
        if offset + count > len(bank):
            raise OutOfRangeError(f"read {offset}+{count} beyond {len(bank)}")
        return bank[offset : offset + count]

    async def read_holding(self, offset: int, count: int) -> list[int]:
        self.read_log.append(f"H@{offset}x{count}")
        return self._window(self.holding, offset, count)

    async def read_input(self, offset: int, count: int) -> list[int]:
        self.read_log.append(f"I@{offset}x{count}")
        return self._window(self.input, offset, count)

    async def read_coils(self, offset: int, count: int) -> list[bool]:
        return self._window(self.coils, offset, count)

    async def read_discrete(self, offset: int, count: int) -> list[bool]:
        return self._window(self.discrete, offset, count)

    async def write_holding(self, offset: int, words) -> None:
        if offset + len(words) > len(self.holding):
            raise OutOfRangeError("write beyond bank")
        self.holding[offset : offset + len(words)] = [w & 0xFFFF for w in words]

    async def write_coil(self, offset: int, on: bool) -> None:
        if offset >= len(self.coils):
            raise OutOfRangeError("write beyond bank")
        self.coils[offset] = on
