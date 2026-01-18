"""Maico WS API to handle Modbus communication."""

from __future__ import annotations

import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException

_LOGGER = logging.getLogger(__name__)


# Maico WS Modbus register definitions
# Based on official documentation for RTU/TCP
class MaicoWSRegisters:
    """Register addresses for Maico WS VMC based on official documentation."""

    # Date/Time Settings
    DATE_YEAR = 100  # Year
    DATE_MONTH = 101  # Month
    DATE_DAY = 102  # Day
    TIME_HOUR = 103  # Hour
    TIME_MINUTE = 104  # Minute
    TIME_SECOND = 105  # Second

    # Filter Settings
    FILTER_DEVICE_MONTHS = 150  # Filter lifespan device filter (3-12 months)
    FILTER_OUTDOOR_MONTHS = 151  # Filter lifespan outdoor filter (3-18 months)
    FILTER_ROOM_MONTHS = 152  # Filter lifespan room filter (1-6 months)
    FILTER_DURATION = 153  # Ventilation level duration (Min)
    VOLUME_FLOW_REDUCED = 154  # Volume flow reduced ventilation
    VOLUME_FLOW_NORMAL = 155  # Volume flow nominal ventilation
    VOLUME_FLOW_INTENSIVE = 156  # Volume flow intensive ventilation
    FILTER_CHANGE_DEVICE = 157  # Filter change device filter (0=not changed, 1=changed)
    FILTER_CHANGE_OUTDOOR = (
        158  # Filter change outdoor filter (0=not changed, 1=changed)
    )
    FILTER_CHANGE_ROOM = 159  # Filter change room filter (0=not changed, 1=changed)

    # Temperature Settings
    ROOM_TEMP_ADJUST = 300  # Room temperature adjustment
    SUPPLY_TEMP_MIN_COOL = 301  # Supply temp min. cooling
    ROOM_TEMP_MAX = 302  # Room temp max.

    # Error and Info Messages
    CURRENT_ERROR_HI = 401  # Current error (High-Word)
    CURRENT_ERROR_LO = 402  # Current error (Low-Word)
    CURRENT_INFO_HI = 403  # Current info (High-Word)
    CURRENT_INFO_LO = 404  # Current info (Low-Word)
    ERROR_RESET = 405  # Error reset (0=normal, 1=reset)

    # Basic Settings
    # Operation mode: 0=Off, 1=Manual, 2=Auto-Time, 3=Auto-Sensor,
    # 4=Eco-Supply Air, 5=Eco-Extract Air
    OPERATION_MODE = 550
    BOOST_VENTILATION = 551  # Boost ventilation (0=inactive, 1=active)
    SEASON = 552  # Season (0=Winter, 1=Summer)
    TARGET_ROOM_TEMP = 553  # Target room temperature (°C * 10)
    # Ventilation level: 0=Off, 1=Humidity protection, 2=Reduced,
    # 3=Nominal, 4=Intensive
    VENTILATION_LEVEL = 554

    # Ventilation Queries
    # Current level: 0=Off, 1=Humidity prot, 2=Reduced, 3=Nominal, 4=Intensive
    CURRENT_VENTILATION_LEVEL = 650
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

    # CO2 Sensors (already managed in block read 750+)
    # Registers 755-758

    # VOC Sensors
    VOC_SENSOR_1 = 759  # VOC sensor 1 (ppm * 10)
    VOC_SENSOR_2 = 760  # VOC sensor 2 (ppm * 10)
    VOC_SENSOR_3 = 761  # VOC sensor 3 (ppm * 10)
    VOC_SENSOR_4 = 762  # VOC sensor 4 (ppm * 10)

    # Switch States
    SUPPLY_FAN_STATE = 800  # Supply fan state (0=off, 1=on)
    EXTRACT_FAN_STATE = 801  # Extract fan state (0=off, 1=on)
    BYPASS_ACTUATOR = 802  # Summer bypass actuator (0=closed, 1=open)
    PTC_HEATER = 803  # PTC heater (0=off, 1=on)

    # Operating Hours
    HOURS_HUMIDITY_HI = 850
    HOURS_HUMIDITY_LO = 851
    HOURS_REDUCED_HI = 852
    HOURS_REDUCED_LO = 853
    HOURS_NOMINAL_HI = 854
    HOURS_NOMINAL_LO = 855
    HOURS_INTENSIVE_HI = 856
    HOURS_INTENSIVE_LO = 857
    HOURS_TOTAL_HI = 858
    HOURS_TOTAL_LO = 859

    # Constants
    MAX_INT_16BIT = 32767
    VENTILATION_LEVEL_MIN = 0
    VENTILATION_LEVEL_MAX = 4


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
                    name="maicows",
                )
                _LOGGER.debug(
                    "Connecting to Maico WS via TCP: %s:%d",
                    self._host,
                    self._port,
                )

            # Connect returns True if success
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
            if raw_value > MaicoWSRegisters.MAX_INT_16BIT:
                raw_value -= 65536
            # Temperature values are stored in 0.1°C increments
            return raw_value / 10.0

        except ModbusException:
            _LOGGER.exception("Modbus error reading temperature register %d", register)
            return None
        except Exception:
            _LOGGER.exception("Error reading temperature register %d", register)
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

        except ModbusException:
            _LOGGER.exception("Modbus error reading humidity register %d", register)
            return None
        except Exception:
            _LOGGER.exception("Error reading humidity register %d", register)
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

        except ModbusException:
            _LOGGER.exception("Modbus error reading fan speed register %d", register)
            return None
        except Exception:
            _LOGGER.exception("Error reading fan speed register %d", register)
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

            return response.registers[0]

        except ModbusException:
            _LOGGER.exception("Modbus error reading current ventilation level")
            return None
        except Exception:
            _LOGGER.exception("Error reading current ventilation level")
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

    # Note: Fan speed might not be directly available, documentation is unclear.
    # Using 558/559 based on similar models, needs verification.
    async def read_current_supply_fan_speed(self) -> int | None:
        """Read current supply fan speed (rpm)."""
        if not self._connected:
            return None

        try:
            # Register 558 might be supply fan speed
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.SUPPLY_FAN_SPEED,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                return None

            return response.registers[0]

        except ModbusException:
            # Low severity, might not be supported
            return None
        except Exception:  # noqa: BLE001
            # Low severity, might not be supported
            return None

    async def read_current_extract_fan_speed(self) -> int | None:
        """Read current extract fan speed (rpm)."""
        if not self._connected:
            return None

        try:
            # Register 559 might be extract fan speed
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.EXTRACT_FAN_SPEED,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                return None

            return response.registers[0]

        except ModbusException:
            # Low severity, might not be supported
            return None
        except Exception:  # noqa: BLE001
            # Low severity, might not be supported
            return None

    async def read_power_state(self) -> bool | None:
        """Read power state (derived from operation mode)."""
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

        except ModbusException:
            _LOGGER.exception("Modbus error reading power state")
            return None
        except Exception:
            _LOGGER.exception("Error reading power state")
            return None
        else:
            # Operation mode 0 = Off, any other value = On
            operation_mode = response.registers[0]
            return operation_mode != 0

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
                status["device_filter_days"] = device_filter_days.registers[0]

            if outdoor_filter_days and not outdoor_filter_days.isError():
                status["outdoor_filter_days"] = outdoor_filter_days.registers[0]

            if room_filter_days and not room_filter_days.isError():
                status["room_filter_days"] = room_filter_days.registers[0]

        except ModbusException:
            _LOGGER.exception("Modbus error reading filter replacement days")
            return None
        except Exception:
            _LOGGER.exception("Error reading filter replacement days")
            return None
        else:
            return status

    async def read_fault_status(self) -> str | None:
        """Read fault status from high and low word registers."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            # Fault Status High Word
            fault_hi = await self._client.read_holding_registers(
                address=MaicoWSRegisters.FAULT_STATUS_HI,
                count=1,
                device_id=self._slave_id,
            )
            # Fault Status Low Word
            fault_lo = await self._client.read_holding_registers(
                address=MaicoWSRegisters.FAULT_STATUS_LO,
                count=1,
                device_id=self._slave_id,
            )

            if (
                fault_hi
                and not fault_hi.isError()
                and fault_lo
                and not fault_lo.isError()
            ):
                error_hi = fault_hi.registers[0]
                error_lo = fault_lo.registers[0]

        except ModbusException:
            _LOGGER.exception("Modbus error reading fault status")
            return None
        except Exception:
            _LOGGER.exception("Error reading fault status")
            return None
        else:
            if error_hi == 0 and error_lo == 0:
                return "no_fault"
            # Return combined error code
            return f"error_hi_{error_hi}_lo_{error_lo}"

    async def read_info_messages(self) -> str | None:
        """Read info messages from high and low word registers."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            # Info Message High Word
            info_hi_reg = await self._client.read_holding_registers(
                address=MaicoWSRegisters.INFO_MESSAGE_HI,
                count=1,
                device_id=self._slave_id,
            )
            # Info Message Low Word
            info_lo_reg = await self._client.read_holding_registers(
                address=MaicoWSRegisters.INFO_MESSAGE_LO,
                count=1,
                device_id=self._slave_id,
            )

            if (
                info_hi_reg
                and not info_hi_reg.isError()
                and info_lo_reg
                and not info_lo_reg.isError()
            ):
                info_hi = info_hi_reg.registers[0]
                info_lo = info_lo_reg.registers[0]

        except ModbusException:
            _LOGGER.exception("Modbus error reading info messages")
            return None
        except Exception:
            _LOGGER.exception("Error reading info messages")
            return None
        else:
            if info_hi == 0 and info_lo == 0:
                return "no_info"
            # Return combined info code
            return f"info_hi_{info_hi}_lo_{info_lo}"

    async def read_operation_mode(self) -> str | None:
        """Read current operation mode."""
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

            mode_code = response.registers[0]

            # Map mode codes to human-readable strings based on documentation
            # 0=Off, 1=Manual, 2=Auto-Time, 3=Auto-Sensor, 4=Eco-Supply, 5=Eco-Extract
            mode_map = {
                0: "off",
                1: "manual",
                2: "auto_time",
                3: "auto_sensor",
                4: "eco_supply",
                5: "eco_extract",
            }

            return mode_map.get(mode_code, f"unknown_{mode_code}")

        except Exception:
            _LOGGER.exception("Error reading operation mode")
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

            status = response.registers[0]
            # 0=closed, 1=open
            return bool(status)

        except ModbusException:
            _LOGGER.exception("Modbus error reading bypass status")
            return None
        except Exception:
            _LOGGER.exception("Error reading bypass status")
            return None

    async def read_frost_protection_status(self) -> bool | None:
        """Read frost protection status (True=Active/Open, False=Inactive/Closed)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        try:
            response = await self._client.read_holding_registers(
                address=MaicoWSRegisters.FROST_PROTECTION_STATUS,
                count=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error reading frost protection status: %s", response)
                return None

            status = response.registers[0]
            # 0=inactive, 1=active
            return bool(status)

        except ModbusException:
            _LOGGER.exception("Modbus error reading frost protection status")
            return None
        except Exception:
            _LOGGER.exception("Error reading frost protection status")
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

            state = response.registers[0]
            # 0=off, 1=on
            return bool(state)

        except ModbusException:
            _LOGGER.exception("Modbus error reading supply fan state")
            return None
        except Exception:
            _LOGGER.exception("Error reading supply fan state")
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

            state = response.registers[0]
            # 0=off, 1=on
            return bool(state)

        except ModbusException:
            _LOGGER.exception("Modbus error reading extract fan state")
            return None
        except Exception:
            _LOGGER.exception("Error reading extract fan state")
            return None

    async def read_season(self) -> str | None:  # noqa: PLR0911
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
        except ModbusException:
            _LOGGER.exception("Modbus error reading season setting")
            return None
        except Exception:
            _LOGGER.exception("Error reading season setting")
            return None
        else:
            if raw_value == 0:
                return "winter"
            if raw_value == 1:
                return "summer"
            return f"unknown_{raw_value}"

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
            _LOGGER.debug(
                "Writing season: %d (%s)",
                season,
                "Summer" if season == 1 else "Winter",
            )

            response = await self._client.write_register(
                address=MaicoWSRegisters.SEASON,
                value=season,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing season %d: %s", season, response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error writing season %d", season)
            return False
        except Exception:
            _LOGGER.exception("Error writing season %d", season)
            return False
        else:
            _LOGGER.debug("Season set to: %s", "Summer" if season == 1 else "Winter")
            return True

    async def write_filter_change_device(self, *, changed: bool) -> bool:
        """Write device filter change status (0=not changed, 1=changed)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            # 880 is Device Filter Change
            value = 1 if changed else 0
            _LOGGER.debug(
                "Writing device filter change status: %s (val: %d)", changed, value
            )

            response = await self._client.write_register(
                address=MaicoWSRegisters.FILTER_CHANGE_DEVICE,
                value=value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing device filter change status: %s", response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error writing device filter change status")
            return False
        except Exception:
            _LOGGER.exception("Error writing device filter change status")
            return False
        else:
            _LOGGER.debug("Device filter change status set to: %s", changed)
            return True

    async def write_filter_change_outdoor(self, *, changed: bool) -> bool:
        """Write outdoor filter change status (0=not changed, 1=changed)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            # 881 is Outdoor Filter Change
            value = 1 if changed else 0
            _LOGGER.debug(
                "Writing outdoor filter change status: %s (val: %d)", changed, value
            )

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

        except ModbusException:
            _LOGGER.exception("Modbus error writing outdoor filter change status")
            return False
        except Exception:
            _LOGGER.exception("Error writing outdoor filter change status")
            return False
        else:
            _LOGGER.debug("Outdoor filter change status set to: %s", changed)
            return True

    async def write_filter_change_room(self, *, changed: bool) -> bool:
        """Write room filter change status (0=not changed, 1=changed)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            # 882 is Room Filter Change
            value = 1 if changed else 0
            _LOGGER.debug(
                "Writing room filter change status: %s (val: %d)", changed, value
            )

            response = await self._client.write_register(
                address=MaicoWSRegisters.FILTER_CHANGE_ROOM,
                value=value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing room filter change status: %s", response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error writing room filter change status")
            return False
        except Exception:
            _LOGGER.exception("Error writing room filter change status")
            return False
        else:
            _LOGGER.debug("Room filter change status set to: %s", changed)
            return True

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

        except ModbusException:
            _LOGGER.exception("Modbus error writing supply temp min cool")
            return False
        except Exception:
            _LOGGER.exception("Error writing supply temp min cool")
            return False
        else:
            _LOGGER.info("Supply temp min cool successfully set to: %f", temperature)
            return True

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

            # Convert unsigned 16-bit to signed 16-bit
            raw_value = response.registers[0]
            if raw_value > MaicoWSRegisters.MAX_INT_16BIT:
                raw_value -= 65536
            return raw_value / 10.0  # Convert from 0.1°C to °C

        except ModbusException:
            _LOGGER.exception("Modbus error reading max room temperature: %s")
            return None
        except Exception:
            _LOGGER.exception("Error reading max room temperature: %s")
            return None

    async def write_max_room_temperature(self, temperature: float) -> bool:
        """Write max room temperature setpoint."""
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

        except ModbusException:
            _LOGGER.exception(
                "Modbus error writing max room temperature %f", temperature
            )
            return False
        except Exception:
            _LOGGER.exception("Error writing max room temperature %f", temperature)
            return False
        else:
            return True

    async def write_target_room_temperature(self, temperature: float) -> bool:
        """Write target room temperature setpoint."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        # Convert temperature to 0.1°C units
        temp_value = int(temperature * 10)

        try:
            _LOGGER.debug("Target room temperature set to: %f", temperature)
            response = await self._client.write_register(
                address=MaicoWSRegisters.ROOM_TEMP_ADJUST,
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

        except ModbusException:
            _LOGGER.exception(
                "Modbus error writing target room temperature %f", temperature
            )
            return False
        except Exception:
            _LOGGER.exception("Error writing target room temperature %f", temperature)
            return False
        else:
            return True

    async def write_operation_mode(self, mode: int) -> bool:
        """Write operation mode (0-5)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        if mode < 0 or mode > 5:  # noqa: PLR2004
            _LOGGER.error("Invalid operation mode: %d. Must be between 0 and 5.", mode)
            return False

        try:
            _LOGGER.debug(
                "Writing operation mode: %d to register %s",
                mode,
                MaicoWSRegisters.OPERATION_MODE,
            )

            response = await self._client.write_register(
                address=MaicoWSRegisters.OPERATION_MODE,
                value=mode,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing operation mode %d: %s", mode, response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error writing operation mode %d", mode)
            return False
        except Exception:
            _LOGGER.exception("Error writing operation mode %d", mode)
            return False
        else:
            _LOGGER.debug("Operation mode set to: %d", mode)
            return True

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

            return response.registers[0]

        except ModbusException:
            _LOGGER.exception("Modbus error reading current supply volume flow")
            return None
        except Exception:
            _LOGGER.exception("Error reading current supply volume flow")
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

            return response.registers[0]

        except ModbusException:
            _LOGGER.exception("Modbus error reading current extract volume flow")
            return None

    async def write_power_state(self, *, state: bool) -> bool:
        """Write power state to the VMC (sets operation mode to off or manual)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            # Power on = Manual (1), Power off = Off (0)
            mode_value = 1 if state else 0
            _LOGGER.debug("Writing power state: %s (mode=%d)", state, mode_value)

            response = await self._client.write_register(
                address=MaicoWSRegisters.OPERATION_MODE,
                value=mode_value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing power state: %s", response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error writing power state")
            return False
        except Exception:
            _LOGGER.exception("Error writing power state")
            return False
        else:
            _LOGGER.debug("Power state set to: %s (mode=%d)", state, mode_value)
            return True

    async def write_ventilation_level(self, level: int) -> bool:
        """Write ventilation level (0-4)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        if (
            level < MaicoWSRegisters.VENTILATION_LEVEL_MIN
            or level > MaicoWSRegisters.VENTILATION_LEVEL_MAX
        ):
            _LOGGER.error(
                "Invalid ventilation level: %d. Must be between %d and %d.",
                level,
                MaicoWSRegisters.VENTILATION_LEVEL_MIN,
                MaicoWSRegisters.VENTILATION_LEVEL_MAX,
            )
            return False

        try:
            # Register 554 is ventilation level
            _LOGGER.debug(
                "Writing ventilation level: %d to register %s",
                level,
                MaicoWSRegisters.VENTILATION_LEVEL,
            )

            response = await self._client.write_register(
                address=MaicoWSRegisters.VENTILATION_LEVEL,
                value=level,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing ventilation level %d: %s", level, response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error writing ventilation level %d", level)
            return False
        except Exception:
            _LOGGER.exception("Error writing ventilation level %d", level)
            return False
        else:
            _LOGGER.debug("Ventilation level set to: %d", level)
            return True

    async def write_boost_ventilation(self, *, state: bool) -> bool:
        """Write boost ventilation status."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            # Register 551 is 1 for Boost/Intensive, 0 for off
            value = 1 if state else 0
            _LOGGER.debug("Writing boost ventilation: %s (val: %d)", state, value)
            response = await self._client.write_register(
                address=MaicoWSRegisters.BOOST_VENTILATION,
                value=value,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error writing boost ventilation: %s", response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error writing boost ventilation %s", state)
            return False
        except Exception:
            _LOGGER.exception("Error writing boost ventilation %s", state)
            return False
        else:
            _LOGGER.debug("Boost ventilation set to: %s", state)
            return True

    async def trigger_error_reset(self) -> bool:
        """Trigger error reset (write 1 to register 405)."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            response = await self._client.write_register(
                address=MaicoWSRegisters.ERROR_RESET,
                value=1,
                device_id=self._slave_id,
            )

            if response.isError():
                _LOGGER.error("Error triggering error reset: %s", response)
                return False

        except ModbusException:
            _LOGGER.exception("Modbus error triggering error reset")
            return False
        except Exception:
            _LOGGER.exception("Error triggering error reset")
            return False
        else:
            return True

    async def write_register_value(self, register: int, value: int) -> bool:
        """Write a specific value to a holding register."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return False

        try:
            _LOGGER.debug("Writing register %d: %d", register, value)
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
            return True

    async def read_holding_registers_block(
        self, start_address: int, count: int
    ) -> list[int] | None:
        """Read a block of holding registers."""
        if not self._connected:
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

        except ModbusException:
            _LOGGER.exception(
                "Modbus error reading block starting at %d", start_address
            )
            return None
        except Exception:
            _LOGGER.exception("Error reading block starting at %d", start_address)
            return None
        else:
            return response.registers

    def _process_status_results(self, results: tuple) -> dict[str, Any]:  # noqa: PLR0915, PLR0912
        """Process the results from the parallel Modbus reads."""
        (
            settings_block,
            vent_block,
            temp_block,
            hum_block,
            op_block,
            switch_block,
            fault_block,
            filter_flow_block,
            hours_block,
            power_state,
        ) = results

        status: dict[str, Any] = {}

        # Constants
        temp_threshold = 32767
        temp_subtract = 65536
        temp_divisor = 10.0

        # Helper functions
        def to_signed(raw: int) -> float:
            """Convert unsigned 16-bit to signed integer."""
            return float(raw if raw <= temp_threshold else raw - temp_subtract)

        def to_temp(raw: int) -> float:
            """Convert signed 16-bit to temperature (divide by 10)."""
            val = raw if raw <= temp_threshold else raw - temp_subtract
            return val / temp_divisor

        def combine(hi: int, lo: int) -> int:
            """Combine high and low words."""
            return (hi << 16) | lo

        # 1. Process Settings Block (300-302)
        if settings_block and not isinstance(settings_block, Exception):
            status["room_temp_adjust"] = to_signed(settings_block[0])
            raw_301 = settings_block[1]
            signed_301 = (
                raw_301 if raw_301 <= temp_threshold else raw_301 - temp_subtract
            )
            status["supply_temp_min_cool"] = float(signed_301)
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

        # 4. Process Humidity and CO2 Block (750-759)
        if hum_block and not isinstance(hum_block, Exception):
            # Humidity (750-754) - User reported no division needed
            status["extract_air_humidity"] = hum_block[0]
            # Additional humidity sensors if available
            if len(hum_block) > 1:
                status["humidity_sensor_1"] = hum_block[1]
                status["humidity_sensor_2"] = hum_block[2]
                status["humidity_sensor_3"] = hum_block[3]
                status["humidity_sensor_4"] = hum_block[4]

            # CO2 Sensors (755-758) - Spec says *10 (so divide by 10 for ppm)
            # Need to ensure block is large enough
            if len(hum_block) >= 9:  # noqa: PLR2004
                status["co2_sensor_1"] = hum_block[5] / 10.0
                status["co2_sensor_2"] = hum_block[6] / 10.0
                status["co2_sensor_3"] = hum_block[7] / 10.0
                status["co2_sensor_4"] = hum_block[8] / 10.0

            # VOC Sensors (759-762) - Spec says *10 (so divide by 10 for ppm)
            if len(hum_block) >= 13:  # noqa: PLR2004
                status["voc_sensor_1"] = hum_block[9] / 10.0
                status["voc_sensor_2"] = hum_block[10] / 10.0
                status["voc_sensor_3"] = hum_block[11] / 10.0
                status["voc_sensor_4"] = hum_block[12] / 10.0

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
            # Boost is 551 (index 1)
            status["boost_ventilation"] = bool(op_block[1])

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
        if power_state is not None and not isinstance(power_state, Exception):
            status["power_state"] = power_state

        # 9. Process Filter/Flow Settings (150-159)
        if filter_flow_block and not isinstance(filter_flow_block, Exception):
            status["filter_device_months"] = filter_flow_block[0]
            status["filter_outdoor_months"] = filter_flow_block[1]
            status["filter_room_months"] = filter_flow_block[2]
            status["filter_duration"] = filter_flow_block[3]
            status["volume_flow_reduced"] = filter_flow_block[4]
            status["volume_flow_normal"] = filter_flow_block[5]
            status["volume_flow_intensive"] = filter_flow_block[6]

        # 10. Process Operating Hours (850-859)
        if hours_block and not isinstance(hours_block, Exception):
            status["hours_humidity"] = combine(hours_block[0], hours_block[1])
            status["hours_reduced"] = combine(hours_block[2], hours_block[3])
            status["hours_nominal"] = combine(hours_block[4], hours_block[5])
            status["hours_intensive"] = combine(hours_block[6], hours_block[7])
            status["hours_total"] = combine(hours_block[8], hours_block[9])

        return status

    async def get_all_status(self) -> dict[str, Any] | None:
        """Read all status data using parallel block reads."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS320B")
            return None

        # Execute Modbus reads sequentially to avoid overwhelming the device
        # Concurrent reads (asyncio.gather) can cause connection drops
        # on some VMC controllers
        results = []
        try:
            results.append(await self.read_holding_registers_block(300, 3))  # Settings
            results.append(await self.read_holding_registers_block(650, 8))  # Vent/Fans
            results.append(await self.read_holding_registers_block(700, 7))  # Temps
            results.append(
                await self.read_holding_registers_block(750, 14)
            )  # Humidity & CO2 & VOC (Expanded to 14 registers: 750-763)
            results.append(
                await self.read_holding_registers_block(550, 5)
            )  # Mode & Boost
            results.append(await self.read_holding_registers_block(800, 4))  # Switches
            results.append(await self.read_holding_registers_block(401, 4))  # Faults
            results.append(
                await self.read_holding_registers_block(150, 10)
            )  # Filter/Flow
            results.append(await self.read_holding_registers_block(850, 10))  # Hours
            results.append(await self.read_power_state())  # Power State
        except Exception:
            # If a critical error occurs during sequential reads, log it
            _LOGGER.exception("Error during sequential status update")
            # Fill remaining with exceptions to match expected length if needed,
            # or just return None to retry later
            return None

        # Check for exceptions in parallel reads
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                _LOGGER.warning("Error in parallel read %d: %s", i, result)

        return self._process_status_results(results)

    @property
    def connected(self) -> bool:
        """Return connection status."""
        return self._connected

    # Alias for backward compatibility and integration usage
    async def read_all_registers(self) -> dict[str, Any] | None:
        """Read all registers (alias for get_all_status)."""
        return await self.get_all_status()


# Backward compatibility alias
MaicoWS320B = MaicoWS
MaicoWS320BRegisters = MaicoWSRegisters
