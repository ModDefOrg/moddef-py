# SPDX-License-Identifier: Apache-2.0

"""Typed errors (spec §26.3/§26.4, §32), mirroring the TS error classes."""

from __future__ import annotations


class ModDefError(Exception):
    """Base class for all moddef errors."""


class ParseError(ModDefError):
    """Document failed to parse (bad format, unknown field, bad enum value)."""


class PointNotFoundError(ModDefError):
    def __init__(self, point_id: str) -> None:
        super().__init__(f"point not found: {point_id}")
        self.point_id = point_id


class DeviceNotFoundError(ModDefError):
    def __init__(self, device_id: str) -> None:
        super().__init__(f"device profile not found: {device_id}")
        self.device_id = device_id


class DecodeError(ModDefError):
    def __init__(self, point_id: str, message: str) -> None:
        super().__init__(f"decode {point_id}: {message}")
        self.point_id = point_id


class EncodeError(ModDefError):
    def __init__(self, point_id: str, message: str) -> None:
        super().__init__(f"encode {point_id}: {message}")
        self.point_id = point_id


class UnsupportedMappingError(ModDefError):
    def __init__(self, subject: str, message: str) -> None:
        super().__init__(f"{subject}: {message}")
        self.subject = subject


class MeasurandNotSupportedError(ModDefError):
    def __init__(self, query: object) -> None:
        super().__init__(f"measurand not supported: {query}")
        self.query = query


class AmbiguousMeasurandError(ModDefError):
    """More than one point matches the measurand query (spec §26.4)."""

    def __init__(self, query: object, matches: list[str]) -> None:
        super().__init__(f"measurand query is ambiguous: {query} matches {matches}")
        self.query = query
        self.matches = matches


class WriteAccessError(ModDefError):
    def __init__(self, point_id: str, access: str) -> None:
        super().__init__(f"point {point_id} is not writable (access {access})")
        self.point_id = point_id


class WriteConstraintError(ModDefError):
    """§11.4 constraint violation; `constraint` names the violated rule."""

    def __init__(self, point_id: str, constraint: str, value: object, message: str) -> None:
        super().__init__(f"write {point_id}: {message}")
        self.point_id = point_id
        self.constraint = constraint
        self.value = value


class CommandNotFoundError(ModDefError):
    """A command id does not exist in the device profile (spec §11.7)."""

    def __init__(self, command_id: str) -> None:
        super().__init__(f"command not found: {command_id}")
        self.command_id = command_id


class RequiredParamMissingError(ModDefError):
    """A required command param was not supplied to run_command (spec §11.7)."""

    def __init__(self, command_id: str, field: str) -> None:
        super().__init__(f"command {command_id}: required param missing: {field}")
        self.command_id = command_id
        self.field = field


class PollTimeoutError(ModDefError):
    """A poll step exceeded its timeout_ms (spec §11.7)."""

    def __init__(self, point_id: str, timeout_ms: int) -> None:
        super().__init__(f"poll step timed out on {point_id} after {timeout_ms}ms")
        self.point_id = point_id
        self.timeout_ms = timeout_ms


class StepReferenceError(ModDefError):
    """A command step/result reference does not resolve (spec §11.7)."""

    def __init__(self, ref: str, kind: str) -> None:
        super().__init__(f"command step reference not found: {kind} {ref}")
        self.ref = ref
        self.kind = kind
