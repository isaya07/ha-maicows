"""Fixtures for Maico WS tests."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    return


@pytest.fixture(autouse=True)
def mock_pymodbus_clients():
    """Mock pymodbus clients to prevent socket usage."""
    with (
        patch(
            "custom_components.maicows.maico_ws_api.AsyncModbusTcpClient"
        ) as mock_tcp,
        patch(
            "custom_components.maicows.maico_ws_api.AsyncModbusSerialClient"
        ) as mock_serial,
    ):
        # Configure TCP client
        tcp_client = mock_tcp.return_value

        async def mock_tcp_connect():
            return True

        tcp_client.connect.side_effect = mock_tcp_connect
        tcp_client.connected = True

        async def mock_tcp_read(address, count=1, **kwargs):
            mock = MagicMock()
            mock.isError.return_value = False
            mock.registers = [0] * count
            return mock

        tcp_client.read_holding_registers.side_effect = mock_tcp_read

        async def mock_tcp_write(*args, **kwargs):
            mock = MagicMock()
            mock.isError.return_value = False
            return mock

        tcp_client.write_register.side_effect = mock_tcp_write

        # Configure Serial client similarly (optional but good for safety)
        serial_client = mock_serial.return_value
        serial_client.connect.side_effect = mock_tcp_connect

        yield


@pytest.fixture
def mock_setup_entry():
    """Mock setting up a config entry."""
    with patch(
        "custom_components.maicows.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
def mock_maico_ws_client():
    """Mock MaicoWS client."""
    with (
        patch(
            "custom_components.maicows.maico_ws_api.MaicoWS", autospec=True
        ) as mock_client,
        patch("custom_components.maicows.config_flow.MaicoWS", new=mock_client),
    ):
        client = mock_client.return_value
        client.host = "1.2.3.4"
        client.port = 502

        async def mock_connect():
            return True

        client.connect.side_effect = mock_connect

        async def mock_get_all_status():
            return {}

        client.get_all_status.side_effect = mock_get_all_status

        async def mock_get_device_info():
            return {"serial_number": "12345"}

        client.get_device_info.side_effect = mock_get_device_info

        client.connected = True
        yield client
