from moddef.v1 import mapping_pb2 as _mapping_pb2
from moddef.v1 import measurand_pb2 as _measurand_pb2
from moddef.v1 import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DiscoveryKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISCOVERY_KIND_UNSPECIFIED: _ClassVar[DiscoveryKind]
    SUNSPEC: _ClassVar[DiscoveryKind]
DISCOVERY_KIND_UNSPECIFIED: DiscoveryKind
SUNSPEC: DiscoveryKind

class Discovery(_message.Message):
    __slots__ = ("kind", "anchor_candidates", "model_id")
    KIND_FIELD_NUMBER: _ClassVar[int]
    ANCHOR_CANDIDATES_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    kind: DiscoveryKind
    anchor_candidates: _containers.RepeatedScalarFieldContainer[int]
    model_id: int
    def __init__(self, kind: _Optional[_Union[DiscoveryKind, str]] = ..., anchor_candidates: _Optional[_Iterable[int]] = ..., model_id: _Optional[int] = ...) -> None: ...

class Availability(_message.Message):
    __slots__ = ("point_id", "equals")
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    EQUALS_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    equals: int
    def __init__(self, point_id: _Optional[str] = ..., equals: _Optional[int] = ...) -> None: ...

class DeviceProfile(_message.Message):
    __slots__ = ("device_id", "vendor", "model", "family", "description", "supported_transports", "default_unit_id", "firmware_versions", "blocks", "variants")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    FAMILY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_TRANSPORTS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    BLOCKS_FIELD_NUMBER: _ClassVar[int]
    VARIANTS_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    vendor: str
    model: str
    family: str
    description: str
    supported_transports: _containers.RepeatedScalarFieldContainer[_types_pb2.Transport]
    default_unit_id: int
    firmware_versions: _containers.RepeatedScalarFieldContainer[str]
    blocks: _containers.RepeatedCompositeFieldContainer[RegisterBlock]
    variants: _containers.RepeatedCompositeFieldContainer[DeviceVariant]
    def __init__(self, device_id: _Optional[str] = ..., vendor: _Optional[str] = ..., model: _Optional[str] = ..., family: _Optional[str] = ..., description: _Optional[str] = ..., supported_transports: _Optional[_Iterable[_Union[_types_pb2.Transport, str]]] = ..., default_unit_id: _Optional[int] = ..., firmware_versions: _Optional[_Iterable[str]] = ..., blocks: _Optional[_Iterable[_Union[RegisterBlock, _Mapping]]] = ..., variants: _Optional[_Iterable[_Union[DeviceVariant, _Mapping]]] = ...) -> None: ...

class DeviceVariant(_message.Message):
    __slots__ = ("variant_id", "name", "base_device_id", "overrides", "additions", "removals")
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BASE_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    OVERRIDES_FIELD_NUMBER: _ClassVar[int]
    ADDITIONS_FIELD_NUMBER: _ClassVar[int]
    REMOVALS_FIELD_NUMBER: _ClassVar[int]
    variant_id: str
    name: str
    base_device_id: str
    overrides: _containers.RepeatedCompositeFieldContainer[PointOverride]
    additions: _containers.RepeatedCompositeFieldContainer[Point]
    removals: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, variant_id: _Optional[str] = ..., name: _Optional[str] = ..., base_device_id: _Optional[str] = ..., overrides: _Optional[_Iterable[_Union[PointOverride, _Mapping]]] = ..., additions: _Optional[_Iterable[_Union[Point, _Mapping]]] = ..., removals: _Optional[_Iterable[str]] = ...) -> None: ...

class PointOverride(_message.Message):
    __slots__ = ("point_id", "replacement")
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    REPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    replacement: Point
    def __init__(self, point_id: _Optional[str] = ..., replacement: _Optional[_Union[Point, _Mapping]] = ...) -> None: ...

