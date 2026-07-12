# SPDX-License-Identifier: Apache-2.0

"""Canonical Protobuf binary encoding (spec §33).

Protobuf's own ``SerializeToString(deterministic=True)`` is not portable
across runtimes. The C/upb backend orders map entries by descending key while
the pure-Python backend and the Go reference implementation order them by
ascending key. ModDef's canonical ``.moddef`` form requires ascending map
keys, so we encode the document ourselves.

The encoder reuses Protobuf's pure-Python scalar field encoders, which are
present regardless of the active backend and produce bytes identical to the Go
reference for scalars, packed repeated fields, and default omission. We take
control only of the two things the backend gets wrong or that need ordering
guarantees: map entries are emitted in ascending key order, and nested
messages recurse through this same routine.
"""

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.internal import encoder as _encoder
from google.protobuf.message import Message

_T = FieldDescriptor

# Protobuf field type -> pure-Python encoder factory. Message and group are
# handled directly (recursion), so they are absent here.
_SCALAR_ENCODERS = {
    _T.TYPE_DOUBLE: _encoder.DoubleEncoder,
    _T.TYPE_FLOAT: _encoder.FloatEncoder,
    _T.TYPE_INT64: _encoder.Int64Encoder,
    _T.TYPE_UINT64: _encoder.UInt64Encoder,
    _T.TYPE_INT32: _encoder.Int32Encoder,
    _T.TYPE_FIXED64: _encoder.Fixed64Encoder,
    _T.TYPE_FIXED32: _encoder.Fixed32Encoder,
    _T.TYPE_BOOL: _encoder.BoolEncoder,
    _T.TYPE_STRING: _encoder.StringEncoder,
    _T.TYPE_BYTES: _encoder.BytesEncoder,
    _T.TYPE_UINT32: _encoder.UInt32Encoder,
    _T.TYPE_ENUM: _encoder.EnumEncoder,
    _T.TYPE_SFIXED32: _encoder.SFixed32Encoder,
    _T.TYPE_SFIXED64: _encoder.SFixed64Encoder,
    _T.TYPE_SINT32: _encoder.SInt32Encoder,
    _T.TYPE_SINT64: _encoder.SInt64Encoder,
}


def _encode_scalar(out: bytearray, field: FieldDescriptor, value, *, repeated: bool) -> None:
    factory = _SCALAR_ENCODERS[field.type]
    encode = factory(field.number, repeated, field.is_packed if repeated else False)
    encode(out.extend, value, True)


def _encode_message_field(out: bytearray, field_number: int, body: bytes) -> None:
    # A length-delimited (wire type 2) field: tag, length, then the body.
    tag = _encoder.TagBytes(field_number, 2)
    out += tag
    out += _encoder._VarintBytes(len(body))
    out += body


def _encode_map(out: bytearray, field: FieldDescriptor, mapping) -> None:
    entry = field.message_type
    key_field = entry.fields_by_number[1]
    value_field = entry.fields_by_number[2]
    for key in sorted(mapping):
        body = bytearray()
        _encode_scalar(body, key_field, key, repeated=False)
        if value_field.type == FieldDescriptor.TYPE_MESSAGE:
            _encode_message_field(body, 2, canonical_bytes(mapping[key]))
        else:
            _encode_scalar(body, value_field, mapping[key], repeated=False)
        _encode_message_field(out, field.number, bytes(body))


def canonical_bytes(msg: Message) -> bytes:
    """Serialize ``msg`` to deterministic Protobuf bytes with ascending map keys."""
    out = bytearray()
    # ListFields() returns only set fields, already omitting proto3 defaults;
    # sort by field number for a stable, Go-matching field order.
    for field, value in sorted(msg.ListFields(), key=lambda fv: fv[0].number):
        if (
            field.type == FieldDescriptor.TYPE_MESSAGE
            and field.message_type.GetOptions().map_entry
        ):
            _encode_map(out, field, value)
        elif field.type == FieldDescriptor.TYPE_MESSAGE:
            if field.is_repeated:
                for item in value:
                    _encode_message_field(out, field.number, canonical_bytes(item))
            else:
                _encode_message_field(out, field.number, canonical_bytes(value))
        elif field.is_repeated:
            _encode_scalar(out, field, list(value), repeated=True)
        else:
            _encode_scalar(out, field, value, repeated=False)
    return bytes(out)
