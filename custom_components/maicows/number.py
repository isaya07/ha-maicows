"""Number platform for Maico WS adjustable settings."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MaicoCoordinator
from .const import DOMAIN
from .maico_ws_api import MaicoWSRegisters

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Maico WS320B number platform."""
    coordinator: MaicoCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        MaicoWS320BSupplyTempMinCoolNumber(coordinator),
        MaicoWS320BMaxRoomTempNumber(coordinator),
        MaicoRoomTempAdjustNumber(coordinator),
        # External temperature inputs
        MaicoExternalTempNumber(
            coordinator,
            "room_temp_external",
            MaicoWSRegisters.ROOM_TEMP_EXT,
            icon="mdi:home-thermometer",
        ),
        MaicoExternalTempNumber(
            coordinator,
            "room_temp_bus",
            MaicoWSRegisters.ROOM_TEMP_BUS,
            icon="mdi:thermometer-lines",
        ),
        # External humidity and air quality inputs
        MaicoBusSensorNumber(
            coordinator,
            "humidity_bus",
            MaicoWSRegisters.HUMIDITY_BUS,
            min_val=0,
            max_val=100,
            unit="%",
            icon="mdi:water-percent",
        ),
        MaicoBusSensorNumber(
            coordinator,
            "air_quality_bus",
            MaicoWSRegisters.AIR_QUALITY_BUS,
            min_val=0,
            max_val=5000,
            unit="ppm",
            icon="mdi:molecule-co2",
        ),
        # Filter settings
        MaicoWS320BConfigNumber(
            coordinator,
            "filter_device_months",
            MaicoWSRegisters.FILTER_DEVICE_MONTHS,
            3,
            12,
            unit="months",
            icon="mdi:calendar-range",
        ),
        MaicoWS320BConfigNumber(
            coordinator,
            "filter_outdoor_months",
            MaicoWSRegisters.FILTER_OUTDOOR_MONTHS,
            3,
            18,
            unit="months",
            icon="mdi:calendar-range",
        ),
        MaicoWS320BConfigNumber(
            coordinator,
            "filter_room_months",
            MaicoWSRegisters.FILTER_ROOM_MONTHS,
            1,
            6,
            unit="months",
            icon="mdi:calendar-range",
        ),
        # Volume flow settings
        MaicoWS320BConfigNumber(
            coordinator,
            "volume_flow_reduced",
            MaicoWSRegisters.VOLUME_FLOW_REDUCED,
            0,
            400,
            unit="m³/h",
            icon="mdi:weather-windy",
        ),
        MaicoWS320BConfigNumber(
            coordinator,
            "volume_flow_normal",
            MaicoWSRegisters.VOLUME_FLOW_NORMAL,
            0,
            400,
            unit="m³/h",
            icon="mdi:weather-windy",
        ),
        MaicoWS320BConfigNumber(
            coordinator,
            "volume_flow_intensive",
            MaicoWSRegisters.VOLUME_FLOW_INTENSIVE,
            0,
            400,
            unit="m³/h",
            icon="mdi:weather-windy",
        ),
    ]

    async_add_entities(entities, update_before_add=True)


class MaicoWS320BSupplyTempMinCoolNumber(
    CoordinatorEntity[MaicoCoordinator], NumberEntity
):
    """Representation of a Maico WS320B min supply air temp for cooling."""

    _attr_has_entity_name = True
    _attr_translation_key = "supply_temp_min_cool"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_supply_temp_min_cool"
        self._attr_device_info = coordinator.device_info
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_min_value = 8.0  # From documentation: 8°C
        self._attr_native_max_value = 29.0  # From documentation: 29°C
        self._attr_native_step = 1.0  # VMC register 301 only accepts integers
        self._attr_mode = NumberMode.BOX
        self._attr_icon = "mdi:thermometer-low"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get("supply_temp_min_cool")

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        success = await self._api.write_supply_temp_min_cool(value)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set min supply air temperature to %f", value)


