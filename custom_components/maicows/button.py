"""Button platform for Maico WS integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MaicoCoordinator
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Maico WS320B button platform."""
    coordinator: MaicoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        MaicoWS320BErrorResetButton(coordinator),
    ]

    async_add_entities(entities)


class MaicoWS320BErrorResetButton(CoordinatorEntity[MaicoCoordinator], ButtonEntity):
    """Representation of the Maico WS320B Error Reset button."""

    _attr_has_entity_name = True
    _attr_translation_key = "error_reset"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_error_reset"
        self._attr_device_info = coordinator.device_info
        self._attr_icon = "mdi:alert-remove"

    async def async_press(self) -> None:
        """Handle the button press."""
        success = await self._api.trigger_error_reset()
        if success:
            _LOGGER.info("Error reset triggered successfully")
            # Refresh coordinator data to clear error status
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to trigger error reset")
