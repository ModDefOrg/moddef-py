"""Transport abstraction (spec §32.3): async register-level access.

`offset` is the zero-based data-model offset within the given address space
(spec §7.2); implementations apply any unit/base-address mapping. One
in-flight request per transport is the caller's responsibility (Modbus is a
serial request/response channel).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class Transport(Protocol):
    async def read_holding(self, offset: int, count: int) -> Sequence[int]: ...

    async def read_input(self, offset: int, count: int) -> Sequence[int]: ...

    async def read_coils(self, offset: int, count: int) -> Sequence[bool]: ...

    async def read_discrete(self, offset: int, count: int) -> Sequence[bool]: ...

    async def write_holding(self, offset: int, words: Sequence[int]) -> None: ...

    async def write_coil(self, offset: int, on: bool) -> None: ...
