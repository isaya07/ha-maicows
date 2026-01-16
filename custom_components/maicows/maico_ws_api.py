"""Maico WS API to handle Modbus communication."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException

_LOGGER = logging.getLogger(__name__)


# Maico WS Modbus register definitions
# Based on official documentation from KWL_Steuerung_Modbus_Parameterbeschreibung_RTU_TCP.csv
class MaicoWSRegisters:
    """Register addresses for Maico WS VMC based on official documentation."""

    # Date/Time Settings
    DATE_YEAR = 100  # Jahr
    DATE_MONTH = 101  # Monat
    DATE_DAY = 102  # Tag
    TIME_HOUR = 103  # Stunde
    TIME_MINUTE = 104  # Minute
    TIME_SECOND = 105  # Sekunde

    # Filter Settings
    FILTER_DEVICE_MONTHS = 150  # Filterstand Gerätefilter (3-12 months)
    FILTER_OUTDOOR_MONTHS = 151  # Filterstand Aussenfilter (3-18 months)
    FILTER_ROOM_MONTHS = 152  # Filterstand Raumfilter (1-6 months)
    FILTER_CHANGE_DEVICE = 157  # Filterwechsel Gerätefilter (0=not changed, 1=changed)
    FILTER_CHANGE_OUTDOOR = 158  # Filterwechsel Außenfilter (0=not changed, 1=changed)
    FILTER_CHANGE_ROOM = 159  # Filterwechsel Raumfilter (0=not changed, 1=changed)

    # Temperature Settings
    ROOM_TEMP_ADJUST = 300  # Abgleich Raumtemperatur
    SUPPLY_TEMP_MIN_COOL = 301  # T-Zuluft min. kühlen
    ROOM_TEMP_MAX = 302  # T-Raum max.

    # Error and Info Messages
    CURRENT_ERROR_HI = 401  # Aktueller Fehler (High-Word)
    CURRENT_ERROR_LO = 402  # Aktueller Fehler (Low-Word)
    CURRENT_INFO_HI = 403  # Aktueller Hinweis (High-Word)
    CURRENT_INFO_LO = 404  # Aktueller Hinweis (Low-Word)
    ERROR_RESET = 405  # Fehler Reset (0=normal, 1=reset)

    # Basic Settings
    OPERATION_MODE = 550  # Operation mode (0=Off, 1=Manual, 2=Auto-Time, 3=Auto-Sensor, 4=Eco-Supply Air, 5=Eco-Extract Air)
    BOOST_VENTILATION = 551  # Stoßlüftung (0=inaktiv, 1=aktiv)
    SEASON = 552  # Jahreszeit (0=Winter, 1=Sommer)
    TARGET_ROOM_TEMP = 553  # Solltemperatur Raum (°C * 10)
    VENTILATION_LEVEL = 554  # Ventilation level (0=Off, 1=Humidity protection, 2=Reduced, 3=Nominal, 4=Intensive)

    # Ventilation Queries
    CURRENT_VENTILATION_LEVEL = 650  # Current ventilation level (0=Off, 1=Humidity protection, 2=Reduced, 3=Nominal, 4=Intensive)
    SUPPLY_FAN_SPEED = 651  # Current supply fan speed (U/min)
    EXTRACT_FAN_SPEED = 652  # Current extract fan speed (U/min)
    SUPPLY_VOLUME_FLOW = 653  # Current supply volume flow (m³/h)
    EXTRACT_VOLUME_FLOW = 654  # Current extract volume flow (m³/h)
    FILTER_REMAIN_DEVICE = 655  # Device filter remaining time (days)
    FILTER_REMAIN_OUTDOOR = 656  # Outdoor filter remaining time (days)
    FILTER_REMAIN_ROOM = 657  # Room filter remaining time (days)

    # Current Temperatures
    ROOM_TEMP = 700  # Room temperature (°C * 10)
    ROOM_TEMP_EXT = 701  # External room temperature (°C * 10)
    INLET_AIR_TEMP = 703  # Inlet air temperature (°C * 10)
    SUPPLY_AIR_TEMP = 704  # Supply air temperature (°C * 10)
    EXTRACT_AIR_TEMP = 705  # Extract air temperature (°C * 10)
    EXHAUST_AIR_TEMP = 706  # Exhaust air temperature (°C * 10)

    # Humidity Data
    EXTRACT_AIR_HUMIDITY = 750  # Extract air humidity (% * 10)
    HUMIDITY_SENSOR_1 = 751  # Humidity sensor 1 (% * 10)
    HUMIDITY_SENSOR_2 = 752  # Humidity sensor 2 (%10)
    HUMIDITY_SENSOR_3 = 753  # Humidity sensor 3 (% * 10)
    HUMIDITY_SENSOR_4 = 754  # Humidity sensor 4 (% * 10)

    # Switch States
    SUPPLY_FAN_STATE = 800  # Supply fan state (0=off, 1=on)
    EXTRACT_FAN_STATE = 801  # Extract fan state (0=off, 1=on)
    BYPASS_ACTUATOR = 802  # Summer bypass actuator (0=closed, 1=open)
    PTC_HEATER = 803  # PTC heater (0=off, 1=on)


class MaicoWS:
    """Maico WS VMC API class supporting both TCP and RTU."""

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

    async def connect(self) -> bool:
        """Connect to the Maico WS device."""
        try:
            if self._is_rtu:
                # Modbus RTU connection
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
                # Modbus TCP connection
                self._client = AsyncModbusTcpClient(
                    host=self._host,
                    port=self._port,
                )
                _LOGGER.debug(
                    "Connecting to Maico WS via TCP: %s:%d", self._host, self._port
                )

            result = await self._client.connect()
            if result:
                self._connected = True
                connection_type = "RTU" if self._is_rtu else "TCP"
                _LOGGER.debug("Connected to Maico WS via %s", connection_type)
                return True
            connection_type = "RTU" if self._is_rtu else "TCP"
            _LOGGER.error("Failed to connect to Maico WS via %s", connection_type)
            return False
        except ConnectionException as e:
            _LOGGER.exception("Connection error to Maico WS: %s", e)
            return False
        except Exception as e:
            _LOGGER.exception("Unexpected error during connection: %s", e)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the Maico WS device."""
        if self._client:
            self._client.close()
            self._connected = False
            _LOGGER.debug("Disconnected from Maico WS")

    async def read_temperature(self, register: int) -> float | None:
        """Read temperature value from register (values are in 0.1°C increments)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=register,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error reading temperature register %d: %s", register, response
                )
                return None

            # Convert unsigned 16-bit to signed 16-bit
            raw_value = response.registers[0]
            if raw_value > 32767:
                raw_value -= 65536
            # Temperature values are stored in 0.1°C increments
            return raw_value / 10.0

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error reading temperature register %d: %s", register, e
            )
            return None
        except Exception as e:
            _LOGGER.exception("Error reading temperature register %d: %s", register, e)
            return None

    async def read_humidity(self, register: int) -> int | None:
        """Read humidity value from register (values are in 0.1% increments)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=register,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error reading humidity register %d: %s", register, response
                )
                return None

            raw_value = response.registers[0]
            humidity = raw_value / 10.0  # Convert from 0.1% to %
            return int(humidity)

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error reading humidity register %d: %s", register, e
            )
            return None
        except Exception as e:
            _LOGGER.exception("Error reading humidity register %d: %s", register, e)
            return None

    async def read_fan_speed(self, register: int) -> int | None:
        """Read fan speed value from register."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=register,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error reading fan speed register %d: %s", register, response
                )
                return None

            return response.registers[0]

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error reading fan speed register %d: %s", register, e
            )
            return None
        except Exception as e:
            _LOGGER.exception("Error reading fan speed register %d: %s", register, e)
            return None

    async def read_current_ventilation_level(self) -> int | None:
        """Read current ventilation level."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.CURRENT_VENTILATION_LEVEL,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading current ventilation level: %s", response)
                return None

            response.registers[0]
            return level

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading current ventilation level: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading current ventilation level: %s", e)
            return None

    async def read_supply_air_temperature(self) -> float | None:
        """Read supply air temperature."""
        return await self.read_temperature(MaicoWSRegisters.SUPPLY_AIR_TEMP)

    async def read_extract_air_temperature(self) -> float | None:
        """Read extract air temperature."""
        return await self.read_temperature(MaicoWSRegisters.EXTRACT_AIR_TEMP)

    async def read_room_temperature(self) -> float | None:
        """Read room temperature."""
        return await self.read_temperature(MaicoWSRegisters.ROOM_TEMP)

    async def read_inlet_air_temperature(self) -> float | None:
        """Read inlet air temperature."""
        return await self.read_temperature(MaicoWSRegisters.INLET_AIR_TEMP)

    async def read_exhaust_air_temperature(self) -> float | None:
        """Read exhaust air temperature."""
        return await self.read_temperature(MaicoWSRegisters.EXHAUST_AIR_TEMP)

    async def read_supply_air_humidity(self) -> int | None:
        """Read supply air humidity."""
        return await self.read_humidity(MaicoWSRegisters.EXTRACT_AIR_HUMIDITY)

    async def read_supply_fan_speed(self) -> int | None:
        """Read supply fan speed."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.SUPPLY_FAN_SPEED,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading supply fan speed: %s", response)
                return None

            response.registers[0]
            return speed

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading supply fan speed: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading supply fan speed: %s", e)
            return None

    async def read_extract_fan_speed(self) -> int | None:
        """Read extract fan speed."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.EXTRACT_FAN_SPEED,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading extract fan speed: %s", response)
                return None

            response.registers[0]
            return speed

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading extract fan speed: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading extract fan speed: %s", e)
            return None

    async def read_power_state(self) -> bool | None:
        """Read power state of the VMC (based on operation mode)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.OPERATION_MODE,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading power state: %s", response)
                return None

            # Operation mode 0 = Off, any other value = On
            operation_mode = response.registers[0]
            return operation_mode != 0

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading power state: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading power state: %s", e)
            return None

    async def read_filter_status(self) -> dict[str, int] | None:
        """Read filter status including remaining time for each filter."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            # Read remaining time for each filter (in days)
            device_filter_days = await self._client.read_holding_registers(
                address=MaicoWSRegisters.FILTER_REMAIN_DEVICE,
                count=1,
                device_id=self._slave_id,
            )

            outdoor_filter_days = await self._client.read_holding_registers(
                address=MaicoWSRegisters.FILTER_REMAIN_OUTDOOR,
                count=1,
                device_id=self._slave_id,
            )

            room_filter_days = await self._client.read_holding_registers(
                address=MaicoWSRegisters.FILTER_REMAIN_ROOM,
                count=1,
                device_id=self._slave_id,
            )

            status = {}
            if device_filter_days and not device_filter_days.isError():
                status["device_filter_days"] = decoder.decode_16bit_uint()

            if outdoor_filter_days and not outdoor_filter_days.isError():
                status["outdoor_filter_days"] = decoder.decode_16bit_uint()

            if room_filter_days and not room_filter_days.isError():
                status["room_filter_days"] = decoder.decode_16bit_uint()

            return status

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading filter status: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading filter status: %s", e)
            return None

    async def read_fault_status(self) -> str | None:
        """Read fault status from high and low word registers."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            # Read both high and low word for error codes
            error_hi_response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.CURRENT_ERROR_HI,
                count=1,
                device_id=self._slave_id,
            )

            error_lo_response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.CURRENT_ERROR_LO,
                count=1,
                device_id=self._slave_id,
            )

            if error_hi_response.isError() or error_lo_response.isError():
                _LOGGER.error("Error reading fault status")
                return None

            error_hi = error_hi_response.registers[0]
            error_lo = error_lo_response.registers[0]

            # If both registers are 0, no errors
            if error_hi == 0 and error_lo == 0:
                return "no_fault"
            # Return combined error code
            return f"error_hi_{error_hi}_lo_{error_lo}"

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading fault status: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading fault status: %s", e)
            return None

    async def read_info_messages(self) -> str | None:
        """Read info messages from high and low word registers."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            # Read both high and low word for info messages
            info_hi_response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.CURRENT_INFO_HI,
                count=1,
                device_id=self._slave_id,
            )

            info_lo_response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.CURRENT_INFO_LO,
                count=1,
                device_id=self._slave_id,
            )

            if info_hi_response.isError() or info_lo_response.isError():
                _LOGGER.error("Error reading info messages")
                return None

            info_hi = info_hi_response.registers[0]
            info_lo = info_lo_response.registers[0]

            # If both registers are 0, no info messages
            if info_hi == 0 and info_lo == 0:
                return "no_info"
            # Return combined info code
            return f"info_hi_{info_hi}_lo_{info_lo}"

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading info messages: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading info messages: %s", e)
            return None

    async def read_operation_mode(self) -> str | None:
        """Read operation mode based on official documentation."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.OPERATION_MODE,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading operation mode: %s", response)
                return None

            response.registers[0]

            # Map mode codes to human-readable strings based on documentation
            # 0=Aus, 1=Manuell, 2=Auto-Zeit, 3=Auto-Sensor, 4=Eco-Zuluft, 5=Eco-Abluft
            mode_map = {
                0: "off",
                1: "manual",
                2: "auto_time",
                3: "auto_sensor",
                4: "eco_supply",
                5: "eco_extract",
            }

            return mode_map.get(mode_code, f"unknown_{mode_code}")

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading operation mode: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading operation mode: %s", e)
            return None

    async def read_fault_status(self) -> str | None:
        """Read fault status/code."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.FAULT_CODE,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading fault status: %s", response)
                return None

            response.registers[0]

            # Return fault code or "no_fault" if 0
            if fault_code == 0:
                return "no_fault"
            return f"fault_{fault_code}"

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading fault status: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading fault status: %s", e)
            return None

    async def read_info_messages(self) -> str | None:
        """Read info messages."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.INFO_CODE,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading info messages: %s", response)
                return None

            response.registers[0]

            # Return info code or "no_info" if 0
            if info_code == 0:
                return "no_info"
            return f"info_{info_code}"

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading info messages: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading info messages: %s", e)
            return None

    async def read_bypass_status(self) -> bool | None:
        """Read bypass actuator status."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.BYPASS_ACTUATOR,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading bypass actuator status: %s", response)
                return None

            response.registers[0]
            # 0=zu (closed), 1=auf (open)
            return bool(status)

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading bypass actuator status: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading bypass actuator status: %s", e)
            return None

    async def read_supply_fan_state(self) -> bool | None:
        """Read supply fan state."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.SUPPLY_FAN_STATE,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading supply fan state: %s", response)
                return None

            response.registers[0]
            # 0=aus (off), 1=ein (on)
            return bool(state)

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading supply fan state: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading supply fan state: %s", e)
            return None

    async def read_extract_fan_state(self) -> bool | None:
        """Read extract fan state."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.EXTRACT_FAN_STATE,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading extract fan state: %s", response)
                return None

            response.registers[0]
            # 0=aus (off), 1=ein (on)
            return bool(state)

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading extract fan state: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading extract fan state: %s", e)
            return None

    async def read_season(self) -> str | None:
        """Read season setting (Winter or Summer)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.SEASON,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading season setting: %s", response)
                return None

            raw_value = response.registers[0]

            # 0=Winter, 1=Sommer
            if raw_value == 0:
                return "winter"
            if raw_value == 1:
                return "summer"
            return f"unknown_{raw_value}"

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading season setting: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading season setting: %s", e)
            return None

    async def write_season(self, season: int) -> bool:
        """Write season setting (0=Winter, 1=Summer)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        if season not in [0, 1]:
            _LOGGER.error(
                "Invalid season: %d. Must be 0 (Winter) or 1 (Summer).", season
            )
            return False

        try:
            response = await self._client.write_register(
                address=MaicoWSRegisters.SEASON,
                value=season,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing season %d: %s", season, response)
                return False

            _LOGGER.debug("Season set to: %s", "Summer" if season == 1 else "Winter")
            return True

        except ModbusException as e:
            _LOGGER.exception("Modbus error writing season %d: %s", season, e)
            return False
        except Exception as e:
            _LOGGER.exception("Error writing season %d: %s", season, e)
            return False

    async def write_filter_change_device(self, changed: bool) -> bool:
        """Write device filter change status (0=not changed, 1=changed)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            value = 1 if changed else 0
            response = await self._client.write_register(
                address=MaicoWSRegisters.FILTER_CHANGE_DEVICE,
                value=value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing device filter change status: %s", response)
                return False

            _LOGGER.debug("Device filter change status set to: %s", changed)
            return True

        except ModbusException as e:
            _LOGGER.exception("Modbus error writing device filter change status: %s", e)
            return False
        except Exception as e:
            _LOGGER.exception("Error writing device filter change status: %s", e)
            return False

    async def write_filter_change_outdoor(self, changed: bool) -> bool:
        """Write outdoor filter change status (0=not changed, 1=changed)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            value = 1 if changed else 0
            response = await self._client.write_register(
                address=MaicoWSRegisters.FILTER_CHANGE_OUTDOOR,
                value=value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error writing outdoor filter change status: %s", response
                )
                return False

            _LOGGER.debug("Outdoor filter change status set to: %s", changed)
            return True

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error writing outdoor filter change status: %s", e
            )
            return False
        except Exception as e:
            _LOGGER.exception("Error writing outdoor filter change status: %s", e)
            return False

    async def write_filter_change_room(self, changed: bool) -> bool:
        """Write room filter change status (0=not changed, 1=changed)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            value = 1 if changed else 0
            response = await self._client.write_register(
                address=MaicoWSRegisters.FILTER_CHANGE_ROOM,
                value=value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing room filter change status: %s", response)
                return False

            _LOGGER.debug("Room filter change status set to: %s", changed)
            return True

        except ModbusException as e:
            _LOGGER.exception("Modbus error writing room filter change status: %s", e)
            return False
        except Exception as e:
            _LOGGER.exception("Error writing room filter change status: %s", e)
            return False

    async def read_supply_temp_min_cool(self) -> float | None:
        """Read minimum supply air temperature for cooling (°C * 10)."""
        return await self.read_temperature(MaicoWSRegisters.SUPPLY_TEMP_MIN_COOL)

    async def write_supply_temp_min_cool(self, temperature: float) -> bool:
        """
        Write minimum supply air temperature for cooling.

        Register 301 stores values directly in °C (min=8, max=29).
        NO multiplication by 10 needed - unlike register 302.
        """
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        # Register 301: VMC only accepts integer values 8-29 (no *10 format)
        temp_value = round(temperature)

        _LOGGER.info(
            "Writing supply_temp_min_cool: %.1f°C -> raw value: %d",
            temperature,
            temp_value,
        )

        try:
            response = await self._client.write_register(
                address=MaicoWSRegisters.SUPPLY_TEMP_MIN_COOL,
                value=temp_value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error writing supply temp min cool %f: %s", temperature, response
                )
                return False

            _LOGGER.info("Supply temp min cool successfully set to: %f", temperature)
            return True

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error writing supply temp min cool %f: %s", temperature, e
            )
            return False
        except Exception as e:
            _LOGGER.exception(
                "Error writing supply temp min cool %f: %s", temperature, e
            )
            return False

    async def read_room_temp_max(self) -> float | None:
        """Read max room temperature (°C * 10)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.ROOM_TEMP_MAX,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading max room temperature: %s", response)
                return None

            raw_value = response.registers[0]
            if raw_value > 32767:
                raw_value -= 65536
            return raw_value / 10.0  # Convert from 0.1°C to °C

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading max room temperature: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading max room temperature: %s", e)
            return None

    async def write_room_temp_max(self, temperature: float) -> bool:
        """Write max room temperature (°C * 10)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        # Convert temperature to 0.1°C units
        temp_value = int(temperature * 10)

        try:
            response = await self._client.write_register(
                address=MaicoWSRegisters.ROOM_TEMP_MAX,
                value=temp_value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error writing max room temperature %f: %s", temperature, response
                )
                return False

            _LOGGER.debug("Max room temperature set to: %f", temperature)
            return True

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error writing max room temperature %f: %s", temperature, e
            )
            return False
        except Exception as e:
            _LOGGER.exception(
                "Error writing max room temperature %f: %s", temperature, e
            )
            return False

    async def write_supply_air_temperature(self, temperature: float) -> bool:
        """Write target room temperature (°C * 10) - Register 553 TARGET_ROOM_TEMP."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        # Convert temperature to 0.1°C units
        temp_value = int(temperature * 10)

        try:
            response = await self._client.write_register(
                address=MaicoWSRegisters.TARGET_ROOM_TEMP,
                value=temp_value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error writing target room temperature %f: %s",
                    temperature,
                    response,
                )
                return False

            _LOGGER.debug("Target room temperature set to: %f", temperature)
            return True

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error writing target room temperature %f: %s", temperature, e
            )
            return False
        except Exception as e:
            _LOGGER.exception(
                "Error writing target room temperature %f: %s", temperature, e
            )
            return False

    async def write_operation_mode(self, mode: int) -> bool:
        """Write operation mode (0=Off, 1=Manual, 2=Auto-Time, 3=Auto-Sensor, 4=Eco-Supply Air, 5=Eco-Extract Air)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        if mode < 0 or mode > 5:
            _LOGGER.error("Invalid operation mode: %d. Must be between 0 and 5.", mode)
            return False

        try:
            response = await self._client.write_register(
                address=MaicoWSRegisters.OPERATION_MODE,
                value=mode,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing operation mode %d: %s", mode, response)
                return False

            _LOGGER.debug("Operation mode set to: %d", mode)
            return True

        except ModbusException as e:
            _LOGGER.exception("Modbus error writing operation mode %d: %s", mode, e)
            return False
        except Exception as e:
            _LOGGER.exception("Error writing operation mode %d: %s", mode, e)
            return False

    async def read_current_supply_volume_flow(self) -> int | None:
        """Read current supply volume flow."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.SUPPLY_VOLUME_FLOW,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading current supply volume flow: %s", response)
                return None

            response.registers[0]
            return flow

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading current supply volume flow: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading current supply volume flow: %s", e)
            return None

    async def read_current_extract_volume_flow(self) -> int | None:
        """Read current extract volume flow."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.EXTRACT_VOLUME_FLOW,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading current extract volume flow: %s", response)
                return None

            response.registers[0]
            return flow

        except ModbusException as e:
            _LOGGER.exception("Modbus error reading current extract volume flow: %s", e)
            return None
        except Exception as e:
            _LOGGER.exception("Error reading current extract volume flow: %s", e)
            return None

    async def write_power_state(self, state: bool) -> bool:
        """Write power state to the VMC (sets operation mode to off or manual)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            # Set operation mode: 0=Off, 1=Manual (when turning on)
            mode_value = 1 if state else 0
            response = await self._client.write_register(
                address=MaicoWSRegisters.OPERATION_MODE,
                value=mode_value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing power state: %s", response)
                return False

            _LOGGER.debug("Power state set to: %s (mode=%d)", state, mode_value)
            return True

        except ModbusException as e:
            _LOGGER.exception("Modbus error writing power state: %s", e)
            return False
        except Exception as e:
            _LOGGER.exception("Error writing power state: %s", e)
            return False

    async def write_ventilation_level(self, level: int) -> bool:
        """Write ventilation level (0-4) to the VMC."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        if level < 0 or level > 4:
            _LOGGER.error(
                "Invalid ventilation level: %d. Must be between 0 and 4.", level
            )
            return False

        try:
            response = await self._client.write_register(
                address=MaicoWSRegisters.VENTILATION_LEVEL,
                value=level,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing ventilation level %d: %s", level, response)
                return False

            _LOGGER.debug("Ventilation level set to: %d", level)
            return True

        except ModbusException as e:
            _LOGGER.exception("Modbus error writing ventilation level %d: %s", level, e)
            return False
        except Exception as e:
            _LOGGER.exception("Error writing ventilation level %d: %s", level, e)
            return False

    async def write_supply_air_temperature(self, temperature: float) -> bool:
        """Write supply air temperature setpoint."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        # Convert temperature to 0.1°C units
        temp_value = int(temperature * 10)

        try:
            response = await self._client.write_register(
                address=MaicoWSRegisters.TARGET_ROOM_TEMP,
                value=temp_value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error writing supply air temperature %f: %s", temperature, response
                )
                return False

            _LOGGER.debug("Supply air temperature set to: %f", temperature)
            return True

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error writing supply air temperature %f: %s", temperature, e
            )
            return False
        except Exception as e:
            _LOGGER.exception(
                "Error writing supply air temperature %f: %s", temperature, e
            )
            return False

    async def read_holding_registers_block(
        self, start_address: int, count: int
    ) -> list[int] | None:
        """Read a block of holding registers."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=start_address,
                count=count,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error(
                    "Error reading block starting at %d: %s", start_address, response
                )
                return None

            return response.registers

        except ModbusException as e:
            _LOGGER.exception(
                "Modbus error reading block starting at %d: %s", start_address, e
            )
            return None
        except Exception as e:
            _LOGGER.exception(
                "Error reading block starting at %d: %s", start_address, e
            )
            return None

    async def get_all_status(self) -> dict[str, Any] | None:
        """Read all status data from the device using parallel block reads for optimal performance."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        # Execute all Modbus reads in parallel for maximum performance
        # This reduces total request time from ~900ms (sequential) to ~150ms (parallel)
        results = await asyncio.gather(
            self.read_holding_registers_block(300, 3),  # Settings
            self.read_holding_registers_block(650, 8),  # Ventilation/Fans
            self.read_holding_registers_block(700, 7),  # Temperatures
            self.read_holding_registers_block(750, 1),  # Humidity
            self.read_holding_registers_block(550, 5),  # Operation Mode
            self.read_holding_registers_block(800, 4),  # Switch States
            self.read_holding_registers_block(401, 4),  # Faults/Info
            self.read_power_state(),  # Power State (coil)
            return_exceptions=True,
        )

        # Unpack results
        (
            settings_block,
            vent_block,
            temp_block,
            hum_block,
            op_block,
            switch_block,
            fault_block,
            power_state,
        ) = results

        # Check for exceptions in parallel reads
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                _LOGGER.warning("Error in parallel read %d: %s", i, result)

        status: dict[str, Any] = {}

        # Helper functions for data conversion (defined once, reused throughout)
        def to_signed(raw: int) -> float:
            """Convert unsigned 16-bit to signed integer."""
            return float(raw if raw <= 32767 else raw - 65536)

        def to_temp(raw: int) -> float:
            """Convert signed 16-bit to temperature (divide by 10)."""
            val = raw if raw <= 32767 else raw - 65536
            return val / 10.0

        # 1. Process Settings Block (300-302)
        if settings_block and not isinstance(settings_block, Exception):
            _LOGGER.info("Settings block raw values: %s", settings_block)
            status["room_temp_adjust"] = to_signed(settings_block[0])
            # Register 301: Value stored directly in °C (min=8, max=29 per documentation)
            # NO division by 10 needed - unlike register 302
            raw_301 = settings_block[1]
            signed_301 = raw_301 if raw_301 <= 32767 else raw_301 - 65536
            status["supply_temp_min_cool"] = float(signed_301)
            _LOGGER.info(
                "supply_temp_min_cool: raw=%d, result=%.1f",
                raw_301,
                status["supply_temp_min_cool"],
            )
            # Register 302: Temperature * 10 format (min=180=18°C, max=300=30°C)
            status["room_temp_max"] = to_temp(settings_block[2])

        # 2. Process Ventilation/Fan Status Block (650-657)
        if vent_block and not isinstance(vent_block, Exception):
            status["current_ventilation_level"] = vent_block[0]
            status["supply_fan_speed"] = vent_block[1]
            status["extract_fan_speed"] = vent_block[2]
            status["current_supply_volume_flow"] = vent_block[3]
            status["current_extract_volume_flow"] = vent_block[4]
            status["filter_status"] = {
                "filter_device_days": vent_block[5],
                "filter_outdoor_days": vent_block[6],
                "filter_room_days": vent_block[7],
            }

        # 3. Process Temperatures Block (700-706)
        if temp_block and not isinstance(temp_block, Exception):
            status["room_temperature"] = to_temp(temp_block[0])
            status["inlet_air_temperature"] = to_temp(temp_block[3])
            status["supply_air_temperature"] = to_temp(temp_block[4])
            status["extract_air_temperature"] = to_temp(temp_block[5])
            status["exhaust_air_temperature"] = to_temp(temp_block[6])

        # 4. Process Humidity Block (750)
        if hum_block and not isinstance(hum_block, Exception):
            status["extract_air_humidity"] = hum_block[0]

        # 5. Process Operation Mode Block (550-554)
        if op_block and not isinstance(op_block, Exception):
            mode_map = {
                0: "off",
                1: "manual",
                2: "auto_time",
                3: "auto_sensor",
                4: "eco_supply",
                5: "eco_extract",
            }
            status["operation_mode"] = mode_map.get(
                op_block[0], f"unknown_{op_block[0]}"
            )
            season_map = {0: "winter", 1: "summer"}
            status["season"] = season_map.get(op_block[2], f"unknown_{op_block[2]}")
            status["target_temperature"] = to_temp(op_block[3])

        # 6. Process Switch States Block (800-803)
        if switch_block and not isinstance(switch_block, Exception):
            status["supply_fan_state"] = bool(switch_block[0])
            status["extract_fan_state"] = bool(switch_block[1])
            status["bypass_status"] = bool(switch_block[2])

        # 7. Process Faults/Info Block (401-404)
        if fault_block and not isinstance(fault_block, Exception):
            err_hi, err_lo, info_hi, info_lo = fault_block
            status["fault_status"] = (
                "no_fault"
                if (err_hi == 0 and err_lo == 0)
                else f"error_hi_{err_hi}_lo_{err_lo}"
            )
            status["info_messages"] = (
                "no_info"
                if (info_hi == 0 and info_lo == 0)
                else f"info_hi_{info_hi}_lo_{info_lo}"
            )

        # 8. Process Power State
        if power_state and not isinstance(power_state, Exception):
            status["power_state"] = power_state

        return status

    @property
    def connected(self) -> bool:
        """Return connection status."""
        return self._connected


# Backward compatibility alias
MaicoWS320B = MaicoWS
MaicoWS320BRegisters = MaicoWSRegisters
