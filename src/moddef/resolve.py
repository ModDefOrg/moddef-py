# SPDX-License-Identifier: Apache-2.0

"""Import resolution (spec §19). Import URIs follow the package form
`moddef:<namespace>:<name>:<version>` (e.g. `moddef:stdlib:measurands:1.0.0`),
resolved against package roots as
`<root>/<name>/<version>/<name>.moddef.{yaml,json,binary}` — the layout of
moddef/stdlib and the Go resolver's MODDEF_PACKAGE_ROOTS."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol

from moddef import schema
from moddef.document import DocumentFormat, parse_document
from moddef.errors import ParseError


class PackageResolver(Protocol):
    def fetch(self, uri: str) -> tuple[bytes, DocumentFormat]: ...


class DirResolver:
    """Resolver over MODDEF_PACKAGE_ROOTS-style directories."""

    def __init__(self, roots: list[str] | None = None) -> None:
        if roots is None:
            roots = [r for r in os.environ.get("MODDEF_PACKAGE_ROOTS", "").split(":") if r]
        self.roots = roots

    def fetch(self, uri: str) -> tuple[bytes, DocumentFormat]:
        parts = uri.split(":")
        if len(parts) != 4 or parts[0] != "moddef":
            raise ParseError(f"unsupported import uri: {uri}")
        _, _, name, version = parts
        candidates: list[tuple[str, DocumentFormat]] = [
            (f"{name}.moddef.yaml", "yaml"),
            (f"{name}.moddef.json", "json"),
            (f"{name}.moddef", "binary"),
        ]
        for root in self.roots:
            for fname, fmt in candidates:
                path = os.path.join(root, name, version, fname)
                try:
                    with open(path, "rb") as f:
                        return f.read(), fmt
                except OSError:
                    continue
        raise ParseError(f"import not found under package roots: {uri}")


@dataclass
class ResolvedDocument:
    """A document's visible symbol tables after import resolution: local
    symbols first, then imported ones (alias-prefixed as `<alias>:<id>`,
    never overriding an existing entry)."""

    doc: schema.ModDefDocument
    enums: dict[str, schema.EnumType] = field(default_factory=dict)
    measurands: dict[str, schema.MeasurandDefinition] = field(default_factory=dict)
    imports: dict[str, schema.ModDefDocument] = field(default_factory=dict)


def resolve_imports(
    doc: schema.ModDefDocument,
    resolver: PackageResolver | None = None,
) -> ResolvedDocument:
    """Resolve a document's imports and build the visible symbol tables."""
    out = ResolvedDocument(doc=doc)
    for e in doc.enums:
        out.enums[e.type_id] = e
    for m in doc.measurands:
        out.measurands[m.measurand_id] = m

    for imp in doc.imports:
        if resolver is None:
            raise ParseError(f"document imports {imp.uri} but no resolver was supplied")
        data, fmt = resolver.fetch(imp.uri)
        idoc = parse_document(data, fmt)
        out.imports[imp.uri] = idoc
        prefix = f"{imp.alias}:" if imp.alias else ""
        for e in idoc.enums:
            out.enums.setdefault(prefix + e.type_id, e)
        for m in idoc.measurands:
            out.measurands.setdefault(prefix + m.measurand_id, m)
    return out
