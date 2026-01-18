# Release v1.2.0: VOC & Quality

This release brings support for **VOC (Volatile Organic Compounds) sensors**, enabling better air quality monitoring. It also includes a major overhaul of the development infrastructure with **comprehensive unit tests**, **CI/CD workflows**, and **strict linting**, ensuring higher stability and code quality.

## 🚀 New Features

### 🌬️ Air Quality (VOC)
- **New Sensors:** Added 4 new VOC sensors (`voc_sensor_1` through `voc_sensor_4`) reading from registers 759-762.
- **Integration:** These sensors are now auto-discovered and available with proper unit definitions (ppm) and translations (EN, FR, DE).

### 🛠️ Developer Experience
- **Unit Tests:** Implemented a full suite of tests (API, Config Flow, Init) using `pytest`.
- **CI/CD:** Added GitHub Actions for automatic validation:
  - `hassfest`: Validates the integration against Home Assistant standards.
  - `hacs`: Validates compatibility with HACS.
- **Linting:** Enforced strict ruff linting rules to maintain code quality.

## 🐛 Fixes
- **Modbus Stability:** Fixed `ImportError` issues with newer `pymodbus` versions by removing deprecated `BinaryPayloadDecoder`.
- **Config Flow:** Fixed potential crash in configuration flow by properly handling `get_device_info`.
- **Translations:** Added missing translation keys for VOC sensors in all supported languages.

---

# Release v1.0.0: Initial Release

We are excited to announce the first stable release of the **Maico WS VMC Integration** for Home Assistant! This integration provides full control and monitoring for Maico WS (and compatible) ventilation systems via Modbus (TCP and RTU).

## 🌟 Key Features

### 🔌 Connectivity
- **Modbus TCP & RTU Support**: Flexible connection options for both network-connected and serial-connected devices.
- **Robust Connection Handling**: Automatic reconnection and error management.
- **UI Configuration**: Fully configurable via the Home Assistant integrations page (config flow).

### 🌡️ Climate & Control
- **Climate Entity**: Main control interface supporting:
  - **HVAC Modes**: Off, Fan Only (Manual/Auto).
  - **Fan Modes**: Auto (Humidity Protection), Low (Reduced), Medium (Normal), High (Intensive).
  - **Temperature Control**: Set target supply air temperature (registers `553` / `301`).
- **Fan Entity**: Granular control with:
  - **Speed Percentage**: 0-100% sliding scale mapped to 4 ventilation levels.
  - **Presets**: Humidity Protection, Reduced, Normal, Intensive.
- **Operation Modes**: Dedicated `select` entity for switching between:
  - Manual
  - Auto Time
  - Auto Sensor
  - Eco Supply / Eco Extract
- **Season Mode**: Switch between Winter and Summer modes manually.

### 📊 Monitoring & Sensors
- **Comprehensive Data**: Over 20 real-time sensors including:
  - **Temperatures**: Supply, Extract, Outdoor, Inlet, Exhaust, Room.
  - **Humidity**: Extract air humidity.
  - **Airflow**: Current volume flow (m³/h) and fan speeds (RPM).
  - **Calculated Efficiency**: Real-time Heat Recovery Efficiency (%) sensor.
- **Status Indicators**:
  - Bypass status (Open/Closed).
  - Power state.
  - Fault and Info message decoding.

### 🛠️ Maintenance & Configuration
- **Filter Management**: 
  - Trace remaining filter life (days) for Device, Outdoor, and Room filters.
  - **Reset Switches**: Momentary switches to easily reset filter timers after maintenance.
- **Advanced Settings**:
  - `number` entities to adjust "Max Room Temperature" and "Min Supply Temperature" limits.

## 📋 Changelog

### Added
- Initial codebase for `maicows` integration.
- Full `async` implementation using `pymodbus`.
- Platform support: `climate`, `fan`, `sensor`, `binary_sensor` (via sensors), `switch`, `number`, `select`.
- French and English translations.
- HACS compatibility (`hacs.json` and `manifest.json` compliance).

### Fixed
- Addressed private member access (`SLF001`) for future-proof Home Assistant compatibility.
- Optimized fan speed mapping logic.
- Resolved specific Icon translation keys for `hassfest` validation.

## 🚀 Installation

1. Install via HACS (Custom Repository) or copy `custom_components/maicows` to your `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration**.
4. Search for "Maico WS VMC".
5. Follow the configuration wizard to select TCP or RTU and enter your connection details.
