"""Maico WS sensor reading methods."""

from __future__ import annotations

import logging

from .registers import MaicoWSRegisters

_LOGGER = logging.getLogger(__name__)


class SensorsMixin:
    """Mixin providing sensor reading methods for MaicoWS."""

    # These will be provided by the base class
    _connected: bool
    _slave_id: int

    async def read_holding_register(self, register: int) -> int | None:
        """Read a single holding register (from base class)."""

    @staticmethod
    def to_temp(raw: int) -> float:
        """Convert raw to temperature (from base class)."""

    @staticmethod
    def to_signed(value: int) -> int:
        """Convert to signed (from base class)."""

    async def read_temperature(self, register: int) -> float | None:
        """Read temperature from register (values in 0.1°C)."""
        value = await self.read_holding_register(register)
        if value is None:
            return None
        return self.to_temp(value)

    async def read_humidity(self, register: int) -> float | None:
        """Read humidity from register (values in 0.1%)."""
        value = await self.read_holding_register(register)
        if value is None:
            return None
        return value / 10.0

    async def read_room_temperature(self) -> float | None:
        """Read room temperature."""
        return await self.read_temperature(MaicoWSRegisters.ROOM_TEMP)

    async def read_room_temperature_external(self) -> float | None:
        """Read external room temperature sensor."""
        return await self.read_temperature(MaicoWSRegisters.ROOM_TEMP_EXT)

    async def read_supply_air_temperature(self) -> float | None:
        """Read supply air temperature."""
        return await self.read_temperature(MaicoWSRegisters.SUPPLY_AIR_TEMP)

    async def read_extract_air_temperature(self) -> float | None:
        """Read extract air temperature."""
        return await self.read_temperature(MaicoWSRegisters.EXTRACT_AIR_TEMP)

    async def read_inlet_air_temperature(self) -> float | None:
        """Read inlet air temperature."""
        return await self.read_temperature(MaicoWSRegisters.INLET_AIR_TEMP)

    async def read_exhaust_air_temperature(self) -> float | None:
        """Read exhaust air temperature."""
        return await self.read_temperature(MaicoWSRegisters.EXHAUST_AIR_TEMP)

    async def read_extract_air_humidity(self) -> float | None:
        """Read extract air humidity."""
        return await self.read_humidity(MaicoWSRegisters.EXTRACT_AIR_HUMIDITY)

    async def read_current_ventilation_level(self) -> int | None:
        """Read current ventilation level (0-4)."""
        return await self.read_holding_register(
            MaicoWSRegisters.CURRENT_VENTILATION_LEVEL
        )

    async def read_supply_fan_speed(self) -> int | None:
        """Read supply fan speed (RPM)."""
        return await self.read_holding_register(MaicoWSRegisters.SUPPLY_FAN_SPEED)

    async def read_extract_fan_speed(self) -> int | None:
        """Read extract fan speed (RPM)."""
        return await self.read_holding_register(MaicoWSRegisters.EXTRACT_FAN_SPEED)

    async def read_supply_volume_flow(self) -> int | None:
        """Read supply volume flow (m³/h)."""
        return await self.read_holding_register(MaicoWSRegisters.SUPPLY_VOLUME_FLOW)

    async def read_extract_volume_flow(self) -> int | None:
        """Read extract volume flow (m³/h)."""
        return await self.read_holding_register(MaicoWSRegisters.EXTRACT_VOLUME_FLOW)

    async def read_operation_mode(self) -> int | None:
        """Read operation mode (0-5)."""
        return await self.read_holding_register(MaicoWSRegisters.OPERATION_MODE)

    async def read_season(self) -> int | None:
        """Read season setting (0=Winter, 1=Summer)."""
        return await self.read_holding_register(MaicoWSRegisters.SEASON)

    async def read_target_room_temp(self) -> float | None:
        """Read target room temperature."""
        return await self.read_temperature(MaicoWSRegisters.TARGET_ROOM_TEMP)

    async def read_bypass_status(self) -> bool | None:
        """Read bypass actuator status (0=closed, 1=open)."""
        value = await self.read_holding_register(MaicoWSRegisters.BYPASS_ACTUATOR)
        if value is None:
            return None
        return bool(value)

    async def read_supply_fan_state(self) -> bool | None:
        """Read supply fan state (0=off, 1=on)."""
        value = await self.read_holding_register(MaicoWSRegisters.SUPPLY_FAN_STATE)
        if value is None:
            return None
        return bool(value)

    async def read_extract_fan_state(self) -> bool | None:
        """Read extract fan state (0=off, 1=on)."""
        value = await self.read_holding_register(MaicoWSRegisters.EXTRACT_FAN_STATE)
        if value is None:
            return None
        return bool(value)

    async def read_ptc_heater_state(self) -> bool | None:
        """Read PTC heater state (0=off, 1=on)."""
        value = await self.read_holding_register(MaicoWSRegisters.PTC_HEATER)
        if value is None:
            return None
        return bool(value)

    async def read_boost_ventilation(self) -> bool | None:
        """Read boost ventilation status (0=inactive, 1=active)."""
        value = await self.read_holding_register(MaicoWSRegisters.BOOST_VENTILATION)
        if value is None:
            return None
        return bool(value)

    async def read_room_temp_selection(self) -> int | None:
        """Read room temperature sensor selection (0-3)."""
        return await self.read_holding_register(MaicoWSRegisters.ROOM_TEMP_SELECTION)

    async def read_filter_remaining_device(self) -> int | None:
        """Read device filter remaining days."""
        return await self.read_holding_register(MaicoWSRegisters.FILTER_REMAIN_DEVICE)

    async def read_filter_remaining_outdoor(self) -> int | None:
        """Read outdoor filter remaining days."""
        return await self.read_holding_register(MaicoWSRegisters.FILTER_REMAIN_OUTDOOR)

    async def read_filter_remaining_room(self) -> int | None:
        """Read room filter remaining days."""
        return await self.read_holding_register(MaicoWSRegisters.FILTER_REMAIN_ROOM)

    async def read_error_code(self) -> int | None:
        """Read current error code (combined high and low word)."""
        hi = await self.read_holding_register(MaicoWSRegisters.CURRENT_ERROR_HI)
        lo = await self.read_holding_register(MaicoWSRegisters.CURRENT_ERROR_LO)
        if hi is None or lo is None:
            return None
        return (hi << 16) | lo

    async def read_info_code(self) -> int | None:
        """Read current info code (combined high and low word)."""
        hi = await self.read_holding_register(MaicoWSRegisters.CURRENT_INFO_HI)
        lo = await self.read_holding_register(MaicoWSRegisters.CURRENT_INFO_LO)
        if hi is None or lo is None:
            return None
        return (hi << 16) | lo
