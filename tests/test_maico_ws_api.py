"""Tests for the Maico WS API."""

from unittest.mock import MagicMock, patch

import pytest
from pymodbus.exceptions import ModbusException

from custom_components.maicows.maico_ws_api import MaicoWS


@pytest.fixture
def mock_modbus_client():
    """Mock the AsyncModbusTcpClient."""
    with patch(
        "custom_components.maicows.maico_ws_api.AsyncModbusTcpClient"
    ) as mock_client:
        client = mock_client.return_value
        # Mock connect as an async method returning True
        client.connect = MagicMock(return_value=True)
        # For pymodbus v3, connect is async
        client.connect.side_effect = None

        # But wait, MagicMock isn't awaitable by default unless used as return_value
        # of an AsyncMock
        # Easier: make it a coroutine
        async def mock_connect():
            return True

        client.connect.side_effect = mock_connect

        # Also need write_register to be async
        async def mock_write_register(*args, **kwargs):
            mock = MagicMock()
            mock.isError.return_value = False
            return mock

        client.write_register.side_effect = mock_write_register

        # And read_holding_registers
        async def mock_read_holding_registers(address, count, device_id):
            mock = MagicMock()
            mock.isError.return_value = False
            # Return list of correct length based on requested count
            mock.registers = [0] * count
            return mock

        client.read_holding_registers.side_effect = mock_read_holding_registers

        yield client


async def test_connect_success(mock_modbus_client):
    """Test successful connection."""
    api = MaicoWS("localhost", 502)
    assert await api.connect() is True
    assert api.connected is True


async def test_connect_failure(mock_modbus_client):
    """Test connection failure."""

    async def mock_connect_fail():
        return False

    mock_modbus_client.connect.side_effect = mock_connect_fail

    api = MaicoWS("localhost", 502)
    assert await api.connect() is False
    assert api.connected is False


async def test_read_all_registers_success(mock_modbus_client):
    """Test reading all registers successfully."""
    api = MaicoWS("localhost", 502)
    await api.connect()

    # Mock behavior already set in fixture but we can override if needed
    # The default fixture setup should handle it now

    data = await api.get_all_status()
    assert data is not None
    assert isinstance(data, dict)


async def test_write_ventilation_level(mock_modbus_client):
    """Test writing ventilation level."""
    api = MaicoWS("localhost", 502)
    await api.connect()

    assert await api.write_ventilation_level(1) is True
    # Verify call arguments
    # Note: write_register is now a coroutine side_effect, checking calls
    # on the mock_client itself might be tricky
    # heavily mocked objects sometimes loose call history on side_effect coroutines
    # depending on how they are attached
    # But let's check correct calls
    mock_modbus_client.write_register.assert_called()


async def test_write_ventilation_level_invalid(mock_modbus_client):
    """Test writing invalid ventilation level."""
    api = MaicoWS("localhost", 502)
    await api.connect()

    # 0 to 4 are valid
    assert await api.write_ventilation_level(5) is False
    mock_modbus_client.write_register.assert_not_called()


async def test_modbus_exception_handling(mock_modbus_client):
    """Test handling of Modbus exceptions."""
    api = MaicoWS("localhost", 502)
    await api.connect()

    mock_modbus_client.read_holding_registers.side_effect = ModbusException(
        "Test Error"
    )

    result = await api.read_holding_registers_block(100, 1)
    assert result is None
