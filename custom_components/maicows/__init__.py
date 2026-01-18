"""The Maico WS integration initialization."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from .const import (
    CONF_BAUDRATE,
    CONF_CONNECTION_TYPE,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONNECTION_TYPE_RTU,
    DOMAIN,
)
from .maico_ws_api import MaicoWS, MaicoWS320B

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.FAN,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


class MaicoCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Maico WS data."""

    def __init__(
        self, hass: HomeAssistant, api: MaicoWS320B, entry: ConfigEntry
    ) -> None:
        """Initialize."""
        self.api = api
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> Any:
        """Fetch data from API endpoint."""
        data = await self.api.read_all_registers()
        if not data:
            msg = "Error reading data from Maico WS device"
            raise UpdateFailed(msg)
        return data

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": f"Maico WS {self.entry.entry_id}",
            "manufacturer": "Maico",
            "model": "WS 320 B",
        }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Maico WS from a config entry."""
    connection_type = entry.data.get(CONF_CONNECTION_TYPE, "tcp")
    slave_id = entry.data.get(CONF_SLAVE_ID, 1)

    if connection_type == CONNECTION_TYPE_RTU:
        # RTU / Serial
        serial_port = entry.data.get(CONF_SERIAL_PORT, "/dev/ttyUSB0")
        baudrate = entry.data.get(CONF_BAUDRATE, 9600)
        api = MaicoWS(serial_port=serial_port, baudrate=baudrate, slave_id=slave_id)
        conn_str = f"serial {serial_port} ({baudrate} baud)"
    else:
        # TCP
        host = entry.data.get(CONF_HOST)
        port = entry.data.get(CONF_PORT, 502)
        api = MaicoWS(host=host, port=port, slave_id=slave_id)
        conn_str = f"{host}:{port}"

    try:
        connected = await api.connect()
    except Exception as e:
        _LOGGER.exception("Failed to connect to Maico WS")
        msg = f"Failed to connect to Maico WS: {e}"
        raise ConfigEntryNotReady(msg) from e

    if not connected:
        msg = f"Could not connect to Maico WS at {conn_str}"
        raise ConfigEntryNotReady(msg)

    # Create the coordinator
    coordinator = MaicoCoordinator(hass, api, entry)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator instance in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward the setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Disconnect from the device
    coordinator: MaicoCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.api.disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
