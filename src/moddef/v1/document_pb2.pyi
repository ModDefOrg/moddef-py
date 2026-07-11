from moddef.v1 import device_pb2 as _device_pb2
from moddef.v1 import measurand_pb2 as _measurand_pb2
from moddef.v1 import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModDefDocument(_message.Message):
    __slots__ = ("doc_id", "name", "version", "imports", "enums", "structs", "measurands", "measurand_aliases", "devices")
    DOC_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    IMPORTS_FIELD_NUMBER: _ClassVar[int]
    ENUMS_FIELD_NUMBER: _ClassVar[int]
    STRUCTS_FIELD_NUMBER: _ClassVar[int]
    MEASURANDS_FIELD_NUMBER: _ClassVar[int]
    MEASURAND_ALIASES_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    doc_id: str
    name: str
    version: str
    imports: _containers.RepeatedCompositeFieldContainer[Import]
    enums: _containers.RepeatedCompositeFieldContainer[_types_pb2.EnumType]
    structs: _containers.RepeatedCompositeFieldContainer[_types_pb2.StructType]
    measurands: _containers.RepeatedCompositeFieldContainer[_measurand_pb2.MeasurandDefinition]
    measurand_aliases: _containers.RepeatedCompositeFieldContainer[_measurand_pb2.MeasurandAlias]
    devices: _containers.RepeatedCompositeFieldContainer[_device_pb2.DeviceProfile]
    def __init__(self, doc_id: _Optional[str] = ..., name: _Optional[str] = ..., version: _Optional[str] = ..., imports: _Optional[_Iterable[_Union[Import, _Mapping]]] = ..., enums: _Optional[_Iterable[_Union[_types_pb2.EnumType, _Mapping]]] = ..., structs: _Optional[_Iterable[_Union[_types_pb2.StructType, _Mapping]]] = ..., measurands: _Optional[_Iterable[_Union[_measurand_pb2.MeasurandDefinition, _Mapping]]] = ..., measurand_aliases: _Optional[_Iterable[_Union[_measurand_pb2.MeasurandAlias, _Mapping]]] = ..., devices: _Optional[_Iterable[_Union[_device_pb2.DeviceProfile, _Mapping]]] = ...) -> None: ...

class Import(_message.Message):
    __slots__ = ("uri", "alias", "checksum_sha256")
    URI_FIELD_NUMBER: _ClassVar[int]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_SHA256_FIELD_NUMBER: _ClassVar[int]
    uri: str
    alias: str
    checksum_sha256: str
    def __init__(self, uri: _Optional[str] = ..., alias: _Optional[str] = ..., checksum_sha256: _Optional[str] = ...) -> None: ...
