# SPDX-License-Identifier: Apache-2.0

"""Decoded value model (spec §8, §13).

A decoded point value is one of: float (scaled DECIMAL/FLOAT), int (raw
UINT/INT/enum/BCD), bool, str, bytes, list[str] (§13.2 flag names),
dict[str, int] (§13 packed sub-fields), datetime (§8.5), or
[`Unavailable`] (§8.4 sentinel).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Unavailable:
    """The device reported "no data" for this point (spec §8.4)."""

    meaning: str = ""


DecodedValue = float | int | bool | str | bytes | list[str] | dict[str, int] | datetime | Unavailable
