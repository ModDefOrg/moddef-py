# SPDX-License-Identifier: Apache-2.0

"""ModDef runtime for Python (spec v0.4): parse declarative Modbus device
definitions, decode/encode points exactly, and drive devices asynchronously.

Quick start::

    import asyncio
    from moddef import Device, MeasurandQuery, load
    from moddef.pymodbus import Options, PymodbusTransport   # extra: moddef[pymodbus]

    async def main():
        doc = load("growatt-sph.moddef.yaml")
        transport = await PymodbusTransport.tcp("192.168.1.50", options=Options())
        dev = Device.create(doc, None, transport)
        print(await dev.read_point("state_of_charge"))
        print(await dev.read_measurand(MeasurandQuery("frequency")))

    asyncio.run(main())
"""

from moddef import schema
from moddef.codec import (
    decode_all,
    decode_point,
    decode_point_raw,
    encode_point,
    point_words,
    resolve_context,
)
from moddef.device import Device, validate_constraints
from moddef.document import (
    DocumentFormat,
    detect_format,
    load,
    parse_document,
    save,
    serialize_document,
)
from moddef.errors import (
    AmbiguousMeasurandError,
    DecodeError,
    DeviceNotFoundError,
    EncodeError,
    MeasurandNotSupportedError,
    ModDefError,
    ParseError,
    PointNotFoundError,
    UnsupportedMappingError,
    WriteAccessError,
    WriteConstraintError,
)
from moddef.measurand import MeasurandQuery, measurand_matches
from moddef.resolve import DirResolver, ResolvedDocument, resolve_imports
from moddef.transport import Transport
from moddef.values import DecodedValue, Unavailable

__all__ = [
    "AmbiguousMeasurandError",
    "DecodeError",
    "DecodedValue",
    "Device",
    "DeviceNotFoundError",
    "DirResolver",
    "DocumentFormat",
    "EncodeError",
    "MeasurandNotSupportedError",
    "MeasurandQuery",
    "ModDefError",
    "ParseError",
    "PointNotFoundError",
    "ResolvedDocument",
    "Transport",
    "Unavailable",
    "UnsupportedMappingError",
    "WriteAccessError",
    "WriteConstraintError",
    "decode_all",
    "decode_point",
    "decode_point_raw",
    "detect_format",
    "encode_point",
    "load",
    "measurand_matches",
    "parse_document",
    "point_words",
    "resolve_context",
    "resolve_imports",
    "save",
    "schema",
    "serialize_document",
    "validate_constraints",
]
