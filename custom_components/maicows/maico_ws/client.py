"""Maico WS base client for Modbus communication."""

from __future__ import annotations

import logging

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException

from .registers import MaicoWSRegisters

_LOGGER = logging.getLogger(__name__)


class MaicoWSClient:
    """Base Modbus client for Maico WS VMC supporting TCP and RTU."""

    def __init__(
        self,
        host: str | None = None,
        port: int = 502,
        serial_port: str | None = None,
        baudrate: int = 9600,
        slave_id: int = 1,
    ) -> None:
        """
        Initialize the Maico WS API.

        For TCP: provide host and port
        For RTU: provide serial_port and baudrate
        """
        self._host = host
        self._port = port
        self._serial_port = serial_port
        self._baudrate = baudrate
        self._slave_id = slave_id
        self._client: AsyncModbusTcpClient | AsyncModbusSerialClient | None = None
        self._connected = False
        self._is_rtu = serial_port is not None

    @property
    def host(self) -> str | None:
        """Return the host."""
        return self._host

    @property
    def port(self) -> int:
        """Return the port."""
        return self._port

    @property
    def slave_id(self) -> int:
        """Return the slave id."""
        return self._slave_id

    @property
    def connected(self) -> bool:
        """Return connection status."""
        return self._connected

    async def connect(self) -> bool:
        """Connect to the Maico WS device."""
        try:
            if self._is_rtu:
                self._client = AsyncModbusSerialClient(
                    port=self._serial_port,
                    baudrate=self._baudrate,
                    bytesize=8,
                    parity="E",  # Even parity per Maico documentation
                    stopbits=1,
                    timeout=3,
                )
                _LOGGER.debug(
                    "Connecting to Maico WS via RTU: %s @ %d baud",
                    self._serial_port,
                    self._baudrate,
                )
            else:
                self._client = AsyncModbusTcpClient(
                    host=self._host,
                    port=self._port,
                )
                _LOGGER.debug(
                    "Connecting to Maico WS via TCP: %s:%d",
                    self._host,
                    self._port,
                )

            if await self._client.connect():
                self._connected = True
                connection_type = "RTU" if self._is_rtu else "TCP"
                _LOGGER.debug("Connected to Maico WS via %s", connection_type)
                return True

        except ConnectionException:
            _LOGGER.exception("Connection error to Maico WS")
            return False
        except Exception:
            _LOGGER.exception("Error connecting to Maico WS")
            return False

        connection_type = "RTU" if self._is_rtu else "TCP"
        _LOGGER.error("Failed to connect to Maico WS via %s", connection_type)
        return False

    async def disconnect(self) -> None:
        """Disconnect from the Maico WS device."""
        if self._client:
            self._client.close()
            self._connected = False
            _LOGGER.debug("Disconnected from Maico WS")

    async def read_holding_register(self, register: int) -> int | None:
        """Read a single holding register."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=register,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading register %d: %s", register, response)
                return None

            return response.registers[0]

        except ModbusException:
            _LOGGER.exception("Modbus error reading register %d", register)
            return None
        except Exception:
            _LOGGER.exception("Error reading register %d", register)
            return None

    async def read_holding_registers(
        self, register: int, count: int
    ) -> list[int] | None:
        """Read multiple holding registers."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=register,
                count=count,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error reading registers %d-%d: %s",
                    register,
                    register + count - 1,
                    response,
                )
                return None

            return list(response.registers)

        except ModbusException:
            _LOGGER.exception(
                "Modbus error reading registers %d-%d", register, register + count - 1
            )
            return None
        except Exception:
            _LOGGER.exception(
                "Error reading registers %d-%d", register, register + count - 1
            )
            return None

    async def write_register(self, register: int, value: int) -> bool:
        """Write a value to a single holding register."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS")
            return False

        try:
            response = await self._client.write_register(
                address=register,
                value=value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing register %d: %s", register, response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error writing register %d", register)
            return False
        except Exception:
            _LOGGER.exception("Error writing register %d", register)
            return False
        else:
            _LOGGER.debug("Wrote value %d to register %d", value, register)
            return True

    # Helper methods for data conversion
    @staticmethod
    def to_signed(value: int) -> int:
        """Convert unsigned 16-bit to signed 16-bit."""
        if value > MaicoWSRegisters.MAX_INT_16BIT:
            return value - 65536
        return value

    @staticmethod
    def to_temp(raw: int) -> float:
        """Convert raw register value to temperature (°C)."""
        signed = MaicoWSClient.to_signed(raw)
        return signed / 10.0

    @staticmethod
    def combine_words(hi: int, lo: int) -> int:
        """Combine high and low words into a 32-bit value."""
        return (hi << 16) | lo
