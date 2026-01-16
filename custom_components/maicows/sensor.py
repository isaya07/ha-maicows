"""Sensor platform for Maico WS integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MaicoCoordinator
from .const import (
    ATTR_EXTRACT_AIR_TEMP,
    ATTR_OUTDOOR_AIR_TEMP,
    ATTR_SUPPLY_AIR_HUMIDITY,
    ATTR_SUPPLY_AIR_TEMP,
    ATTR_SUPPLY_FAN_SPEED,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

# Sensor types to be created
SENSOR_TYPES = [
    {
        "key": "supply_air_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
        "attr_name": ATTR_SUPPLY_AIR_TEMP,
        "icon": "mdi:thermometer",
    },
    {
        "key": "extract_air_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
        "attr_name": ATTR_EXTRACT_AIR_TEMP,
        "icon": "mdi:thermometer",
    },
    {
        "key": "outdoor_air_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
        "attr_name": ATTR_OUTDOOR_AIR_TEMP,
        "icon": "mdi:thermometer",
    },
    {
        "key": "extract_air_humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": PERCENTAGE,
        "attr_name": ATTR_SUPPLY_AIR_HUMIDITY,
        "icon": "mdi:water-percent",
    },
    {
        "key": "supply_fan_speed",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": "RPM",
        "attr_name": ATTR_SUPPLY_FAN_SPEED,
        "icon": "mdi:fan",
    },
    {
        "key": "extract_fan_speed",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": "RPM",
        "attr_name": "extract_fan_speed",
        "icon": "mdi:fan",
    },
    {
        "key": "current_supply_volume_flow",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": "m³/h",
        "attr_name": "current_supply_volume_flow",
        "icon": "mdi:weather-windy",
    },
    {
        "key": "current_extract_volume_flow",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": "m³/h",
        "attr_name": "current_extract_volume_flow",
        "icon": "mdi:weather-windy",
    },
    {
        "key": "current_ventilation_level",
        "device_class": None,
        "unit_of_measurement": None,
        "attr_name": "current_ventilation_level",
        "icon": "mdi:fan-speed-1",
    },
    {
        "key": "filter_device_days",
        "device_class": SensorDeviceClass.DURATION,
        "unit_of_measurement": "d",
        "attr_name": "filter_device_days",
        "icon": "mdi:air-filter",
    },
    {
        "key": "filter_outdoor_days",
        "device_class": SensorDeviceClass.DURATION,
        "unit_of_measurement": "d",
        "attr_name": "filter_outdoor_days",
        "icon": "mdi:air-filter",
    },
    {
        "key": "filter_room_days",
        "device_class": SensorDeviceClass.DURATION,
        "unit_of_measurement": "d",
        "attr_name": "filter_room_days",
        "icon": "mdi:air-filter",
    },
    {
        "key": "room_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
        "attr_name": "room_temperature",
        "icon": "mdi:thermometer",
    },
    {
        "key": "inlet_air_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
        "attr_name": "inlet_air_temperature",
        "icon": "mdi:thermometer",
    },
    {
        "key": "exhaust_air_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
        "attr_name": "exhaust_air_temperature",
        "icon": "mdi:thermometer",
    },
    {
        "key": "supply_fan_state",
        "device_class": None,
        "unit_of_measurement": None,
        "attr_name": "supply_fan_state",
        "icon": "mdi:fan",
    },
    {
        "key": "extract_fan_state",
        "device_class": None,
        "unit_of_measurement": None,
        "attr_name": "extract_fan_state",
        "icon": "mdi:fan",
    },
    {
        "key": "season",
        "device_class": None,
        "unit_of_measurement": None,
        "attr_name": "season",
        "icon": "mdi:snowflake",
    },
    {
        "key": "operation_mode",
        "device_class": None,
        "unit_of_measurement": None,
        "attr_name": "operation_mode",
        "icon": "mdi:cog",
    },
    {
        "key": "fault_status",
        "device_class": None,
        "unit_of_measurement": None,
        "attr_name": "fault_status",
        "icon": "mdi:alert-circle",
    },
    {
        "key": "info_messages",
        "device_class": None,
        "unit_of_measurement": None,
        "attr_name": "info_messages",
        "icon": "mdi:information",
    },
    {
        "key": "bypass_status",
        "device_class": None,
        "unit_of_measurement": None,
        "attr_name": "bypass_status",
        "icon": "mdi:valve",
    },
    {
        "key": "heat_recovery_efficiency",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": PERCENTAGE,
        "attr_name": "heat_recovery_efficiency",
        "icon": "mdi:percent",
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Maico WS320B sensor platform."""
    coordinator: MaicoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        MaicoWS320BSensor(
            coordinator=coordinator,
            key=sensor_type["key"],
            device_class=sensor_type["device_class"],
            unit_of_measurement=sensor_type["unit_of_measurement"],
            attr_name=sensor_type["attr_name"],
            icon=sensor_type.get("icon"),
        )
        for sensor_type in SENSOR_TYPES
    ]

    async_add_entities(sensors)


