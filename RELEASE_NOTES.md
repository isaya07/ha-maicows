# Release v1.4.1: Bug Fixes

This release fixes critical bugs discovered after the v1.4.0 refactoring.

## 🐛 Bug Fixes

### Write Operations Not Working
- **Fixed:** Number entities were not sending values to the VMC due to an empty `write_register` stub method in `ControlsMixin` that was shadowing the real implementation in `MaicoWSClient`.

### Missing Write Methods
- **Fixed:** Added missing methods `write_supply_temp_min_cool()` and `write_room_temp_max()` that were not migrated during refactoring.

### VOC Sensor Warning
- **Fixed:** Removed incompatible `device_class: VOLATILE_ORGANIC_COMPOUNDS` from VOC sensors. The ppm unit is not compatible with this device class (requires μg/m³).

## 🚀 New Entity

### Room Temperature Adjustment
- **New:** `number.room_temp_adjust` (register 300) - Correction température ambiante (-3°C to +3°C)

## 🎨 UI Improvements
- Changed `room_temp_bus` icon from bus vehicle to thermometer (`mdi:thermometer-lines`)

---

# Release v1.4.0: Refactoring & External Sensors

This release brings a **major code refactoring** and **external sensor support**, enabling integration with external temperature, humidity, and air quality sensors via Modbus.

## 🚀 New Features

### 🌡️ External Sensor Support
New Number entities to write external sensor values to the VMC:
- **Room Temperature External** (register 701): Write external room temperature
- **Room Temperature Bus** (register 707): Write bus room temperature
- **Humidity Bus** (register 763): Write bus humidity (0-100%)
- **Air Quality Bus** (register 764): Write bus CO2/air quality (0-5000 ppm)

### 🎛️ Room Temperature Sensor Selection
New Select entity (`select.room_temp_selection`) to choose temperature source:
- Comfort BDE (remote control)
- External sensor
- Internal sensor
- Bus (Modbus input)

## 🔧 Technical Improvements

### Code Refactoring
Refactored `maico_ws_api.py` (1533 lines) into modular package structure:
- `maico_ws/registers.py` - Register constants
- `maico_ws/client.py` - Modbus connection logic
- `maico_ws/sensors.py` - Sensor reading methods
- `maico_ws/controls.py` - Control/write methods
- `maico_ws/status.py` - Status aggregation

### Translations
- Added German, French, and English translations for all new entities.

---

# Release v1.3.0: Stability & Compatibility

This release focuses on **stability fixes** and **improved compatibility** with Home Assistant 2025.11+.

## 🐛 Bug Fixes

### Config Flow
- **Fixed:** Fresh installations now work correctly. Simplified connection validation to only verify TCP connectivity (previously required additional Modbus register reads that could fail).

### Missing Entities
- **Fixed:** Restored `Platform.SELECT` to platforms list - Operation Mode and Season entities are now properly created.

### Modbus Connection
- **Fixed:** Removed `name` parameter from `AsyncModbusTcpClient` which could cause connection issues with some pymodbus versions.

## 📋 Compatibility
- Updated minimum Home Assistant version to **2025.11.3**.
- All 11 unit tests passing.

---

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
