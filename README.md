# Maico WS VMC Integration

[![GitHub Release](https://img.shields.io/github/release/isaya07/ha-maicows.svg?style=flat-square)](https://github.com/isaya07/ha-maicows/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)
[![Validate with hassfest](https://github.com/isaya07/ha-maicows/actions/workflows/hassfest.yml/badge.svg)](https://github.com/isaya07/ha-maicows/actions/workflows/hassfest.yml)
[![Validate with HACS](https://github.com/isaya07/ha-maicows/actions/workflows/hacs.yml/badge.svg)](https://github.com/isaya07/ha-maicows/actions/workflows/hacs.yml)

Integration for Maico WS VMC ventilation systems for Home Assistant.

This integration communicates with Maico ventilation units via Modbus TCP (or potentially RTU, depending on configuration).

## Features

- **Fan**: Control ventilation speed/levels.
- **Climate**: Control core climate parameters (if supported).
- **Sensors**: Read various statuses from the device (temperatures, air quality, etc.).
- **Switches**: Toggle specific functions.
- **Select**: Choose operation modes.
- **Number**: Adjust numeric parameters.

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed.
2. Go to **HACS** > **Integrations**.
3. Click the three dots (top right) > **Custom repositories**.
4. Add the URL of this repository: `https://github.com/isaya07/ha-maicows`
5. Select category **Integration**.
6. Click **Add**.
7. Close the dialog, find **Maico WS VMC** in the list, and install it.
8. Restart Home Assistant.

[![Ouvre votre instance Home Assistant et ajoute un dépôt dans la boutique communautaire Home Assistant.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=isaya07&repository=ha-maicows&category=integration)

### Manual

1. Download the latest release.
2. Copy the `custom_components/maicows` folder to your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Maico WS VMC**.
4. Follow the on-screen instructions to configure the connection (IP address, port, etc.).

> [!IMPORTANT]
> **RLS 1 WR Remote Control**: If you are using an RLS 1 WR remote control, make sure it is configured in **Auxiliary mode**. Otherwise, Modbus settings will be limited and some features will not be accessible.

## Development

For developers who want to contribute or modify this integration, please see [DEVELOPMENT.md](DEVELOPMENT.md).

***


