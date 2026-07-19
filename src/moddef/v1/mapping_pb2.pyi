from moddef.v1 import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ComposedKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMPOSED_KIND_UNSPECIFIED: _ClassVar[ComposedKind]
    MANTISSA_EXPONENT: _ClassVar[ComposedKind]

class WriteBehavior(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WRITE_BEHAVIOR_UNSPECIFIED: _ClassVar[WriteBehavior]
    DIRECT: _ClassVar[WriteBehavior]
    MOMENTARY: _ClassVar[WriteBehavior]
    LATCH: _ClassVar[WriteBehavior]
    MASKED: _ClassVar[WriteBehavior]
    COMMAND_TRIGGER: _ClassVar[WriteBehavior]

class Charset(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHARSET_UNSPECIFIED: _ClassVar[Charset]
    ASCII: _ClassVar[Charset]
    UTF8: _ClassVar[Charset]

class Padding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PADDING_UNSPECIFIED: _ClassVar[Padding]
    PADDING_NULL: _ClassVar[Padding]
    PADDING_SPACE: _ClassVar[Padding]
    PADDING_NONE: _ClassVar[Padding]

class Termination(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TERMINATION_UNSPECIFIED: _ClassVar[Termination]
    FIXED_LENGTH: _ClassVar[Termination]
    NULL_TERMINATED: _ClassVar[Termination]

class ScaleMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCALE_MODE_UNSPECIFIED: _ClassVar[ScaleMode]
    POW10: _ClassVar[ScaleMode]
    MULTIPLY: _ClassVar[ScaleMode]

class DateTimeEncoding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATETIME_ENCODING_UNSPECIFIED: _ClassVar[DateTimeEncoding]
    EPOCH_S: _ClassVar[DateTimeEncoding]
    EPOCH_MS: _ClassVar[DateTimeEncoding]
    PACKED_BCD_DATETIME: _ClassVar[DateTimeEncoding]
    SPLIT_FIELDS: _ClassVar[DateTimeEncoding]
COMPOSED_KIND_UNSPECIFIED: ComposedKind
MANTISSA_EXPONENT: ComposedKind
WRITE_BEHAVIOR_UNSPECIFIED: WriteBehavior
DIRECT: WriteBehavior
MOMENTARY: WriteBehavior
LATCH: WriteBehavior
MASKED: WriteBehavior
COMMAND_TRIGGER: WriteBehavior
CHARSET_UNSPECIFIED: Charset
ASCII: Charset
UTF8: Charset
PADDING_UNSPECIFIED: Padding
PADDING_NULL: Padding
PADDING_SPACE: Padding
PADDING_NONE: Padding
TERMINATION_UNSPECIFIED: Termination
FIXED_LENGTH: Termination
NULL_TERMINATED: Termination
SCALE_MODE_UNSPECIFIED: ScaleMode
POW10: ScaleMode
MULTIPLY: ScaleMode
DATETIME_ENCODING_UNSPECIFIED: DateTimeEncoding
EPOCH_S: DateTimeEncoding
EPOCH_MS: DateTimeEncoding
PACKED_BCD_DATETIME: DateTimeEncoding
SPLIT_FIELDS: DateTimeEncoding

class Mapping(_message.Message):
    __slots__ = ("space", "offset", "length_words", "bit_index", "byte_order", "word_order", "sign_magnitude", "stride_words", "model_relative_offset", "composed", "allowed_function_codes", "string_encoding", "storage_type", "bit_offset", "bit_length")
    SPACE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LENGTH_WORDS_FIELD_NUMBER: _ClassVar[int]
    BIT_INDEX_FIELD_NUMBER: _ClassVar[int]
    BYTE_ORDER_FIELD_NUMBER: _ClassVar[int]
    WORD_ORDER_FIELD_NUMBER: _ClassVar[int]
    SIGN_MAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    STRIDE_WORDS_FIELD_NUMBER: _ClassVar[int]
    MODEL_RELATIVE_OFFSET_FIELD_NUMBER: _ClassVar[int]
    COMPOSED_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_FUNCTION_CODES_FIELD_NUMBER: _ClassVar[int]
    STRING_ENCODING_FIELD_NUMBER: _ClassVar[int]
    STORAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    BIT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    BIT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    space: _types_pb2.AddressSpace
    offset: int
    length_words: int
    bit_index: int
    byte_order: _types_pb2.ByteOrder
    word_order: _types_pb2.WordOrder
    sign_magnitude: bool
    stride_words: int
    model_relative_offset: int
    composed: ComposedMapping
    allowed_function_codes: _containers.RepeatedScalarFieldContainer[int]
    string_encoding: StringEncoding
    storage_type: _types_pb2.StorageType
    bit_offset: int
    bit_length: int
    def __init__(self, space: _Optional[_Union[_types_pb2.AddressSpace, str]] = ..., offset: _Optional[int] = ..., length_words: _Optional[int] = ..., bit_index: _Optional[int] = ..., byte_order: _Optional[_Union[_types_pb2.ByteOrder, str]] = ..., word_order: _Optional[_Union[_types_pb2.WordOrder, str]] = ..., sign_magnitude: _Optional[bool] = ..., stride_words: _Optional[int] = ..., model_relative_offset: _Optional[int] = ..., composed: _Optional[_Union[ComposedMapping, _Mapping]] = ..., allowed_function_codes: _Optional[_Iterable[int]] = ..., string_encoding: _Optional[_Union[StringEncoding, _Mapping]] = ..., storage_type: _Optional[_Union[_types_pb2.StorageType, str]] = ..., bit_offset: _Optional[int] = ..., bit_length: _Optional[int] = ...) -> None: ...

class ComposedMapping(_message.Message):
    __slots__ = ("mantissa", "exponent", "base", "kind")
    MANTISSA_FIELD_NUMBER: _ClassVar[int]
    EXPONENT_FIELD_NUMBER: _ClassVar[int]
    BASE_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    mantissa: Mapping
    exponent: Mapping
    base: int
    kind: ComposedKind
    def __init__(self, mantissa: _Optional[_Union[Mapping, _Mapping]] = ..., exponent: _Optional[_Union[Mapping, _Mapping]] = ..., base: _Optional[int] = ..., kind: _Optional[_Union[ComposedKind, str]] = ...) -> None: ...

class Transform(_message.Message):
    __slots__ = ("scale", "offset", "clamp", "scale_ref")
    SCALE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    CLAMP_FIELD_NUMBER: _ClassVar[int]
    SCALE_REF_FIELD_NUMBER: _ClassVar[int]
    scale: _types_pb2.Rational
    offset: _types_pb2.Rational
    clamp: Clamp
    scale_ref: ScaleRef
    def __init__(self, scale: _Optional[_Union[_types_pb2.Rational, _Mapping]] = ..., offset: _Optional[_Union[_types_pb2.Rational, _Mapping]] = ..., clamp: _Optional[_Union[Clamp, _Mapping]] = ..., scale_ref: _Optional[_Union[ScaleRef, _Mapping]] = ...) -> None: ...

class Clamp(_message.Message):
    __slots__ = ("enabled", "min_value", "max_value")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    min_value: float
    max_value: float
    def __init__(self, enabled: _Optional[bool] = ..., min_value: _Optional[float] = ..., max_value: _Optional[float] = ...) -> None: ...

class BitField(_message.Message):
    __slots__ = ("field_id", "name", "bit_offset", "bit_length", "value_type")
    FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BIT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    BIT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    field_id: str
    name: str
    bit_offset: int
    bit_length: int
    value_type: _types_pb2.ValueType
    def __init__(self, field_id: _Optional[str] = ..., name: _Optional[str] = ..., bit_offset: _Optional[int] = ..., bit_length: _Optional[int] = ..., value_type: _Optional[_Union[_types_pb2.ValueType, _Mapping]] = ...) -> None: ...

class RegisterField(_message.Message):
    __slots__ = ("field_id", "name", "bit_offset", "bit_length", "value_type", "storage_type", "transform", "unit", "enum_ref")
    FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BIT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    BIT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    ENUM_REF_FIELD_NUMBER: _ClassVar[int]
    field_id: str
    name: str
    bit_offset: int
    bit_length: int
    value_type: _types_pb2.ValueType
    storage_type: _types_pb2.StorageType
    transform: Transform
    unit: str
    enum_ref: _types_pb2.EnumRef
    def __init__(self, field_id: _Optional[str] = ..., name: _Optional[str] = ..., bit_offset: _Optional[int] = ..., bit_length: _Optional[int] = ..., value_type: _Optional[_Union[_types_pb2.ValueType, _Mapping]] = ..., storage_type: _Optional[_Union[_types_pb2.StorageType, str]] = ..., transform: _Optional[_Union[Transform, _Mapping]] = ..., unit: _Optional[str] = ..., enum_ref: _Optional[_Union[_types_pb2.EnumRef, _Mapping]] = ...) -> None: ...

class NaValue(_message.Message):
    __slots__ = ("raw", "meaning")
    RAW_FIELD_NUMBER: _ClassVar[int]
    MEANING_FIELD_NUMBER: _ClassVar[int]
    raw: int
    meaning: str
    def __init__(self, raw: _Optional[int] = ..., meaning: _Optional[str] = ...) -> None: ...

class ScaleRef(_message.Message):
    __slots__ = ("point_id", "mode", "denominator")
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    DENOMINATOR_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    mode: ScaleMode
    denominator: int
    def __init__(self, point_id: _Optional[str] = ..., mode: _Optional[_Union[ScaleMode, str]] = ..., denominator: _Optional[int] = ...) -> None: ...

class SelectorRef(_message.Message):
    __slots__ = ("point_id", "cases")
    class CasesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: SelectorCase
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[SelectorCase, _Mapping]] = ...) -> None: ...
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    CASES_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    cases: _containers.MessageMap[int, SelectorCase]
    def __init__(self, point_id: _Optional[str] = ..., cases: _Optional[_Mapping[int, SelectorCase]] = ...) -> None: ...

class SelectorCase(_message.Message):
    __slots__ = ("scale", "offset", "unit")
    SCALE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    scale: _types_pb2.Rational
    offset: _types_pb2.Rational
    unit: str
    def __init__(self, scale: _Optional[_Union[_types_pb2.Rational, _Mapping]] = ..., offset: _Optional[_Union[_types_pb2.Rational, _Mapping]] = ..., unit: _Optional[str] = ...) -> None: ...

class StringEncoding(_message.Message):
    __slots__ = ("charset", "padding", "termination")
    CHARSET_FIELD_NUMBER: _ClassVar[int]
    PADDING_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_FIELD_NUMBER: _ClassVar[int]
    charset: Charset
    padding: Padding
    termination: Termination
    def __init__(self, charset: _Optional[_Union[Charset, str]] = ..., padding: _Optional[_Union[Padding, str]] = ..., termination: _Optional[_Union[Termination, str]] = ...) -> None: ...

class DateTimeSpec(_message.Message):
    __slots__ = ("encoding", "width")
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    encoding: DateTimeEncoding
    width: _types_pb2.StorageType
    def __init__(self, encoding: _Optional[_Union[DateTimeEncoding, str]] = ..., width: _Optional[_Union[_types_pb2.StorageType, str]] = ...) -> None: ...

class WriteEncoding(_message.Message):
    __slots__ = ("storage_type", "transform", "prefix_high_byte")
    STORAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    PREFIX_HIGH_BYTE_FIELD_NUMBER: _ClassVar[int]
    storage_type: _types_pb2.StorageType
    transform: Transform
    prefix_high_byte: int
    def __init__(self, storage_type: _Optional[_Union[_types_pb2.StorageType, str]] = ..., transform: _Optional[_Union[Transform, _Mapping]] = ..., prefix_high_byte: _Optional[int] = ...) -> None: ...

class WriteSemantics(_message.Message):
    __slots__ = ("behavior", "confirmation_point", "requires_enable_point", "constraints")
    BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    CONFIRMATION_POINT_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_ENABLE_POINT_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    behavior: WriteBehavior
    confirmation_point: str
    requires_enable_point: str
    constraints: WriteConstraints
    def __init__(self, behavior: _Optional[_Union[WriteBehavior, str]] = ..., confirmation_point: _Optional[str] = ..., requires_enable_point: _Optional[str] = ..., constraints: _Optional[_Union[WriteConstraints, _Mapping]] = ...) -> None: ...

class WriteConstraints(_message.Message):
    __slots__ = ("min_value", "max_value", "step", "allowed_values", "cooldown_ms", "safety_note")
    MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_VALUES_FIELD_NUMBER: _ClassVar[int]
    COOLDOWN_MS_FIELD_NUMBER: _ClassVar[int]
    SAFETY_NOTE_FIELD_NUMBER: _ClassVar[int]
    min_value: _types_pb2.Rational
    max_value: _types_pb2.Rational
    step: _types_pb2.Rational
    allowed_values: _containers.RepeatedScalarFieldContainer[int]
    cooldown_ms: int
    safety_note: str
    def __init__(self, min_value: _Optional[_Union[_types_pb2.Rational, _Mapping]] = ..., max_value: _Optional[_Union[_types_pb2.Rational, _Mapping]] = ..., step: _Optional[_Union[_types_pb2.Rational, _Mapping]] = ..., allowed_values: _Optional[_Iterable[int]] = ..., cooldown_ms: _Optional[int] = ..., safety_note: _Optional[str] = ...) -> None: ...
