"""Diagnostics support for Maico WS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from . import MaicoCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: MaicoCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Get current data from coordinator
    data = coordinator.data or {}

    # Build diagnostics data
    return {
        "config_entry": {
            "title": entry.title,
            "version": entry.version,
        },
        "device_info": {
            "host": coordinator.api.host,
            "port": coordinator.api.port,
            "slave_id": coordinator.api.slave_id,
            "connected": coordinator.api.connected,
        },
        "current_status": {
            # Temperatures
            "supply_air_temperature": data.get("supply_air_temperature"),
            "extract_air_temperature": data.get("extract_air_temperature"),
            "room_temperature": data.get("room_temperature"),
            "inlet_air_temperature": data.get("inlet_air_temperature"),
            "exhaust_air_temperature": data.get("exhaust_air_temperature"),
            # Humidity
            "extract_air_humidity": data.get("extract_air_humidity"),
            # Fan speeds
            "supply_fan_speed": data.get("supply_fan_speed"),
            "extract_fan_speed": data.get("extract_fan_speed"),
            "supply_fan_state": data.get("supply_fan_state"),
            "extract_fan_state": data.get("extract_fan_state"),
            # Volume flows
            "current_supply_volume_flow": data.get("current_supply_volume_flow"),
            "current_extract_volume_flow": data.get("current_extract_volume_flow"),
            # Operation
            "operation_mode": data.get("operation_mode"),
            "current_ventilation_level": data.get("current_ventilation_level"),
            "season": data.get("season"),
            "power_state": data.get("power_state"),
            "bypass_status": data.get("bypass_status"),
            # Temperatures settings
            "target_temperature": data.get("target_temperature"),
            "supply_temp_min_cool": data.get("supply_temp_min_cool"),
            "room_temp_max": data.get("room_temp_max"),
            "room_temp_adjust": data.get("room_temp_adjust"),
            # Filters
            "filter_status": data.get("filter_status"),
            # Errors
            "fault_status": data.get("fault_status"),
            "info_messages": data.get("info_messages"),
        },
        "coordinator_info": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
        },
    }
