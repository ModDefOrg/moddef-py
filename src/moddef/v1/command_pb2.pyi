from moddef.v1 import mapping_pb2 as _mapping_pb2
from moddef.v1 import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConditionOp(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONDITION_OP_UNSPECIFIED: _ClassVar[ConditionOp]
    EQ: _ClassVar[ConditionOp]
    NE: _ClassVar[ConditionOp]
    MASK: _ClassVar[ConditionOp]
    RANGE: _ClassVar[ConditionOp]
CONDITION_OP_UNSPECIFIED: ConditionOp
EQ: ConditionOp
NE: ConditionOp
MASK: ConditionOp
RANGE: ConditionOp

class Condition(_message.Message):
    __slots__ = ("op", "value", "mask", "min", "max")
    OP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    MASK_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    op: ConditionOp
    value: int
    mask: int
    min: int
    max: int
    def __init__(self, op: _Optional[_Union[ConditionOp, str]] = ..., value: _Optional[int] = ..., mask: _Optional[int] = ..., min: _Optional[int] = ..., max: _Optional[int] = ...) -> None: ...

class TriggerWrite(_message.Message):
    __slots__ = ("point_id", "value")
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    value: int
    def __init__(self, point_id: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...

class WriteStep(_message.Message):
    __slots__ = ("param", "trigger")
    PARAM_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    param: str
    trigger: TriggerWrite
    def __init__(self, param: _Optional[str] = ..., trigger: _Optional[_Union[TriggerWrite, _Mapping]] = ...) -> None: ...

class PollStep(_message.Message):
    __slots__ = ("point_id", "until", "interval_ms", "timeout_ms")
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    UNTIL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_MS_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    until: Condition
    interval_ms: int
    timeout_ms: int
    def __init__(self, point_id: _Optional[str] = ..., until: _Optional[_Union[Condition, _Mapping]] = ..., interval_ms: _Optional[int] = ..., timeout_ms: _Optional[int] = ...) -> None: ...

class ReadStep(_message.Message):
    __slots__ = ("point_id", "into")
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    INTO_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    into: str
    def __init__(self, point_id: _Optional[str] = ..., into: _Optional[str] = ...) -> None: ...

class CommandStep(_message.Message):
    __slots__ = ("name", "write", "poll", "read")
    NAME_FIELD_NUMBER: _ClassVar[int]
    WRITE_FIELD_NUMBER: _ClassVar[int]
    POLL_FIELD_NUMBER: _ClassVar[int]
    READ_FIELD_NUMBER: _ClassVar[int]
    name: str
    write: WriteStep
    poll: PollStep
    read: ReadStep
    def __init__(self, name: _Optional[str] = ..., write: _Optional[_Union[WriteStep, _Mapping]] = ..., poll: _Optional[_Union[PollStep, _Mapping]] = ..., read: _Optional[_Union[ReadStep, _Mapping]] = ...) -> None: ...

class CommandParam(_message.Message):
    __slots__ = ("field", "storage_type", "value_type", "mapping", "required")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    STORAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAPPING_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    field: str
    storage_type: _types_pb2.StorageType
    value_type: _types_pb2.ValueType
    mapping: _mapping_pb2.Mapping
    required: bool
    def __init__(self, field: _Optional[str] = ..., storage_type: _Optional[_Union[_types_pb2.StorageType, str]] = ..., value_type: _Optional[_Union[_types_pb2.ValueType, _Mapping]] = ..., mapping: _Optional[_Union[_mapping_pb2.Mapping, _Mapping]] = ..., required: _Optional[bool] = ...) -> None: ...

class CommandResult(_message.Message):
    __slots__ = ("field", "value_type", "enum_ref")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENUM_REF_FIELD_NUMBER: _ClassVar[int]
    field: str
    value_type: _types_pb2.ValueType
    enum_ref: _types_pb2.EnumRef
    def __init__(self, field: _Optional[str] = ..., value_type: _Optional[_Union[_types_pb2.ValueType, _Mapping]] = ..., enum_ref: _Optional[_Union[_types_pb2.EnumRef, _Mapping]] = ..., **kwargs) -> None: ...

class Command(_message.Message):
    __slots__ = ("command_id", "command_ref", "name", "description", "params", "steps", "results")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_REF_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    command_ref: str
    name: str
    description: str
    params: _containers.RepeatedCompositeFieldContainer[CommandParam]
    steps: _containers.RepeatedCompositeFieldContainer[CommandStep]
    results: _containers.RepeatedCompositeFieldContainer[CommandResult]
    def __init__(self, command_id: _Optional[str] = ..., command_ref: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., params: _Optional[_Iterable[_Union[CommandParam, _Mapping]]] = ..., steps: _Optional[_Iterable[_Union[CommandStep, _Mapping]]] = ..., results: _Optional[_Iterable[_Union[CommandResult, _Mapping]]] = ...) -> None: ...
