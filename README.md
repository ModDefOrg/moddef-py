# moddef-py

Python runtime for [ModDef](https://github.com/ModDefOrg/moddef) (spec
v0.4) — declarative Modbus device definitions — plus a pymodbus adapter.

- **Document layer**: parse/serialize `.moddef.yaml`, `.moddef.json`, and
  binary `.moddef` with protojson semantics (unknown fields rejected;
  byte-identical binary output).
- **Codec**: exact rational scaling (`fractions.Fraction`), SunSpec scale
  factors (`scale_ref`), selector cases, sentinels, strings, BCD, flags,
  packed fields, composed values — in behavioral lockstep with the Go, TS,
  and Rust implementations (shared conformance vectors).
- **Async `Device` facade**: point and measurand reads, SunSpec discovery
  (ID-relative model offsets, §7.3), §11.4-validated writes.
- **pymodbus adapter** (`moddef[pymodbus]`): TCP + RTU, chunked reads
  honoring `max_read_words`, per-request timeouts, Modbus exceptions
  surfaced with the device's exception code.

```sh
pip install moddef[pymodbus]
```

```python
import asyncio
from moddef import Device, MeasurandQuery, load
from moddef.pymodbus import Options, PymodbusTransport

async def main():
    doc = load("growatt-sph.moddef.yaml")
    transport = await PymodbusTransport.tcp("192.168.1.50", options=Options())
    dev = Device.create(doc, None, transport)

    soc = await dev.read_point("state_of_charge")
    hz = await dev.read_measurand(MeasurandQuery("frequency"))
    await dev.write_point("ac_charge_enable", 1)   # §11.4 constraints validated
    print(soc, hz)

asyncio.run(main())
```

## Development

```sh
python -m venv .venv && .venv/bin/pip install -e . --group dev
.venv/bin/python -m pytest
```

Conformance tests need sibling checkouts of
[moddef](https://github.com/ModDefOrg/moddef) (fixtures) and
[devices](https://github.com/ModDefOrg/devices) (blessed registry). The
generated protobuf modules under `src/moddef/v1/` are vendored from
`moddef/gen/python` (`scripts/sync-schema.sh`) and drift-checked in CI
against the pinned buf plugins.

## License of generated output

Code generated from a ModDef document (for example by `moddef gen`) is not a
derivative work of the ModDef tooling or runtime. You may license the generated
output under any terms you choose. The runtime it imports (this package, `moddef`) is
Apache-2.0 licensed; see the LICENSE file for its terms, which apply only to the
runtime, not to your generated code.

## License

Apache-2.0. See [LICENSE](LICENSE), [NOTICE](NOTICE), and
[CONTRIBUTING.md](CONTRIBUTING.md).
