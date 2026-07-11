from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddressSpace(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ADDRESS_SPACE_UNSPECIFIED: _ClassVar[AddressSpace]
    COIL: _ClassVar[AddressSpace]
    DISCRETE_INPUT: _ClassVar[AddressSpace]
    INPUT_REGISTER: _ClassVar[AddressSpace]
    HOLDING_REGISTER: _ClassVar[AddressSpace]

class AccessMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCESS_MODE_UNSPECIFIED: _ClassVar[AccessMode]
    READ_ONLY: _ClassVar[AccessMode]
    WRITE_ONLY: _ClassVar[AccessMode]
    READ_WRITE: _ClassVar[AccessMode]
    COMMAND: _ClassVar[AccessMode]

class ByteOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BYTE_ORDER_UNSPECIFIED: _ClassVar[ByteOrder]
    BIG_ENDIAN: _ClassVar[ByteOrder]
    LITTLE_ENDIAN: _ClassVar[ByteOrder]

class WordOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORD_ORDER_UNSPECIFIED: _ClassVar[WordOrder]
    WORD_BIG_ENDIAN: _ClassVar[WordOrder]
    WORD_LITTLE_ENDIAN: _ClassVar[WordOrder]

class StorageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STORAGE_TYPE_UNSPECIFIED: _ClassVar[StorageType]
    BIT: _ClassVar[StorageType]
    U16: _ClassVar[StorageType]
    S16: _ClassVar[StorageType]
    U32: _ClassVar[StorageType]
    S32: _ClassVar[StorageType]
    U64: _ClassVar[StorageType]
    S64: _ClassVar[StorageType]
    IEEE754_F32: _ClassVar[StorageType]
    IEEE754_F64: _ClassVar[StorageType]
    STRING_ASCII: _ClassVar[StorageType]
    STRING_UTF8: _ClassVar[StorageType]
    BYTES_RAW: _ClassVar[StorageType]
    BCD: _ClassVar[StorageType]
    FIXED_POINT: _ClassVar[StorageType]
    COMPOSED: _ClassVar[StorageType]
    U24: _ClassVar[StorageType]
    U48: _ClassVar[StorageType]
    S48: _ClassVar[StorageType]

class PrimitiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRIMITIVE_TYPE_UNSPECIFIED: _ClassVar[PrimitiveType]
    BOOL: _ClassVar[PrimitiveType]
    INT32: _ClassVar[PrimitiveType]
    UINT32: _ClassVar[PrimitiveType]
    INT64: _ClassVar[PrimitiveType]
    UINT64: _ClassVar[PrimitiveType]
    FLOAT32: _ClassVar[PrimitiveType]
    FLOAT64: _ClassVar[PrimitiveType]
    DECIMAL: _ClassVar[PrimitiveType]
    STRING: _ClassVar[PrimitiveType]
    BYTES: _ClassVar[PrimitiveType]
    DATETIME: _ClassVar[PrimitiveType]
    FLAGS: _ClassVar[PrimitiveType]

class Transport(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSPORT_UNSPECIFIED: _ClassVar[Transport]
    MODBUS_RTU: _ClassVar[Transport]
    MODBUS_TCP: _ClassVar[Transport]
    MODBUS_ASCII: _ClassVar[Transport]
ADDRESS_SPACE_UNSPECIFIED: AddressSpace
COIL: AddressSpace
DISCRETE_INPUT: AddressSpace
INPUT_REGISTER: AddressSpace
HOLDING_REGISTER: AddressSpace
ACCESS_MODE_UNSPECIFIED: AccessMode
READ_ONLY: AccessMode
WRITE_ONLY: AccessMode
READ_WRITE: AccessMode
COMMAND: AccessMode
BYTE_ORDER_UNSPECIFIED: ByteOrder
BIG_ENDIAN: ByteOrder
LITTLE_ENDIAN: ByteOrder
WORD_ORDER_UNSPECIFIED: WordOrder
WORD_BIG_ENDIAN: WordOrder
WORD_LITTLE_ENDIAN: WordOrder
STORAGE_TYPE_UNSPECIFIED: StorageType
BIT: StorageType
U16: StorageType
S16: StorageType
U32: StorageType
S32: StorageType
U64: StorageType
S64: StorageType
IEEE754_F32: StorageType
IEEE754_F64: StorageType
STRING_ASCII: StorageType
STRING_UTF8: StorageType
BYTES_RAW: StorageType
BCD: StorageType
FIXED_POINT: StorageType
COMPOSED: StorageType
U24: StorageType
U48: StorageType
S48: StorageType
PRIMITIVE_TYPE_UNSPECIFIED: PrimitiveType
BOOL: PrimitiveType
INT32: PrimitiveType
UINT32: PrimitiveType
INT64: PrimitiveType
UINT64: PrimitiveType
FLOAT32: PrimitiveType
FLOAT64: PrimitiveType
DECIMAL: PrimitiveType
STRING: PrimitiveType
BYTES: PrimitiveType
DATETIME: PrimitiveType
FLAGS: PrimitiveType
TRANSPORT_UNSPECIFIED: Transport
MODBUS_RTU: Transport
MODBUS_TCP: Transport
MODBUS_ASCII: Transport

class Rational(_message.Message):
    __slots__ = ("numerator", "denominator")
    NUMERATOR_FIELD_NUMBER: _ClassVar[int]
    DENOMINATOR_FIELD_NUMBER: _ClassVar[int]
    numerator: int
    denominator: int
    def __init__(self, numerator: _Optional[int] = ..., denominator: _Optional[int] = ...) -> None: ...

class PointRef(_message.Message):
    __slots__ = ("point_id",)
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    def __init__(self, point_id: _Optional[str] = ...) -> None: ...

class ValueType(_message.Message):
    __slots__ = ("primitive", "enum_ref", "struct_ref", "array", "flags")
    PRIMITIVE_FIELD_NUMBER: _ClassVar[int]
    ENUM_REF_FIELD_NUMBER: _ClassVar[int]
    STRUCT_REF_FIELD_NUMBER: _ClassVar[int]
    ARRAY_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    primitive: PrimitiveType
    enum_ref: EnumRef
    struct_ref: StructRef
    array: ArrayType
    flags: FlagSet
    def __init__(self, primitive: _Optional[_Union[PrimitiveType, str]] = ..., enum_ref: _Optional[_Union[EnumRef, _Mapping]] = ..., struct_ref: _Optional[_Union[StructRef, _Mapping]] = ..., array: _Optional[_Union[ArrayType, _Mapping]] = ..., flags: _Optional[_Union[FlagSet, _Mapping]] = ...) -> None: ...

class EnumType(_message.Message):
    __slots__ = ("type_id", "name", "description", "values")
    TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    type_id: str
    name: str
    description: str
    values: _containers.RepeatedCompositeFieldContainer[EnumValue]
    def __init__(self, type_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., values: _Optional[_Iterable[_Union[EnumValue, _Mapping]]] = ...) -> None: ...

class EnumValue(_message.Message):
    __slots__ = ("value", "name", "description")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    value: int
    name: str
    description: str
    def __init__(self, value: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class StructType(_message.Message):
    __slots__ = ("type_id", "name", "description", "fields")
    TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    type_id: str
    name: str
    description: str
    fields: _containers.RepeatedCompositeFieldContainer[StructField]
    def __init__(self, type_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[StructField, _Mapping]]] = ...) -> None: ...

class StructField(_message.Message):
    __slots__ = ("field_id", "name", "value_type")
    FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    field_id: str
    name: str
    value_type: ValueType
    def __init__(self, field_id: _Optional[str] = ..., name: _Optional[str] = ..., value_type: _Optional[_Union[ValueType, _Mapping]] = ...) -> None: ...

class EnumRef(_message.Message):
    __slots__ = ("type_id",)
    TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    type_id: str
    def __init__(self, type_id: _Optional[str] = ...) -> None: ...

class StructRef(_message.Message):
    __slots__ = ("type_id",)
    TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    type_id: str
    def __init__(self, type_id: _Optional[str] = ...) -> None: ...

class ArrayType(_message.Message):
    __slots__ = ("element_type", "length", "count_ref")
    ELEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    COUNT_REF_FIELD_NUMBER: _ClassVar[int]
    element_type: ValueType
    length: int
    count_ref: PointRef
    def __init__(self, element_type: _Optional[_Union[ValueType, _Mapping]] = ..., length: _Optional[int] = ..., count_ref: _Optional[_Union[PointRef, _Mapping]] = ...) -> None: ...

class FlagSet(_message.Message):
    __slots__ = ("bits",)
    class BitsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: str
        def __init__(self, key: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...
    BITS_FIELD_NUMBER: _ClassVar[int]
    bits: _containers.ScalarMap[int, str]
    def __init__(self, bits: _Optional[_Mapping[int, str]] = ...) -> None: ...
