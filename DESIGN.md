# moddef-py — Python runtime + pymodbus adapter

Python implementation of the ModDef v0.4 runtime (spec §32), fourth after
Go/TS/Rust. Scope for v0.1: **runtime + pymodbus adapter + conformance** —
no typed-client generator (the upstream `moddef gen --lang python` catalog
generator already exists; a rich generator can follow the TS/Rust pattern
later).

## Goals

- Parse `.moddef.yaml` / `.moddef.json` / binary `.moddef` at runtime with
  protojson semantics (unknown fields and bad enum values rejected — same
  strictness as Go/TS/Rust; conformance-tested against `moddef/fixtures`).
- Codec in behavioral lockstep with go/codec ↔ moddef-ts ↔ moddef-rs:
  exact rational scaling, scale_ref (POW10/MULTIPLY), selector_ref cases
  with fallback, na_values sentinels, strings/BCD/flags/fields/datetime/
  composed values, §11.4-validated writes.
- Async `Device` facade (§32.4): point + measurand reads, SunSpec discovery
  with **ID-relative** model offsets (§7.3), constrained writes.
- pymodbus 3.x adapter: TCP + serial (RTU), chunked reads honoring
  `max_read_words` (default 125), per-request timeout, Modbus exceptions
  surfaced with the device's exception code.

## Shape

One distribution, `moddef`, with an optional extra for the adapter:

```
moddef-py/
  pyproject.toml            # dist "moddef"; extras: [pymodbus]
  src/moddef/
    v1/                     # vendored gen/python pb2 (+pyi) — proto package
                            # path == our package path, so imports just work
    schema.py               # friendly re-exports (ModDefDocument, enums, …)
    document.py             # detect_format / parse / serialize / load / save
    codec/                  # bytes.py, rat.py, decode.py, encode.py
    values.py               # Unavailable, decoded value types
    errors.py               # ModDefError hierarchy mirroring TS errors
    transport.py            # async Transport protocol
    device.py               # async Device facade
    measurand.py            # MeasurandQuery + matching
    resolve.py              # MODDEF_PACKAGE_ROOTS import resolution (§19)
    pymodbus.py             # adapter (imports pymodbus lazily; extra dep)
  scripts/sync-schema.sh    # copy moddef/gen/python → src/moddef/v1
  tests/                    # pytest + pytest-asyncio, mirrors TS/Rust suites
  .github/workflows/ci.yml  # fork-PR guard + read-only token (org convention)
```

## Decisions (defaults, flag if you disagree)

- **`fractions.Fraction` for exact rational math** — Python's arbitrary-
  precision ints make the i128/bigint machinery unnecessary; scaled values
  surface as `float` (parity with TS/Rust), `decode_point_raw` is the
  exactness escape hatch.
- **Async-only Device/Transport** (native asyncio; pymodbus 3.x is async).
  Transport is count-based (`read_holding(offset, count) -> list[int]`)
  like TS — Python has no fixed-buffer idiom worth forcing.
- **datetime points decode to `datetime` (UTC)**; epoch seconds/millis per
  the point's encoding (parity with TS `Date`).
- **Vendored pb2 under `src/moddef/v1/`** — the generated absolute imports
  (`from moddef.v1 import …`) resolve without patching. Same drift-check
  policy as moddef-ts: CI regenerates with **pinned** buf plugins and
  diffs; the python/pyi plugin pins go into moddef's buf.gen.yaml.
- protobuf runtime `>=7.35` (what the generated stubs validate against),
  PyYAML, pymodbus `>=3.13` (extra). Dev: pytest, pytest-asyncio.
- Python `>=3.11` (asyncio.timeout; StrEnum not needed); developed on
  3.14t, CI matrix 3.11–3.14.

## Milestones

1. Package skeleton + vendored schema + document layer; fixture
   equivalence (yaml == json == binary, lossless round-trips, binary
   byte-equality with goldens, invalid rejected, registry parses).
   ✅ **Done.** Binary byte-equality holds for **all** goldens — python
   protobuf emits explicit zero map keys like Go, so there is no
   prost-style exception here. One found-and-fixed hazard: PyYAML is
   YAML 1.1, where unquoted ON/OFF/YES/NO parse as booleans; a custom
   1.2-core loader keeps enum names like `OFF` (fronius_inverter_state)
   as strings, matching the Go/TS loaders.
2. Codec (decode + encode + constraints) with the shared vector suite.
   ✅ **Done** — `fractions.Fraction` internals, float surface.
3. Device facade + mock-transport tests (measurands, SunSpec, writes).
   ✅ **Done.**
4. pymodbus adapter + in-process server test; example script. ✅ **Done.**
   The server test uses the modern SimData/SimDevice API — the deprecated
   ModbusSequentialDataBlock compat layer is broken in pymodbus 3.13.
5. CI (org conventions: fork-PR guard, read-only token, sibling
   checkouts) + README; buf plugin pins upstream. ✅ **Done** —
   `protocolbuffers/python:v35.1` + `pyi:v35.1` pinned in moddef's
   buf.gen.yaml (pushed). 56 tests green on Python 3.14t locally;
   CI matrix 3.11–3.14.