class MaicoWS320BMaxRoomTempNumber(CoordinatorEntity[MaicoCoordinator], NumberEntity):
    """Representation of a Maico WS320B max room temperature setting."""

    _attr_has_entity_name = True
    _attr_translation_key = "room_temp_max"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_room_temp_max"
        self._attr_device_info = coordinator.device_info
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_min_value = 18.0  # From documentation: 18°C
        self._attr_native_max_value = 30.0  # From documentation: 30°C
        self._attr_native_step = 0.5
        self._attr_mode = NumberMode.BOX
        self._attr_icon = "mdi:thermometer-high"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get("room_temp_max")

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        success = await self._api.write_room_temp_max(value)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set max room temperature to %f", value)


class MaicoRoomTempAdjustNumber(CoordinatorEntity[MaicoCoordinator], NumberEntity):
    """Representation of Maico WS room temperature adjustment (register 300)."""

    _attr_has_entity_name = True
    _attr_translation_key = "room_temp_adjust"

    def __init__(self, coordinator: MaicoCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_room_temp_adjust"
        self._attr_device_info = coordinator.device_info
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_min_value = -3.0  # From documentation: -3°C
        self._attr_native_max_value = 3.0  # From documentation: +3°C
        self._attr_native_step = 0.5
        self._attr_mode = NumberMode.BOX
        self._attr_icon = "mdi:thermometer-plus"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get("room_temp_adjust")

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Register 300 stores values in 0.1°C increments
        raw_value = int(value * 10)
        success = await self._api.write_register(
            MaicoWSRegisters.ROOM_TEMP_ADJUST, raw_value
        )
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set room temp adjust to %f", value)


class MaicoWS320BConfigNumber(CoordinatorEntity[MaicoCoordinator], NumberEntity):
    """Generic number entity for Maico WS320B configuration."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(  # noqa: PLR0913
        self,
        coordinator: MaicoCoordinator,
        key: str,
        register: int,
        min_val: float,
        max_val: float,
        step: float = 1.0,
        unit: str | None = None,
        icon: str | None = None,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self._key = key
        self._register = register
        self._attr_translation_key = key
        self._attr_unique_id = f"{coordinator.api.host}_{coordinator.api.port}_{key}"
        self._attr_device_info = coordinator.device_info
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        success = await self.coordinator.api.write_register(self._register, int(value))
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set %s to %f", self._key, value)


class MaicoExternalTempNumber(CoordinatorEntity[MaicoCoordinator], NumberEntity):
    """Number entity for external temperature input (writeable)."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: MaicoCoordinator,
        key: str,
        register: int,
        icon: str | None = None,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._key = key
        self._register = register
        self._attr_translation_key = key
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_{key}"
        self._attr_device_info = coordinator.device_info
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_min_value = -20.0
        self._attr_native_max_value = 50.0
        self._attr_native_step = 0.5
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Temperature values are stored as °C * 10
        raw_value = int(value * 10)
        _LOGGER.debug(
            "Writing %s: value=%.1f°C, raw=%d, register=%d",
            self._key,
            value,
            raw_value,
            self._register,
        )
        success = await self._api.write_register(self._register, raw_value)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set %s to %f", self._key, value)


class MaicoBusSensorNumber(CoordinatorEntity[MaicoCoordinator], NumberEntity):
    """Number entity for bus sensor input (humidity, air quality)."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(  # noqa: PLR0913
        self,
        coordinator: MaicoCoordinator,
        key: str,
        register: int,
        min_val: float,
        max_val: float,
        unit: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._key = key
        self._register = register
        self._attr_translation_key = key
        self._attr_unique_id = f"{self._api.host}_{self._api.port}_{key}"
        self._attr_device_info = coordinator.device_info
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = 1.0
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        raw_value = int(value)
        _LOGGER.debug(
            "Writing %s: value=%d, register=%d", self._key, raw_value, self._register
        )
        success = await self._api.write_register(self._register, raw_value)
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set %s to %f", self._key, value)
