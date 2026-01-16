"""Switch platform for Maico WS integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up the Maico WS320B switch platform."""
    coordinator: MaicoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        MaicoWS320BPowerSwitch(coordinator),
    ]

    # Add filter change switches (momentary - always show as OFF)
    entities.extend(
        [
            MaicoWS320BFilterChangeSwitch(coordinator, "device"),
            MaicoWS320BFilterChangeSwitch(coordinator, "outdoor"),
            MaicoWS320BFilterChangeSwitch(coordinator, "room"),
        ]
    )

    async_add_entities(entities, update_before_add=True)


class MaicoWS320BPowerSwitch(CoordinatorEntity[MaicoCoordinator], SwitchEntity):
    """Representation of a Maico WS320B power switch."""

    _attr_has_entity_name = True
    _attr_translation_key = "power"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_power_switch"
        self._attr_device_info = coordinator.device_info
        self._attr_icon = "mdi:power"

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self.coordinator.data.get("power_state")

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn on the VMC."""
        success = await self._api.write_power_state(state=True)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn on the VMC")

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn off the VMC."""
        success = await self._api.write_power_state(state=False)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn off the VMC")


class MaicoWS320BFilterChangeSwitch(CoordinatorEntity[MaicoCoordinator], SwitchEntity):
    """Representation of a Maico WS320B filter change switch (momentary)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MaicoCoordinator, filter_type: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._filter_type = filter_type
        self._attr_translation_key = f"filter_change_{filter_type}"
        self._attr_unique_id = (
            f"{self._api.host}_{self._api.port}_{filter_type}_filter_change"
        )
        self._attr_device_info = coordinator.device_info
        self._attr_icon = "mdi:air-filter"

    @property
    def is_on(self) -> bool:
        """Return false - this is a momentary switch, always shows as off."""
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Handle the switch press - mark the filter as changed."""
        success = False
        if self._filter_type == "device":
            success = await self._api.write_filter_change_device(changed=True)
        elif self._filter_type == "outdoor":
            success = await self._api.write_filter_change_outdoor(changed=True)
        elif self._filter_type == "room":
            success = await self._api.write_filter_change_room(changed=True)

        if success:
            _LOGGER.info("Successfully marked %s filter as changed", self._filter_type)
            # Refresh coordinator data to update filter days display
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to mark %s filter as changed", self._filter_type)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off does nothing - this is a momentary switch."""