class RegisterBlock(_message.Message):
    __slots__ = ("block_id", "name", "space", "start_offset", "length_words", "overlay", "discovery", "points")
    BLOCK_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SPACE_FIELD_NUMBER: _ClassVar[int]
    START_OFFSET_FIELD_NUMBER: _ClassVar[int]
    LENGTH_WORDS_FIELD_NUMBER: _ClassVar[int]
    OVERLAY_FIELD_NUMBER: _ClassVar[int]
    DISCOVERY_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    block_id: str
    name: str
    space: _types_pb2.AddressSpace
    start_offset: int
    length_words: int
    overlay: bool
    discovery: Discovery
    points: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, block_id: _Optional[str] = ..., name: _Optional[str] = ..., space: _Optional[_Union[_types_pb2.AddressSpace, str]] = ..., start_offset: _Optional[int] = ..., length_words: _Optional[int] = ..., overlay: _Optional[bool] = ..., discovery: _Optional[_Union[Discovery, _Mapping]] = ..., points: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ("point_id", "name", "description", "access", "storage_type", "value_type", "mapping", "transform", "unit", "display_precision", "measurand", "bit_fields", "fields", "na_values", "datetime", "write_encoding", "available_if", "selector_ref", "recommended_poll_period_ms", "write")
    POINT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    STORAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAPPING_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PRECISION_FIELD_NUMBER: _ClassVar[int]
    MEASURAND_FIELD_NUMBER: _ClassVar[int]
    BIT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    NA_VALUES_FIELD_NUMBER: _ClassVar[int]
    DATETIME_FIELD_NUMBER: _ClassVar[int]
    WRITE_ENCODING_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_IF_FIELD_NUMBER: _ClassVar[int]
    SELECTOR_REF_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDED_POLL_PERIOD_MS_FIELD_NUMBER: _ClassVar[int]
    WRITE_FIELD_NUMBER: _ClassVar[int]
    point_id: str
    name: str
    description: str
    access: _types_pb2.AccessMode
    storage_type: _types_pb2.StorageType
    value_type: _types_pb2.ValueType
    mapping: _mapping_pb2.Mapping
    transform: _mapping_pb2.Transform
    unit: str
    display_precision: int
    measurand: _measurand_pb2.MeasurandRef
    bit_fields: _containers.RepeatedCompositeFieldContainer[_mapping_pb2.BitField]
    fields: _containers.RepeatedCompositeFieldContainer[_mapping_pb2.RegisterField]
    na_values: _containers.RepeatedCompositeFieldContainer[_mapping_pb2.NaValue]
    datetime: _mapping_pb2.DateTimeSpec
    write_encoding: _mapping_pb2.WriteEncoding
    available_if: Availability
    selector_ref: _mapping_pb2.SelectorRef
    recommended_poll_period_ms: int
    write: _mapping_pb2.WriteSemantics
    def __init__(self, point_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., access: _Optional[_Union[_types_pb2.AccessMode, str]] = ..., storage_type: _Optional[_Union[_types_pb2.StorageType, str]] = ..., value_type: _Optional[_Union[_types_pb2.ValueType, _Mapping]] = ..., mapping: _Optional[_Union[_mapping_pb2.Mapping, _Mapping]] = ..., transform: _Optional[_Union[_mapping_pb2.Transform, _Mapping]] = ..., unit: _Optional[str] = ..., display_precision: _Optional[int] = ..., measurand: _Optional[_Union[_measurand_pb2.MeasurandRef, _Mapping]] = ..., bit_fields: _Optional[_Iterable[_Union[_mapping_pb2.BitField, _Mapping]]] = ..., fields: _Optional[_Iterable[_Union[_mapping_pb2.RegisterField, _Mapping]]] = ..., na_values: _Optional[_Iterable[_Union[_mapping_pb2.NaValue, _Mapping]]] = ..., datetime: _Optional[_Union[_mapping_pb2.DateTimeSpec, _Mapping]] = ..., write_encoding: _Optional[_Union[_mapping_pb2.WriteEncoding, _Mapping]] = ..., available_if: _Optional[_Union[Availability, _Mapping]] = ..., selector_ref: _Optional[_Union[_mapping_pb2.SelectorRef, _Mapping]] = ..., recommended_poll_period_ms: _Optional[int] = ..., write: _Optional[_Union[_mapping_pb2.WriteSemantics, _Mapping]] = ...) -> None: ...
