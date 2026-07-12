# SPDX-License-Identifier: Apache-2.0

"""Document layer (spec §4): parse and serialize the three equivalent
encodings — `.moddef.yaml`, `.moddef.json`, binary `.moddef`. YAML and JSON
follow proto3 JSON (protojson) semantics; unknown fields and invalid enum
values are rejected, matching the Go/TS/Rust implementations and the
fixtures under moddef/fixtures/invalid.
"""

from __future__ import annotations

import json
import os
import re
from typing import Literal

import yaml
from google.protobuf import json_format

from moddef.canonical import canonical_bytes
from moddef.errors import ParseError
from moddef.schema import ModDefDocument

DocumentFormat = Literal["yaml", "json", "binary"]


class _Yaml12Loader(yaml.SafeLoader):
    """SafeLoader with YAML 1.2 core-schema booleans.

    PyYAML implements YAML 1.1, where unquoted ON/OFF/YES/NO parse as
    booleans — but the Go loader and the TS `yaml` package speak YAML 1.2,
    where only true/false are. Real profiles have enum members literally
    named OFF (e.g. fronius_inverter_state), so restrict the bool resolver.
    """


# Drop the 1.1 bool resolvers (y/n/yes/no/on/off/...), then register a
# 1.2-core one covering only true/false.
_Yaml12Loader.yaml_implicit_resolvers = {
    ch: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:bool"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
_Yaml12Loader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
    list("tTfF"),
)


def detect_format(path: str | os.PathLike[str]) -> DocumentFormat:
    """Infer the format from a file path per the spec §4 extensions."""
    p = os.fspath(path)
    if p.endswith((".moddef.yaml", ".moddef.yml")):
        return "yaml"
    if p.endswith(".moddef.json"):
        return "json"
    if p.endswith(".moddef"):
        return "binary"
    raise ParseError(f"cannot detect ModDef format from path: {p}")


def parse_document(data: bytes | str, format: DocumentFormat) -> ModDefDocument:
    """Parse a document from text or bytes in the given format."""
    try:
        if format == "binary":
            raw = data.encode() if isinstance(data, str) else data
            doc = ModDefDocument()
            doc.ParseFromString(raw)
            return doc
        text = data.decode() if isinstance(data, bytes) else data
        if format == "json":
            obj = json.loads(text)
        else:
            # YAML parses to plain JSON-shaped values, then through protojson
            # (the same round-trip the Go loader uses). Numeric mapping keys
            # (int64-keyed maps) become strings, as JSON requires.
            obj = _yaml_to_json(yaml.load(text, Loader=_Yaml12Loader))
            if obj is None:
                obj = {}
        return json_format.ParseDict(obj, ModDefDocument())
    except ParseError:
        raise
    except Exception as e:  # json/yaml/protobuf errors → one ParseError type
        raise ParseError(f"failed to parse ModDef {format} document: {e}") from e


def serialize_document(doc: ModDefDocument, format: DocumentFormat) -> bytes | str:
    """Serialize a document. yaml/json return str, binary returns bytes.

    Binary serialization is deterministic (ascending map keys), matching the
    Go-produced golden `.moddef` files byte for byte. It goes through
    `canonical_bytes` rather than `SerializeToString(deterministic=True)`
    because the protobuf C/upb backend orders map entries by descending key,
    which would not match the canonical form.
    """
    if format == "binary":
        return canonical_bytes(doc)
    obj = json_format.MessageToDict(doc)
    if format == "json":
        return json.dumps(obj, indent=2) + "\n"
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)


def load(path: str | os.PathLike[str]) -> ModDefDocument:
    """Load and parse a `.moddef.yaml` / `.moddef.json` / `.moddef` file."""
    format = detect_format(path)
    with open(path, "rb") as f:
        return parse_document(f.read(), format)


def save(doc: ModDefDocument, path: str | os.PathLike[str]) -> None:
    """Serialize and write a document; the format comes from the extension."""
    data = serialize_document(doc, detect_format(path))
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(path, mode) as f:
        f.write(data)


def _yaml_to_json(v: object) -> object:
    """YAML value → JSON-shaped value: stringify non-string mapping keys
    (YAML allows numeric/bool keys; protojson int64-keyed maps want strings).
    """
    if isinstance(v, dict):
        out: dict[str, object] = {}
        for k, val in v.items():
            if isinstance(k, bool):
                key = "true" if k else "false"
            elif isinstance(k, (int, float, str)):
                key = str(k)
            else:
                raise ParseError(f"unsupported yaml mapping key: {k!r}")
            out[key] = _yaml_to_json(val)
        return out
    if isinstance(v, list):
        return [_yaml_to_json(x) for x in v]
    return v
