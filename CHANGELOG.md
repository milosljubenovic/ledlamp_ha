# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-02-05

### Added

- BLE device autodiscovery with active scan
- Manual MAC entry option
- Support for all LEDDMX devices (generic prefix match, no hardcoded models)

### Changed

- No connection during config flow or setup (connects only when using the light)
- Fallback BLEDevice when device not in Bluetooth cache
- Downgraded unexpected disconnect logs from warning to debug

### Fixed

- "Unable to connect" during setup when device not in range
- "NoneType has no attribute hex" for unsupported device models
- BlueZ "Failed to cancel connection" during disconnect

## [0.0.1] - Initial release

- Basic LEDDMX BLE support
- On/Off, RGB, brightness, effects
