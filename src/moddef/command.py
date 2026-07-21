# SPDX-License-Identifier: Apache-2.0

"""Command (multi-step register procedure) helpers, spec §11.7.

The executor itself is `Device.run_command` in device.py; this module holds
the pure pieces: poll-condition evaluation, single-PDU chunking caps, and
the synthetic points that let command params and raw trigger/poll values
reuse the shared codec.
"""

from __future__ import annotations

from collections.abc import Sequence

from moddef import schema
from moddef.codec.decode import decode_point_raw, is_signed

# Modbus single-PDU practical caps (FC03/FC16); larger transfers chunk.
MAX_READ_WORDS = 125
MAX_WRITE_WORDS = 123

# Default poll interval when a PollStep omits interval_ms.
DEFAULT_POLL_INTERVAL_MS = 250


def condition_met(c: schema.Condition, raw: int) -> bool:
    """Evaluate a §11.7 poll exit condition against a raw integer."""
    if c.op == schema.ConditionOp.EQ:
        return raw == c.value
    if c.op == schema.ConditionOp.NE:
        return raw != c.value
    if c.op == schema.ConditionOp.MASK:
        return (raw & c.mask) == c.value
    if c.op == schema.ConditionOp.RANGE:
        return c.min <= raw <= c.max
    return False


def param_point(cp: schema.CommandParam) -> schema.Point:
    """Synthetic point carrying a CommandParam's wire mapping for the codec."""
    return schema.Point(
        point_id=f"param:{cp.field}",
        storage_type=cp.storage_type,
        value_type=cp.value_type,
        mapping=cp.mapping,
    )


def raw_point(p: schema.Point) -> schema.Point:
    """Storage/mapping-only copy of a point: trigger writes and poll reads are
    raw register values (§11.7), bypassing transform and value_type."""
    return schema.Point(
        point_id=p.point_id,
        storage_type=p.storage_type,
        mapping=p.mapping if p.HasField("mapping") else None,
    )


def raw_int(p: schema.Point, regs: Sequence[int]) -> int:
    """Decode a point's raw (pre-transform) integer, sign-extended per storage."""
    raw, bits = decode_point_raw(p, regs)
    if is_signed(p.storage_type) and raw >= 1 << (bits - 1):
        raw -= 1 << bits
    return raw
