"""Shared test helpers: protojson-shaped Point construction (the same
shapes as the TS test helpers) and fixture paths."""

from __future__ import annotations

import os

from google.protobuf import json_format

from moddef import schema

HERE = os.path.dirname(__file__)
FIXTURES = os.path.join(HERE, "..", "..", "moddef", "fixtures")
DEVICES = os.path.join(HERE, "..", "..", "devices")


def point(**fields: object) -> schema.Point:
    return json_format.ParseDict(fields, schema.Point())
