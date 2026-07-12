# SPDX-License-Identifier: Apache-2.0

"""Measurand queries (spec §22, §26.1). A query selects points by their
semantic tuple; unspecified qualifiers are wildcards, base_quantity is
required. Mirrors go/client measurandMatches and the TS/Rust ports."""

from __future__ import annotations

from dataclasses import dataclass

from moddef import schema


@dataclass(frozen=True)
class MeasurandQuery:
    base_quantity: str
    direction: int | None = None
    phase_ref: int | None = None
    aggregation: int | None = None
    location: int | None = None
    accumulation: int | None = None


def measurand_matches(m: schema.MeasurandRef | None, q: MeasurandQuery) -> bool:
    if m is None or m.base_quantity != q.base_quantity:
        return False
    for want, have in (
        (q.direction, m.direction),
        (q.phase_ref, m.phase_ref),
        (q.aggregation, m.aggregation),
        (q.location, m.location),
        (q.accumulation, m.accumulation),
    ):
        # None and *_UNSPECIFIED (0) are wildcards.
        if want and have != want:
            return False
    return True
