"""Configuration flow for the Maico WS integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_BAUDRATE,
    CONF_CONNECTION_TYPE,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONNECTION_TYPE_RTU,
    CONNECTION_TYPE_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SERIAL_PORT,
    DEFAULT_SLAVE_ID,
    DOMAIN,
)
from .maico_ws_api import MaicoWS

_LOGGER = logging.getLogger(__name__)

STEP_CONNECTION_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONNECTION_TYPE, default=CONNECTION_TYPE_TCP): vol.In(
            {CONNECTION_TYPE_TCP: "Modbus TCP", CONNECTION_TYPE_RTU: "Modbus RTU"}
        ),
    }
)

STEP_TCP_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)

STEP_RTU_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERIAL_PORT, default=DEFAULT_SERIAL_PORT): str,
        vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In(
            [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
        ),
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    connection_type = data.get(CONF_CONNECTION_TYPE)

    # Try to connect to the device
    if connection_type == CONNECTION_TYPE_TCP:
        host = data[CONF_HOST]
        port = data[CONF_PORT]
        slave_id = data[CONF_SLAVE_ID]
        maico_api = MaicoWS(host=host, port=port, slave_id=slave_id)
    else:  # RTU
        serial_port = data[CONF_SERIAL_PORT]
        baudrate = data[CONF_BAUDRATE]
        slave_id = data[CONF_SLAVE_ID]
        maico_api = MaicoWS(
            serial_port=serial_port, baudrate=baudrate, slave_id=slave_id
        )

    try:
        connected = await maico_api.connect()
        if connected:
            await maico_api.disconnect()
            return {"title": data[CONF_NAME]}
        msg = "Could not connect to Maico WS"
        raise CannotConnectError(msg)  # noqa: TRY301
    except CannotConnectError:
        raise
    except Exception as e:
        msg = f"Connection failed: {e}"
        raise CannotConnectError(msg) from e


class MaicoWSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Maico WS."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._connection_type = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return MaicoOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step - select connection type."""
        if user_input is not None:
            self._connection_type = user_input[CONF_CONNECTION_TYPE]
            if self._connection_type == CONNECTION_TYPE_TCP:
                return await self.async_step_tcp()
            return await self.async_step_rtu()

        return self.async_show_form(
            step_id="user", data_schema=STEP_CONNECTION_TYPE_SCHEMA
        )

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle TCP configuration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_CONNECTION_TYPE] = CONNECTION_TYPE_TCP
            try:
                info = await validate_input(user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="tcp", data_schema=STEP_TCP_DATA_SCHEMA, errors=errors
        )

    async def async_step_rtu(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle RTU configuration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_CONNECTION_TYPE] = CONNECTION_TYPE_RTU
            try:
                info = await validate_input(user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="rtu", data_schema=STEP_RTU_DATA_SCHEMA, errors=errors
        )


class MaicoOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Maico WS."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Manage the options."""
        return self.async_show_form(step_id="init")


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""
