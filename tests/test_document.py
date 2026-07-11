"""Fixture conformance (spec §33): YAML / JSON / binary triples must parse
to equal documents and round-trip losslessly; binary serialization must
byte-match the checked-in goldens; schema-invalid documents must be
rejected; every blessed registry profile must parse. Mirrors the TS/Rust
conformance suites."""

import os

import pytest
import yaml

from moddef import ParseError, parse_document, serialize_document
from tests.helpers import DEVICES, FIXTURES


def load_manifest() -> dict:
    with open(os.path.join(FIXTURES, "manifest.yaml")) as f:
        return yaml.safe_load(f)


def read(rel: str) -> bytes:
    with open(os.path.join(FIXTURES, rel), "rb") as f:
        return f.read()


MANIFEST = load_manifest()
GOLDEN = MANIFEST["golden"]
INVALID = [i for i in MANIFEST["invalid"] if not i["schema_valid"]]

PROFILES = [
    "solar-inverter/growatt-sph/growatt-sph.moddef.yaml",
    "solar-inverter/fronius-gen24/fronius-gen24.moddef.yaml",
    "energy-meter/eastron-sdm630/eastron-sdm630.moddef.yaml",
    "energy-meter/abb-b23/abb-b23.moddef.yaml",
    "energy-meter/carlo-gavazzi-em24/carlo-gavazzi-em24.moddef.yaml",
    "battery-storage/victron-venus-os/victron-venus-os.moddef.yaml",
    "ev-charger/abb-terra-ac/abb-terra-ac.moddef.yaml",
    "hvac/daikin-altherma-3/daikin-altherma-3.moddef.yaml",
]


@pytest.mark.parametrize("g", GOLDEN, ids=lambda g: g["name"])
def test_golden_yaml_json_binary_equivalence(g):
    y = parse_document(read(g["files"]["yaml"]), "yaml")
    j = parse_document(read(g["files"]["json"]), "json")
    b = parse_document(read(g["files"]["binary"]), "binary")
    assert y == j
    assert y == b


@pytest.mark.parametrize("g", GOLDEN, ids=lambda g: g["name"])
def test_golden_lossless_round_trips(g):
    doc = parse_document(read(g["files"]["yaml"]), "yaml")
    for fmt in ("json", "yaml", "binary"):
        data = serialize_document(doc, fmt)
        assert parse_document(data if isinstance(data, bytes) else data.encode(), fmt) == doc
    # Binary equivalence with the checked-in .moddef bytes (deterministic
    # serialization; protobuf-python emits map entries like Go does).
    assert serialize_document(doc, "binary") == read(g["files"]["binary"])


@pytest.mark.parametrize("inv", INVALID, ids=lambda i: i["rule"])
def test_schema_invalid_fixtures_are_rejected(inv):
    with pytest.raises(ParseError):
        parse_document(read(inv["file"]), "json")


@pytest.mark.parametrize("rel", PROFILES)
def test_blessed_registry_profiles_parse(rel):
    with open(os.path.join(DEVICES, rel), "rb") as f:
        doc = parse_document(f.read(), "yaml")
    assert doc.doc_id
    assert len(doc.devices) > 0
    # JSON round-trip is lossless for real-world profiles too.
    data = serialize_document(doc, "json")
    assert parse_document(data.encode(), "json") == doc
