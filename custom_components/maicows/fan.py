"""Fan platform for Maico WS integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MaicoCoordinator
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

# Supported fan speeds for the Maico WS320B based on official documentation
# 0=Off, 1=Humidity protection, 2=Reduced, 3=Nominal, 4=Intensive
SPEED_LIST = ["off", "humidity_protection", "reduced", "normal", "intensive"]

# Mapping from HA speeds to fan levels
SPEED_TO_LEVEL = {
    "off": 0,
    "humidity_protection": 1,
    "reduced": 2,
    "normal": 3,
    "intensive": 4,
}

LEVEL_TO_SPEED = {
    0: "off",
    1: "humidity_protection",
    2: "reduced",
    3: "normal",
    4: "intensive",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Maico WS320B fan platform."""
    coordinator: MaicoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([MaicoWS320BFan(coordinator)], update_before_add=True)


class MaicoWS320BFan(CoordinatorEntity[MaicoCoordinator], FanEntity):
    """Representation of a Maico WS320B VMC fan."""

    _attr_has_entity_name = True
    _attr_translation_key = "maico_fan"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the fan entity."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_fan"
        self._attr_device_info = coordinator.device_info
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.PRESET_MODE
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
        )
        self._attr_icon = "mdi:fan"

        # Define preset modes based on official documentation
        self._attr_preset_modes = [
            "off",
            "humidity_protection",
            "reduced",
            "normal",
            "intensive",
        ]

    @property
    def is_on(self) -> bool | None:
        """Return true if the entity is on."""
        # Check power state first
        power_state = self.coordinator.data.get("power_state")
        if power_state is not None and not power_state:
            return False

        # Also check ventilation level
        ventilation_level = self.coordinator.data.get("current_ventilation_level")
        return ventilation_level != 0

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        ventilation_level = self.coordinator.data.get("current_ventilation_level")
        if ventilation_level is None:
            return None

        if ventilation_level == 0:
            return 0
        if ventilation_level == 1:
            return 25
        if ventilation_level == 2:
            return 50
        if ventilation_level == 3:
            return 75
        if ventilation_level == 4:
            return 100
        return 50

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        ventilation_level = self.coordinator.data.get("current_ventilation_level")
        if ventilation_level is None:
            return None

        if ventilation_level == 0:
            return "off"
        if ventilation_level == 1:
            return "humidity_protection"
        if ventilation_level == 2:
            return "reduced"
        if ventilation_level == 3:
            return "normal"
        if ventilation_level == 4:
            return "intensive"
        return "normal"

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode (fan level) based on official documentation."""
        if preset_mode not in self._attr_preset_modes:
            msg = f"Unsupported preset mode: {preset_mode}"
            raise HomeAssistantError(msg)

        # Map preset mode to ventilation level based on official documentation
        level = 0
        if preset_mode == "off":
            level = 0
        elif preset_mode == "humidity_protection":
            level = 1
        elif preset_mode == "reduced":
            level = 2
        elif preset_mode == "normal":
            level = 3
        elif preset_mode == "intensive":
            level = 4
        else:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)
            return

        # Ensure the device is turned on when setting a level
        if level != 0 and not self.is_on:  # Only turn on if not setting to "off"
            power_success = await self._api.write_power_state(state=True)
            if not power_success:
                _LOGGER.error("Failed to turn on device before setting fan level")
                return

        # Set the fan level
        level_success = await self._api.write_ventilation_level(level)

        if level_success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set preset mode to %s", preset_mode)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage."""
        if percentage == 0:
            # Turn off the fan (level 0)
            success = await self._api.write_ventilation_level(0)
            if success:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to turn off the fan")
        else:
            # Turn on the device if it's off
            if not self.is_on:
                power_success = await self._api.write_power_state(state=True)
                if not power_success:
                    _LOGGER.error("Failed to turn on device before setting speed")
                    return

            # Map percentage to ventilation level based on official documentation
            level = 3  # Default normal
            if percentage <= 20:
                level = 1  # Humidity protection
            elif percentage <= 40:
                level = 2  # Reduced
            elif percentage <= 60:
                level = 3  # Nominal
            else:
                level = 4  # Intensive

            # Set the ventilation level
            level_success = await self._api.write_ventilation_level(level)

            if level_success:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to set fan speed to %d%%", percentage)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        # Turn on the device
        power_success = await self._api.write_power_state(state=True)
        if not power_success:
            _LOGGER.error("Failed to turn on the device")
            return

        # If a specific speed or preset is requested, set it
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
        elif percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            # Default to reduced level (2) if no specific level requested and currently off
            current_level = self.coordinator.data.get("current_ventilation_level", 0)
            if current_level == 0:
                level_success = await self._api.write_ventilation_level(2)
                if level_success:
                    await self.coordinator.async_request_refresh()
            else:
                await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        success = await self._api.write_power_state(state=False)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn off the fan")
