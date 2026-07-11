"""Read live values from a Growatt SPH (or any ModDef-described device)
over Modbus TCP using the runtime-parsed document — no codegen involved.

    python examples/growatt_tcp.py 192.168.1.50 \
        ../devices/solar-inverter/growatt-sph/growatt-sph.moddef.yaml \
        inverter_status pv1_voltage output_power
"""

import asyncio
import sys

from moddef import Device, load
from moddef.pymodbus import Options, PymodbusTransport


async def main() -> None:
    if len(sys.argv) < 3:
        print("usage: growatt_tcp.py <host[:port]> <profile.moddef.yaml> [point_id...]")
        raise SystemExit(2)
    host, _, port = sys.argv[1].partition(":")
    doc = load(sys.argv[2])
    ids = sys.argv[3:]

    transport = await PymodbusTransport.tcp(host, int(port or 502), Options())
    dev = Device.create(doc, None, transport)
    if not ids:
        ids = [p.point_id for p in dev.points()[:8]]
    for point_id in ids:
        try:
            print(f"{point_id} = {await dev.read_point(point_id)!r}")
        except Exception as e:  # noqa: BLE001 — demo script
            print(f"{point_id}: error: {e}")
    transport.close()


if __name__ == "__main__":
    asyncio.run(main())
