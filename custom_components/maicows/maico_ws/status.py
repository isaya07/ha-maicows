"""Maico WS status aggregation and processing."""

from __future__ import annotations

import logging
from typing import Any

from .registers import MaicoWSRegisters

_LOGGER = logging.getLogger(__name__)


class StatusMixin:
    """Mixin providing status aggregation for MaicoWS."""

    # These will be provided by the base class
    _connected: bool

    async def read_holding_registers(
        self, register: int, count: int
    ) -> list[int] | None:
        """Read multiple holding registers (from base class)."""

    async def read_holding_register(self, register: int) -> int | None:
        """Read single holding register (from base class)."""

    async def read_operation_mode(self) -> int | None:
        """Read operation mode (from sensors mixin)."""

    async def get_all_status(self) -> dict[str, Any] | None:
        """Read all status data using sequential block reads."""
        if not self._connected:
            _LOGGER.error("Not connected to Maico WS")
            return None

        results = []
        try:
            # Settings block (300-302)
            results.append(await self.read_holding_registers(300, 3))
            # Ventilation/Fan block (650-657)
            results.append(await self.read_holding_registers(650, 8))
            # Temperatures block (700-707)
            results.append(await self.read_holding_registers(700, 8))
            # Humidity, CO2, VOC block (750-764)
            results.append(await self.read_holding_registers(750, 15))
            # Operation mode block (550-554)
            results.append(await self.read_holding_registers(550, 5))
            # Switch states block (800-808)
            results.append(await self.read_holding_registers(800, 9))
            # Faults/Info block (401-404)
            results.append(await self.read_holding_registers(401, 4))
            # Filter/Flow settings (150-159)
            results.append(await self.read_holding_registers(150, 10))
            # Operating hours (850-859)
            results.append(await self.read_holding_registers(850, 10))
            # Room temp selection (109)
            results.append(await self.read_holding_register(109))
        except Exception:
            _LOGGER.exception("Error during status update")
            return None

        return self._process_status_results(results)

    def _process_status_results(self, results: list) -> dict[str, Any]:  # noqa: PLR0912, PLR0915
        """Process the results from Modbus reads."""
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
            room_temp_sel,
        ) = results

        status: dict[str, Any] = {}

        # Helper functions
        def to_temp(raw: int) -> float:
            """Convert raw to temperature."""
            if raw > MaicoWSRegisters.MAX_INT_16BIT:
                raw -= 65536
            return raw / 10.0

        def combine(hi: int, lo: int) -> int:
            """Combine high and low words."""
            return (hi << 16) | lo

        # 1. Settings Block (300-302)
        if settings_block:
            status["room_temp_adjust"] = to_temp(settings_block[0])
            status["supply_temp_min_cool"] = settings_block[1]
            status["room_temp_max"] = to_temp(settings_block[2])

        # 2. Ventilation/Fan Block (650-657)
        if vent_block:
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

        # 3. Temperatures Block (700-707)
        if temp_block:
            status["room_temperature"] = to_temp(temp_block[0])
            status["room_temperature_ext"] = to_temp(temp_block[1])
            # temp_block[2] = 702 (before EWT)
            status["inlet_air_temperature"] = to_temp(temp_block[3])
            status["supply_air_temperature"] = to_temp(temp_block[4])
            status["extract_air_temperature"] = to_temp(temp_block[5])
            status["exhaust_air_temperature"] = to_temp(temp_block[6])
            status["room_temperature_bus"] = to_temp(temp_block[7])

        # 4. Humidity, CO2, VOC Block (750-764)
        if hum_block:
            status["extract_air_humidity"] = hum_block[0]
            if len(hum_block) > 4:  # noqa: PLR2004
                status["humidity_sensor_1"] = hum_block[1]
                status["humidity_sensor_2"] = hum_block[2]
                status["humidity_sensor_3"] = hum_block[3]
                status["humidity_sensor_4"] = hum_block[4]

            if len(hum_block) > 8:  # noqa: PLR2004
                status["co2_sensor_1"] = hum_block[5] / 10.0
                status["co2_sensor_2"] = hum_block[6] / 10.0
                status["co2_sensor_3"] = hum_block[7] / 10.0
                status["co2_sensor_4"] = hum_block[8] / 10.0

            if len(hum_block) > 12:  # noqa: PLR2004
                status["voc_sensor_1"] = hum_block[9] / 10.0
                status["voc_sensor_2"] = hum_block[10] / 10.0
                status["voc_sensor_3"] = hum_block[11] / 10.0
                status["voc_sensor_4"] = hum_block[12] / 10.0

            if len(hum_block) > 14:  # noqa: PLR2004
                status["humidity_bus"] = hum_block[13]
                status["air_quality_bus"] = hum_block[14]

        # 5. Operation Mode Block (550-554)
        if op_block:
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
            status["boost_ventilation"] = bool(op_block[1])
            season_map = {0: "winter", 1: "summer"}
            status["season"] = season_map.get(op_block[2], f"unknown_{op_block[2]}")
            status["target_temperature"] = to_temp(op_block[3])
            status["ventilation_level"] = op_block[4]

        # 6. Switch States Block (800-808)
        if switch_block:
            status["supply_fan_state"] = bool(switch_block[0])
            status["extract_fan_state"] = bool(switch_block[1])
            status["bypass_status"] = bool(switch_block[2])
            status["ptc_heater"] = bool(switch_block[3])
            if len(switch_block) > 4:  # noqa: PLR2004
                status["switch_contact"] = bool(switch_block[4])
            if len(switch_block) > 5:  # noqa: PLR2004
                status["post_heater_relay"] = bool(switch_block[5])
            if len(switch_block) > 6:  # noqa: PLR2004
                status["brine_pump"] = switch_block[6]
            if len(switch_block) > 7:  # noqa: PLR2004
                status["three_way_damper"] = switch_block[7]
            if len(switch_block) > 8:  # noqa: PLR2004
                status["zone_damper"] = switch_block[8]

        # 7. Faults/Info Block (401-404)
        if fault_block:
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

        # 8. Filter/Flow Settings (150-159)
        if filter_flow_block:
            status["filter_device_months"] = filter_flow_block[0]
            status["filter_outdoor_months"] = filter_flow_block[1]
            status["filter_room_months"] = filter_flow_block[2]
            status["filter_duration"] = filter_flow_block[3]
            status["volume_flow_reduced"] = filter_flow_block[4]
            status["volume_flow_normal"] = filter_flow_block[5]
            status["volume_flow_intensive"] = filter_flow_block[6]

        # 9. Operating Hours (850-859)
        if hours_block:
            status["hours_humidity"] = combine(hours_block[0], hours_block[1])
            status["hours_reduced"] = combine(hours_block[2], hours_block[3])
            status["hours_nominal"] = combine(hours_block[4], hours_block[5])
            status["hours_intensive"] = combine(hours_block[6], hours_block[7])
            status["hours_total"] = combine(hours_block[8], hours_block[9])

        # 10. Room Temp Selection (109)
        if room_temp_sel is not None:
            room_sel_map = {0: "comfort_bde", 1: "external", 2: "internal", 3: "bus"}
            status["room_temp_selection"] = room_sel_map.get(
                room_temp_sel, f"unknown_{room_temp_sel}"
            )

        # Calculate power state from operation mode
        status["power_state"] = status.get("operation_mode") != "off"

        return status

    async def read_all_registers(self) -> dict[str, Any] | None:
        """Alias for get_all_status (backward compatibility)."""
        return await self.get_all_status()

    async def get_device_info(self) -> dict[str, Any] | None:
        """Get device information."""
        if not self._connected:
            return None

        val = await self.read_holding_register(MaicoWSRegisters.OPERATION_MODE)
        if val is None:
            return None

        return {"serial_number": "maico_ws320b_device"}
