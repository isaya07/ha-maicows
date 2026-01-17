"""The Maico WS320B VMC integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SLAVE_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    PLATFORMS,
)
from .maico_ws_api import MaicoWS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class MaicoCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Maico WS320B data."""

    def __init__(
        self, hass: HomeAssistant, api: MaicoWS320B, entry: ConfigEntry
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self.entry = entry

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        data = await self.api.get_all_status()
        if data is None:
            msg = "Error communicating with API"
            raise UpdateFailed(msg)
        return data

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, f"{self.api.host}_{self.api.port}")},
            "name": self.entry.title,
            "manufacturer": "Maico",
            "model": "WS",
            "sw_version": "1.0.0",
        }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Maico WS from a config entry."""
    from .const import (
        CONF_BAUDRATE,
        CONF_CONNECTION_TYPE,
        CONF_SERIAL_PORT,
        CONNECTION_TYPE_RTU,
    )

    connection_type = entry.data.get(CONF_CONNECTION_TYPE, "tcp")
    slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

    # Initialize the MaicoWS API based on connection type
    if connection_type == CONNECTION_TYPE_RTU:
        serial_port = entry.data[CONF_SERIAL_PORT]
        baudrate = entry.data.get(CONF_BAUDRATE, 9600)
        maico_api = MaicoWS(
            serial_port=serial_port, baudrate=baudrate, slave_id=slave_id
        )
        conn_str = f"{serial_port} @ {baudrate} baud"
    else:  # TCP
        host = entry.data[CONF_HOST]
        port = entry.data.get(CONF_PORT, DEFAULT_PORT)
        maico_api = MaicoWS(host=host, port=port, slave_id=slave_id)
        conn_str = f"{host}:{port}"

    # Try to connect to the device to verify connection
    try:
        connected = await maico_api.connect()
        if not connected:
            msg = f"Could not connect to Maico WS at {conn_str}"
            raise ConfigEntryNotReady(msg)
    except Exception as e:
        _LOGGER.exception("Failed to connect to Maico WS: %s", e)
        msg = f"Failed to connect to Maico WS: {e}"
        raise ConfigEntryNotReady(msg) from e

    # Create the coordinator
    coordinator = MaicoCoordinator(hass, maico_api, entry)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator instance in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Register the device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        **coordinator.device_info,
    )

    # Forward the setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Disconnect from the device
    coordinator: MaicoCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.api.disconnect()

    # Remove the coordinator instance from hass.data
    hass.data[DOMAIN].pop(entry.entry_id)

    # Unload platforms
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