class MaicoWS320BSensor(CoordinatorEntity[MaicoCoordinator], SensorEntity):
    """Representation of a Maico WS320B sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MaicoCoordinator,
        key: str,
        device_class: SensorDeviceClass | None,
        unit_of_measurement: str | None,
        attr_name: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{coordinator.api.host}_{coordinator.api.port}_{key}"
        self._attr_device_info = coordinator.device_info
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement

        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        status = self.coordinator.data
        if not status:
            return None

        # Special handling for individual filter sensors
        if self._key in (
            "filter_device_days",
            "filter_outdoor_days",
            "filter_room_days",
        ):
            filter_status = status.get("filter_status")
            if filter_status and isinstance(filter_status, dict):
                return filter_status.get(self._key)
            return None

        # Special handling for info messages (simplify display)
        if self._key == "info_messages":
            info_msg = status.get("info_messages")
            if info_msg == "no_info":
                return "none"
            if info_msg and info_msg.startswith("info_hi_"):
                # Extract just the low word value for simpler display
                parts = info_msg.split("_")
                if len(parts) >= 4:
                    lo_value = parts[3]
                    if lo_value == "0":
                        return "none"
                    return f"info_{lo_value}"
            return info_msg

        # Special handling for boolean states
        if self._key in ("supply_fan_state", "extract_fan_state"):
            return "on" if status.get(self._key) else "off"

        if self._key == "bypass_status":
            return "open" if status.get(self._key) else "closed"

        # Calculate heat recovery efficiency
        if self._key == "heat_recovery_efficiency":
            try:
                # Get temperatures from coordinator data
                # Note: inlet_air_temperature is the outdoor/fresh air temperature (BEFORE heat recovery)
                # supply_air_temperature is the air after heat recovery
                # extract_air_temperature is the air extracted from the house
                t_supply = status.get("supply_air_temperature")
                t_extract = status.get("extract_air_temperature")
                t_inlet = status.get("inlet_air_temperature")

                # Debug logging
                _LOGGER.debug(
                    "Heat recovery calculation - Supply: %s, Extract: %s, Inlet: %s",
                    t_supply,
                    t_extract,
                    t_inlet,
                )

                # All temperatures must be available
                if t_supply is None or t_extract is None or t_inlet is None:
                    _LOGGER.debug("Heat recovery: Missing temperature data")
                    return None

                # Avoid division by zero
                denominator = t_extract - t_inlet
                if abs(denominator) < 0.1:  # Temperature difference too small
                    _LOGGER.debug(
                        "Heat recovery: Temperature difference too small (%s)",
                        denominator,
                    )
                    return None

                # Calculate efficiency: (T_supply - T_inlet) / (T_extract - T_inlet) * 100
                efficiency = ((t_supply - t_inlet) / denominator) * 100

                # Clamp to reasonable range (0-100%)
                efficiency = max(0, min(100, efficiency))

                _LOGGER.debug("Heat recovery efficiency calculated: %s%%", efficiency)
                return round(efficiency, 1)
            except (TypeError, ValueError, ZeroDivisionError):
                _LOGGER.exception("Heat recovery calculation error")
                return None

        # Direct lookup for all other sensors
        return status.get(self._key)
