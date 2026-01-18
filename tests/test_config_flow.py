"""Tests for the Maico WS config flow."""
from unittest.mock import MagicMock, patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.core import HomeAssistant

from custom_components.maicows.const import (
    DOMAIN, 
    CONF_SERIAL_NUMBER, 
    CONF_SLAVE_ID,
    CONF_CONNECTION_TYPE,
    CONNECTION_TYPE_TCP
)


async def test_form(hass: HomeAssistant, mock_maico_ws_client):
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # Step 1: Select connection type TCP
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CONNECTION_TYPE: CONNECTION_TYPE_TCP},
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "tcp"
    assert result.get("errors") is None or result["errors"] == {}

    # Step 2: Enter TCP details
    with patch(
        "custom_components.maicows.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "1.2.3.4",
                CONF_PORT: 502,
                CONF_SLAVE_ID: 1,
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Maico WS"
    assert result2["data"] == {
        CONF_HOST: "1.2.3.4",
        CONF_PORT: 502,
        CONF_SLAVE_ID: 1,
        CONF_CONNECTION_TYPE: CONNECTION_TYPE_TCP,
        CONF_NAME: "Maico WS",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(hass: HomeAssistant, mock_maico_ws_client):
    """Test we handle cannot connect error."""
    async def mock_connect_fail():
        return False
    mock_maico_ws_client.connect.side_effect = mock_connect_fail
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    # Step 1
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CONNECTION_TYPE: CONNECTION_TYPE_TCP},
    )

    # Step 2
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "1.2.3.4",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
        },
    )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_exception(hass: HomeAssistant, mock_maico_ws_client):
    """Test we handle unknown exceptions."""
    # Patch validate_input directly to bypass its internal try/except
    with patch(
        "custom_components.maicows.config_flow.validate_input",
        side_effect=Exception("Boom"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        # Step 1
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_CONNECTION_TYPE: CONNECTION_TYPE_TCP},
        )

        # Step 2
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "1.2.3.4",
                CONF_PORT: 502,
                CONF_SLAVE_ID: 1,
            },
        )

        assert result2["type"] == data_entry_flow.FlowResultType.FORM
        assert result2["errors"] == {"base": "unknown"}
