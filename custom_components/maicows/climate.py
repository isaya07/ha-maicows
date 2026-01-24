"""Climate platform for Maico WS integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MaicoCoordinator
from .const import (
    ATTR_EXTRACT_AIR_TEMP,
    ATTR_OUTDOOR_AIR_TEMP,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

# Supported HVAC modes - OFF and FAN_ONLY for VMC
SUPPORTED_HVAC_MODES = [HVACMode.OFF, HVACMode.FAN_ONLY]

# Supported fan modes using standard HA constants for proper icon support
# Mapping: 0=off, 1=auto (humidity), 2=low (reduced), 3=medium (normal),
# 4=high (intensive)
FAN_MODES = ["off", "auto", "low", "medium", "high"]

# Internal mapping from VMC level to fan mode
VENTILATION_TO_FAN_MODE = {
    0: "off",
    1: "auto",  # Humidity protection -> auto
    2: "low",  # Reduced -> low
    3: "medium",  # Normal -> medium
    4: "high",  # Intensive -> high
}

# Reverse mapping from fan mode to VMC level
FAN_MODE_TO_VENTILATION = {v: k for k, v in VENTILATION_TO_FAN_MODE.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Maico WS320B climate platform."""
    coordinator: MaicoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([MaicoWS320BClimate(coordinator)], update_before_add=True)


class MaicoWS320BClimate(CoordinatorEntity[MaicoCoordinator], ClimateEntity):
    """Representation of a Maico WS320B VMC climate entity."""

    _attr_has_entity_name = True
    _attr_translation_key = "maico_climate"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_climate"
        self._attr_device_info = coordinator.device_info
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
        )
        self._attr_hvac_modes = SUPPORTED_HVAC_MODES
        self._attr_fan_modes = FAN_MODES
        self._attr_min_temp = 18  # Minimum temperature in Celsius (Maico limit)
        self._attr_max_temp = 25  # Maximum temperature in Celsius (Maico limit)
        self._attr_target_temperature_step = 0.5

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get("room_temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get("target_temperature")

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation mode."""
        # Check if VMC is off based on operation mode
        operation_mode = self.coordinator.data.get("operation_mode")
        if operation_mode == "off":
            return HVACMode.OFF
        return HVACMode.FAN_ONLY

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting using standard HA modes."""
        ventilation_level = self.coordinator.data.get("current_ventilation_level")
        return VENTILATION_TO_FAN_MODE.get(ventilation_level)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode not in self._attr_hvac_modes:
            msg = f"Unsupported HVAC mode: {hvac_mode}"
            raise HomeAssistantError(msg)

        if hvac_mode == HVACMode.OFF:
            # Turn off VMC by setting operation mode to 0 (Off)
            success = await self._api.set_operation_mode(0)
        elif hvac_mode == HVACMode.FAN_ONLY:
            # Turn on VMC by setting operation mode to 1 (Manual)
            success = await self._api.set_operation_mode(1)
        else:
            _LOGGER.error("Invalid HVAC mode: %s", hvac_mode)
            return

        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set HVAC mode to %s", hvac_mode)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        if fan_mode not in self._attr_fan_modes:
            msg = f"Unsupported fan mode: {fan_mode}"
            raise HomeAssistantError(msg)

        # Map standard HA fan mode to VMC ventilation level
        level = FAN_MODE_TO_VENTILATION.get(fan_mode, 3)

        success = await self._api.set_ventilation_level(level)

        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set fan mode to %s", fan_mode)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            temperature = kwargs[ATTR_TEMPERATURE]

            # Validate temperature range
            # Validate temperature range
            if temperature < self._attr_min_temp or temperature > self._attr_max_temp:
                msg = (
                    f"Temperature {temperature} outside range "
                    f"{self._attr_min_temp}-{self._attr_max_temp}"
                )
                raise HomeAssistantError(msg)

            # Set target room temperature using register 553
            success = await self._api.set_target_room_temperature(temperature)

            if success:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to set target temperature to %s", temperature)

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running HVAC action based on operation mode."""
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        # For VMC, we'll return FAN as it's primarily a ventilation system
        return HVACAction.FAN

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        status = self.coordinator.data
        if not status:
            return {}

        attributes = {}

        # Add other temperature readings as attributes
        if status.get("extract_air_temperature") is not None:
            attributes[ATTR_EXTRACT_AIR_TEMP] = status["extract_air_temperature"]
        if status.get("outdoor_air_temperature") is not None:
            attributes[ATTR_OUTDOOR_AIR_TEMP] = status["outdoor_air_temperature"]

        # Add fan speeds
        if status.get("supply_fan_speed") is not None:
            attributes["supply_fan_speed_rpm"] = status["supply_fan_speed"]
        if status.get("extract_fan_speed") is not None:
            attributes["extract_fan_speed_rpm"] = status["extract_fan_speed"]

        # Add filter status
        if status.get("filter_status") is not None:
            attributes["filter_status"] = status["filter_status"]

        # Add operation mode
        if status.get("operation_mode") is not None:
            attributes["operation_mode_raw"] = status["operation_mode"]

        # Add fault and info status
        if status.get("fault_status") is not None:
            attributes["fault_status"] = status["fault_status"]
        if status.get("info_messages") is not None:
            attributes["info_messages"] = status["info_messages"]

        # Add season
        if status.get("season") is not None:
            attributes["season"] = status["season"]

        return attributes
