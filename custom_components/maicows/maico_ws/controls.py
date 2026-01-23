"""Maico WS control/write methods."""

from __future__ import annotations

import logging

from .registers import MaicoWSRegisters

_LOGGER = logging.getLogger(__name__)

# Control constants
OPERATION_MODE_MAX = 5
TARGET_TEMP_MIN = 18.0
TARGET_TEMP_MAX = 25.0
ROOM_TEMP_SEL_MAX = 3
HUMIDITY_MAX = 100
AIR_QUALITY_MAX = 5000
FILTER_DEVICE_MIN = 3
FILTER_DEVICE_MAX = 12
FILTER_OUTDOOR_MIN = 3
FILTER_OUTDOOR_MAX = 18
FILTER_ROOM_MIN = 1
FILTER_ROOM_MAX = 6


class ControlsMixin:
    """Mixin providing control/write methods for MaicoWS."""

    # These will be provided by the base class
    _connected: bool
    _slave_id: int

    # Note: write_register is inherited from MaicoWSClient base class

    async def set_operation_mode(self, mode: int) -> bool:
        """Set operation mode (0-5)."""
        if mode < 0 or mode > OPERATION_MODE_MAX:
            _LOGGER.error("Invalid operation mode: %d. Must be 0-5.", mode)
            return False

        _LOGGER.debug("Setting operation mode to: %d", mode)
        return await self.write_register(MaicoWSRegisters.OPERATION_MODE, mode)

    async def set_ventilation_level(self, level: int) -> bool:
        """Set ventilation level (0-4)."""
        if (
            level < MaicoWSRegisters.VENTILATION_LEVEL_MIN
            or level > MaicoWSRegisters.VENTILATION_LEVEL_MAX
        ):
            _LOGGER.error("Invalid ventilation level: %d. Must be 0-4.", level)
            return False

        _LOGGER.debug("Setting ventilation level to: %d", level)
        return await self.write_register(MaicoWSRegisters.VENTILATION_LEVEL, level)

    async def set_target_room_temperature(self, temp: float) -> bool:
        """Set target room temperature (18.0-25.0°C)."""
        if temp < TARGET_TEMP_MIN or temp > TARGET_TEMP_MAX:
            _LOGGER.error(
                "Invalid target temperature: %.1f. Must be 18.0-25.0°C.", temp
            )
            return False

        # Convert to raw value (°C * 10), round to 0.5°C steps
        raw_value = int(round(temp * 2) / 2 * 10)
        _LOGGER.debug("Setting target room temperature to: %.1f°C", temp)
        return await self.write_register(MaicoWSRegisters.TARGET_ROOM_TEMP, raw_value)

    async def write_supply_temp_min_cool(self, temp: float) -> bool:
        """Write minimum supply air temperature for cooling (register 301)."""
        # Register 301 stores integer values (8-29°C)
        raw_value = int(temp)
        _LOGGER.debug("Writing supply temp min cool: %d°C", raw_value)
        return await self.write_register(
            MaicoWSRegisters.SUPPLY_TEMP_MIN_COOL, raw_value
        )

    async def write_room_temp_max(self, temp: float) -> bool:
        """Write maximum room temperature (register 302)."""
        # Register 302 stores values in 0.1°C increments
        raw_value = int(temp * 10)
        _LOGGER.debug("Writing room temp max: %.1f°C", temp)
        return await self.write_register(MaicoWSRegisters.ROOM_TEMP_MAX, raw_value)

    async def set_season(self, season: int) -> bool:
        """Set season (0=Winter, 1=Summer)."""
        if season not in [0, 1]:
            _LOGGER.error("Invalid season: %d. Must be 0 or 1.", season)
            return False

        season_name = "Summer" if season == 1 else "Winter"
        _LOGGER.debug("Setting season to: %s", season_name)
        return await self.write_register(MaicoWSRegisters.SEASON, season)

    async def set_boost_ventilation(self, *, active: bool) -> bool:
        """Set boost ventilation (True=active, False=inactive)."""
        value = 1 if active else 0
        _LOGGER.debug("Setting boost to: %s", "active" if active else "inactive")
        return await self.write_register(MaicoWSRegisters.BOOST_VENTILATION, value)

    async def reset_filter_device(self) -> bool:
        """Reset device filter change indicator."""
        _LOGGER.debug("Resetting device filter indicator")
        return await self.write_register(MaicoWSRegisters.FILTER_CHANGE_DEVICE, 1)

    async def reset_filter_outdoor(self) -> bool:
        """Reset outdoor filter change indicator."""
        _LOGGER.debug("Resetting outdoor filter indicator")
        return await self.write_register(MaicoWSRegisters.FILTER_CHANGE_OUTDOOR, 1)

    async def reset_filter_room(self) -> bool:
        """Reset room filter change indicator."""
        _LOGGER.debug("Resetting room filter indicator")
        return await self.write_register(MaicoWSRegisters.FILTER_CHANGE_ROOM, 1)

    async def reset_error(self) -> bool:
        """Reset error status."""
        _LOGGER.debug("Resetting error status")
        return await self.write_register(MaicoWSRegisters.ERROR_RESET, 1)

    async def set_room_temp_selection(self, selection: int) -> bool:
        """Set room temp sensor selection (0-3)."""
        if selection < 0 or selection > ROOM_TEMP_SEL_MAX:
            _LOGGER.error("Invalid room temp selection: %d. Must be 0-3.", selection)
            return False

        _LOGGER.debug("Setting room temp selection to: %d", selection)
        return await self.write_register(
            MaicoWSRegisters.ROOM_TEMP_SELECTION, selection
        )

    async def write_external_room_temp(self, temp: float) -> bool:
        """Write external room temperature value."""
        raw_value = int(temp * 10)
        _LOGGER.debug("Writing external room temp: %.1f°C", temp)
        return await self.write_register(MaicoWSRegisters.ROOM_TEMP_EXT, raw_value)

    async def write_bus_room_temp(self, temp: float) -> bool:
        """Write bus room temperature (min cycle 10min)."""
        raw_value = int(temp * 10)
        _LOGGER.debug("Writing bus room temp: %.1f°C", temp)
        return await self.write_register(MaicoWSRegisters.ROOM_TEMP_BUS, raw_value)

    async def write_bus_humidity(self, humidity: int) -> bool:
        """Write bus humidity value (0-100% RH, min cycle 10min)."""
        if humidity < 0 or humidity > HUMIDITY_MAX:
            _LOGGER.error("Invalid humidity: %d. Must be 0-100%%.", humidity)
            return False

        _LOGGER.debug("Writing bus humidity: %d%%", humidity)
        return await self.write_register(MaicoWSRegisters.HUMIDITY_BUS, humidity)

    async def write_bus_air_quality(self, ppm: int) -> bool:
        """Write bus air quality/CO2 (0-5000 ppm, min cycle 10min)."""
        if ppm < 0 or ppm > AIR_QUALITY_MAX:
            _LOGGER.error("Invalid air quality: %d. Must be 0-5000 ppm.", ppm)
            return False

        _LOGGER.debug("Writing bus air quality: %d ppm", ppm)
        return await self.write_register(MaicoWSRegisters.AIR_QUALITY_BUS, ppm)

    async def set_filter_device_months(self, months: int) -> bool:
        """Set device filter lifespan (3-12 months)."""
        if months < FILTER_DEVICE_MIN or months > FILTER_DEVICE_MAX:
            _LOGGER.error("Invalid filter lifespan: %d. Must be 3-12.", months)
            return False

        _LOGGER.debug("Setting device filter lifespan to: %d months", months)
        return await self.write_register(MaicoWSRegisters.FILTER_DEVICE_MONTHS, months)

    async def set_filter_outdoor_months(self, months: int) -> bool:
        """Set outdoor filter lifespan (3-18 months)."""
        if months < FILTER_OUTDOOR_MIN or months > FILTER_OUTDOOR_MAX:
            _LOGGER.error("Invalid filter lifespan: %d. Must be 3-18.", months)
            return False

        _LOGGER.debug("Setting outdoor filter lifespan to: %d months", months)
        return await self.write_register(MaicoWSRegisters.FILTER_OUTDOOR_MONTHS, months)

    async def set_filter_room_months(self, months: int) -> bool:
        """Set room filter lifespan (1-6 months)."""
        if months < FILTER_ROOM_MIN or months > FILTER_ROOM_MAX:
            _LOGGER.error("Invalid filter lifespan: %d. Must be 1-6.", months)
            return False

        _LOGGER.debug("Setting room filter lifespan to: %d months", months)
        return await self.write_register(MaicoWSRegisters.FILTER_ROOM_MONTHS, months)
