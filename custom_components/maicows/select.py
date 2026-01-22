"""Select platform for Maico WS integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MaicoCoordinator
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

# Operation modes based on Maico documentation
# 0=Off, 1=Manual, 2=Auto-Time, 3=Auto-Sensor, 4=Eco-Supply, 5=Eco-Extract
OPERATION_MODES = [
    "off",
    "manual",
    "auto_time",
    "auto_sensor",
    "eco_supply",
    "eco_extract",
]

MODE_TO_VALUE = {
    "off": 0,
    "manual": 1,
    "auto_time": 2,
    "auto_sensor": 3,
    "eco_supply": 4,
    "eco_extract": 5,
}

# Season modes: 0=Winter, 1=Summer
SEASON_MODES = ["winter", "summer"]

SEASON_TO_VALUE = {
    "winter": 0,
    "summer": 1,
}

# Room temperature sensor selection: 0=Comfort-BDE, 1=External, 2=Internal, 3=Bus
ROOM_TEMP_SELECTION_MODES = [
    "comfort_bde",
    "external",
    "internal",
    "bus",
]

ROOM_TEMP_SEL_TO_VALUE = {
    "comfort_bde": 0,
    "external": 1,
    "internal": 2,
    "bus": 3,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Maico WS320B select platform."""
    coordinator: MaicoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            MaicoOperationModeSelect(coordinator),
            MaicoSeasonSelect(coordinator),
            MaicoRoomTempSelectionSelect(coordinator),
        ]
    )


class MaicoOperationModeSelect(CoordinatorEntity[MaicoCoordinator], SelectEntity):
    """Representation of Maico WS320B operation mode select."""

    _attr_has_entity_name = True
    _attr_translation_key = "operation_mode"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = (
            f"{self._api.host}_{self._api.port}_operation_mode_select"
        )
        self._attr_device_info = coordinator.device_info
        self._attr_options = OPERATION_MODES
        self._attr_icon = "mdi:cog"

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self.coordinator.data.get("operation_mode")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in OPERATION_MODES:
            _LOGGER.error("Invalid operation mode: %s", option)
            return

        mode_value = MODE_TO_VALUE[option]
        success = await self._api.set_operation_mode(mode_value)

        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set operation mode to %s", option)


class MaicoSeasonSelect(CoordinatorEntity[MaicoCoordinator], SelectEntity):
    """Representation of Maico WS320B season select."""

    _attr_has_entity_name = True
    _attr_translation_key = "season"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_season_select"
        self._attr_device_info = coordinator.device_info
        self._attr_options = SEASON_MODES
        self._attr_icon = "mdi:weather-sunny-off"

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self.coordinator.data.get("season")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in SEASON_MODES:
            _LOGGER.error("Invalid season: %s", option)
            return

        season_value = SEASON_TO_VALUE[option]
        success = await self._api.set_season(season_value)

        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set season to %s", option)


class MaicoRoomTempSelectionSelect(CoordinatorEntity[MaicoCoordinator], SelectEntity):
    """Representation of Maico WS room temperature sensor selection."""

    _attr_has_entity_name = True
    _attr_translation_key = "room_temp_selection"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = (
            f"{self._api.host}_{self._api.port}_room_temp_selection_select"
        )
        self._attr_device_info = coordinator.device_info
        self._attr_options = ROOM_TEMP_SELECTION_MODES
        self._attr_icon = "mdi:thermometer-probe"

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self.coordinator.data.get("room_temp_selection")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in ROOM_TEMP_SELECTION_MODES:
            _LOGGER.error("Invalid room temp selection: %s", option)
            return

        sel_value = ROOM_TEMP_SEL_TO_VALUE[option]
        success = await self._api.set_room_temp_selection(sel_value)

        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set room temp selection to %s", option)
