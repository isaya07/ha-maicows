"""Tests for Maico WS init."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.maicows.const import CONF_SERIAL_NUMBER, DOMAIN

# Temporary: Allow socket to see if it fixes the issue (meaning mock is bypassed)
# or if it reveals where the connection goes.
# Ideally we fix the mock.


async def test_setup_unload_and_reload_entry(hass: HomeAssistant, mock_maico_ws_client):
    """Test entry setup and unload."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "1.2.3.4",
            CONF_PORT: 502,
            CONF_SCAN_INTERVAL: 30,
            CONF_SERIAL_NUMBER: "12345",
        },
        entry_id="test_entry_id",
    )
    config_entry.add_to_hass(hass)

    # Setup the entry
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify connection was attempted (entry is loaded)
    assert config_entry.state is ConfigEntryState.LOADED

    # Verify coordinator and API are stored
    assert DOMAIN in hass.data
    assert config_entry.entry_id in hass.data[DOMAIN]

    # Unload the entry
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.NOT_LOADED
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass: HomeAssistant, mock_maico_ws_client):
    """Test ConfigEntryNotReady when connection fails."""

    async def mock_connect_fail():
        return False

    with patch(
        "custom_components.maicows.maico_ws_api.AsyncModbusTcpClient"
    ) as mock_tcp_fail:
        mock_tcp_fail.return_value.connect.side_effect = mock_connect_fail

        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_HOST: "1.2.3.4",
                CONF_PORT: 502,
                CONF_SCAN_INTERVAL: 30,
                CONF_SERIAL_NUMBER: "12345",
            },
        )
        config_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.SETUP_RETRY
