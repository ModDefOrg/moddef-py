from moddef.v1 import types_pb2 as _types_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Direction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIRECTION_UNSPECIFIED: _ClassVar[Direction]
    DIRECTION_NONE: _ClassVar[Direction]
    IMPORT: _ClassVar[Direction]
    EXPORT: _ClassVar[Direction]
    NET: _ClassVar[Direction]
    CHARGE: _ClassVar[Direction]
    DISCHARGE: _ClassVar[Direction]
    FORWARD: _ClassVar[Direction]
    REVERSE: _ClassVar[Direction]

class PhaseRef(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PHASE_REF_UNSPECIFIED: _ClassVar[PhaseRef]
    PHASE_NONE: _ClassVar[PhaseRef]
    L1: _ClassVar[PhaseRef]
    L2: _ClassVar[PhaseRef]
    L3: _ClassVar[PhaseRef]
    N: _ClassVar[PhaseRef]
    L1_N: _ClassVar[PhaseRef]
    L2_N: _ClassVar[PhaseRef]
    L3_N: _ClassVar[PhaseRef]
    L1_L2: _ClassVar[PhaseRef]
    L2_L3: _ClassVar[PhaseRef]
    L3_L1: _ClassVar[PhaseRef]

class Aggregation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGGREGATION_UNSPECIFIED: _ClassVar[Aggregation]
    AGGREGATION_NONE: _ClassVar[Aggregation]
    TOTAL: _ClassVar[Aggregation]
    AVERAGE: _ClassVar[Aggregation]
    MINIMUM: _ClassVar[Aggregation]
    MAXIMUM: _ClassVar[Aggregation]
    INSTANTANEOUS: _ClassVar[Aggregation]

class MeasurementLocation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOCATION_UNSPECIFIED: _ClassVar[MeasurementLocation]
    GRID: _ClassVar[MeasurementLocation]
    LOAD: _ClassVar[MeasurementLocation]
    INLET: _ClassVar[MeasurementLocation]
    OUTLET: _ClassVar[MeasurementLocation]
    BATTERY: _ClassVar[MeasurementLocation]
    PV: _ClassVar[MeasurementLocation]
    INVERTER: _ClassVar[MeasurementLocation]
    EV: _ClassVar[MeasurementLocation]
    CABLE: _ClassVar[MeasurementLocation]
    BODY: _ClassVar[MeasurementLocation]
    INTERNAL: _ClassVar[MeasurementLocation]
    EXTERNAL: _ClassVar[MeasurementLocation]

class Accumulation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCUMULATION_UNSPECIFIED: _ClassVar[Accumulation]
    ACCUMULATION_INSTANTANEOUS: _ClassVar[Accumulation]
    REGISTER: _ClassVar[Accumulation]
    INTERVAL: _ClassVar[Accumulation]
    LIFETIME: _ClassVar[Accumulation]
    SESSION: _ClassVar[Accumulation]
    DAILY: _ClassVar[Accumulation]
    MONTHLY: _ClassVar[Accumulation]
DIRECTION_UNSPECIFIED: Direction
DIRECTION_NONE: Direction
IMPORT: Direction
EXPORT: Direction
NET: Direction
CHARGE: Direction
DISCHARGE: Direction
FORWARD: Direction
REVERSE: Direction
PHASE_REF_UNSPECIFIED: PhaseRef
PHASE_NONE: PhaseRef
L1: PhaseRef
L2: PhaseRef
L3: PhaseRef
N: PhaseRef
L1_N: PhaseRef
L2_N: PhaseRef
L3_N: PhaseRef
L1_L2: PhaseRef
L2_L3: PhaseRef
L3_L1: PhaseRef
AGGREGATION_UNSPECIFIED: Aggregation
AGGREGATION_NONE: Aggregation
TOTAL: Aggregation
AVERAGE: Aggregation
MINIMUM: Aggregation
MAXIMUM: Aggregation
INSTANTANEOUS: Aggregation
LOCATION_UNSPECIFIED: MeasurementLocation
GRID: MeasurementLocation
LOAD: MeasurementLocation
INLET: MeasurementLocation
OUTLET: MeasurementLocation
BATTERY: MeasurementLocation
PV: MeasurementLocation
INVERTER: MeasurementLocation
EV: MeasurementLocation
CABLE: MeasurementLocation
BODY: MeasurementLocation
INTERNAL: MeasurementLocation
EXTERNAL: MeasurementLocation
ACCUMULATION_UNSPECIFIED: Accumulation
ACCUMULATION_INSTANTANEOUS: Accumulation
REGISTER: Accumulation
INTERVAL: Accumulation
LIFETIME: Accumulation
SESSION: Accumulation
DAILY: Accumulation
MONTHLY: Accumulation

class MeasurandDefinition(_message.Message):
    __slots__ = ("measurand_id", "name", "description", "base_quantity", "direction", "phase_ref", "aggregation", "location", "accumulation", "canonical_unit", "expected_value_type")
    MEASURAND_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    BASE_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    PHASE_REF_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    ACCUMULATION_FIELD_NUMBER: _ClassVar[int]
    CANONICAL_UNIT_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    measurand_id: str
    name: str
    description: str
    base_quantity: str
    direction: Direction
    phase_ref: PhaseRef
    aggregation: Aggregation
    location: MeasurementLocation
    accumulation: Accumulation
    canonical_unit: str
    expected_value_type: _types_pb2.ValueType
    def __init__(self, measurand_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., base_quantity: _Optional[str] = ..., direction: _Optional[_Union[Direction, str]] = ..., phase_ref: _Optional[_Union[PhaseRef, str]] = ..., aggregation: _Optional[_Union[Aggregation, str]] = ..., location: _Optional[_Union[MeasurementLocation, str]] = ..., accumulation: _Optional[_Union[Accumulation, str]] = ..., canonical_unit: _Optional[str] = ..., expected_value_type: _Optional[_Union[_types_pb2.ValueType, _Mapping]] = ...) -> None: ...

class MeasurandRef(_message.Message):
    __slots__ = ("measurand_id", "base_quantity", "direction", "phase_ref", "aggregation", "location", "accumulation")
    MEASURAND_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    PHASE_REF_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    ACCUMULATION_FIELD_NUMBER: _ClassVar[int]
    measurand_id: str
    base_quantity: str
    direction: Direction
    phase_ref: PhaseRef
    aggregation: Aggregation
    location: MeasurementLocation
    accumulation: Accumulation
    def __init__(self, measurand_id: _Optional[str] = ..., base_quantity: _Optional[str] = ..., direction: _Optional[_Union[Direction, str]] = ..., phase_ref: _Optional[_Union[PhaseRef, str]] = ..., aggregation: _Optional[_Union[Aggregation, str]] = ..., location: _Optional[_Union[MeasurementLocation, str]] = ..., accumulation: _Optional[_Union[Accumulation, str]] = ...) -> None: ...

class MeasurandAlias(_message.Message):
    __slots__ = ("alias", "source", "maps_to")
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    MAPS_TO_FIELD_NUMBER: _ClassVar[int]
    alias: str
    source: str
    maps_to: MeasurandRef
    def __init__(self, alias: _Optional[str] = ..., source: _Optional[str] = ..., maps_to: _Optional[_Union[MeasurandRef, _Mapping]] = ...) -> None: ...
