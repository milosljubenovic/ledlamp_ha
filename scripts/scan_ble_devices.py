#!/usr/bin/env python3
"""
Scan for BLE devices and display their name and MAC address.
Useful for finding LEDDMX devices (e.g. LEDDMX-03-2E0E...).

Note: On macOS, CoreBluetooth does not expose real MAC addresses - it returns
UUIDs instead. The script tries to resolve MAC from the system Bluetooth cache
(for previously connected devices). For devices never connected, use a Linux
machine (e.g. Raspberry Pi) to get the actual MAC address.
"""

import asyncio
import plistlib
import sys
from pathlib import Path

try:
    from bleak import BleakScanner
except ImportError:
    print("Install bleak: pip install bleak")
    sys.exit(1)


def _load_uuid_to_mac_cache() -> dict[str, str]:
    """Load UUID -> MAC mapping from macOS Bluetooth plist cache."""
    cache: dict[str, str] = {}
    paths = [
        Path("/Library/Preferences/com.apple.Bluetooth.plist"),
        Path("/Library/Preferences/com.apple.bluetooth.plist"),
        *Path.home().joinpath("Library/Preferences/ByHost").glob(
            "com.apple.Bluetooth.*.plist"
        ),
    ]
    for path in paths:
        if not path.exists():
            continue
        try:
            with path.open("rb") as f:
                plist = plistlib.load(f)
        except (OSError, plistlib.InvalidFileException):
            continue
        cbcache = plist.get("CoreBluetoothCache")
        if not isinstance(cbcache, dict):
            continue
        for dev_uuid, devinfo in cbcache.items():
            if not isinstance(devinfo, dict):
                continue
            addr = devinfo.get("DeviceAddress")
            if addr:
                mac = addr.replace("-", ":").upper()
                cache[dev_uuid.upper()] = mac
                cache[dev_uuid.lower()] = mac
    return cache


async def scan(timeout: float = 10.0, name_filter: str | None = None) -> None:
    """Scan for BLE devices and print name + address."""
    uuid_to_mac = _load_uuid_to_mac_cache()
    if uuid_to_mac:
        print("(Resolved MAC addresses from Bluetooth cache where available)")
    else:
        print("(macOS: real MACs only available for previously connected devices)")
    print(f"Scanning for BLE devices (timeout: {timeout}s)...")
    if name_filter:
        print(f"Filtering by name prefix: {name_filter}")
    print("-" * 50)

    devices = await BleakScanner.discover(timeout=timeout)

    found = []
    for d in devices:
        name = d.name or "(unknown)"
        if name_filter and not name.startswith(name_filter):
            continue
        mac = uuid_to_mac.get(d.address)
        found.append((name, d.address, mac))

    if not found:
        print("No matching devices found.")
        return

    for name, address, mac in sorted(found, key=lambda x: x[0]):
        print(f"  {name}")
        if mac:
            print(f"    MAC: {mac}")
        print(f"    Address: {address}")

    if not uuid_to_mac and sys.platform == "darwin":
        print()
        print("Note: macOS does not expose BLE MAC addresses (privacy).")
        print("To get real MAC addresses for Home Assistant, run this script on Linux")
        print("(e.g. Raspberry Pi or the machine where HA runs).")


def main() -> None:
    # Usage: python scan_ble_devices.py [name_prefix] [timeout_seconds]
    # Examples:
    #   python scan_ble_devices.py                    # all devices, 10s
    #   python scan_ble_devices.py LEDDMX             # filter by prefix
    #   python scan_ble_devices.py LEDDMX-03-2E0E 15  # filter + 15s timeout
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

    asyncio.run(scan(timeout=timeout, name_filter=name_filter))


if __name__ == "__main__":
    main()
