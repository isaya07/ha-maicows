"""Constants for the Maico WS integration."""

from typing import Final

DOMAIN: Final = "maicows"
DEFAULT_NAME: Final = "Maico WS"
DEFAULT_PORT: Final = 502
DEFAULT_SLAVE_ID: Final = 1

# Configuration keys
CONF_SLAVE_ID: Final = "slave_id"
CONF_CONNECTION_TYPE: Final = "connection_type"
CONF_SERIAL_PORT: Final = "serial_port"
CONF_BAUDRATE: Final = "baudrate"

# Connection types
CONNECTION_TYPE_TCP: Final = "tcp"
CONNECTION_TYPE_RTU: Final = "rtu"

# RTU defaults
DEFAULT_BAUDRATE: Final = 9600
DEFAULT_SERIAL_PORT: Final = "/dev/ttyUSB0"

# Platform setup
PLATFORMS: Final[list[str]] = ["climate", "fan", "sensor", "switch", "number", "select"]

# Device attributes
ATTR_SUPPLY_AIR_TEMP: Final = "supply_air_temperature"
ATTR_EXTRACT_AIR_TEMP: Final = "extract_air_temperature"
ATTR_OUTDOOR_AIR_TEMP: Final = "outdoor_air_temperature"
ATTR_SUPPLY_AIR_HUMIDITY: Final = (
    "extract_air_humidity"  # Maico uses extract for humidity
)
ATTR_SUPPLY_FAN_SPEED: Final = "supply_fan_speed"
ATTR_EXTRACT_FAN_SPEED: Final = "extract_fan_speed"
ATTR_FAN_LEVEL: Final = "fan_level"
ATTR_POWER_STATE: Final = "power_state"
ATTR_FILTER_STATUS: Final = "filter_status"
ATTR_FILTER_RUNTIME: Final = "filter_runtime"
ATTR_BYPASS_STATUS: Final = "bypass_status"
ATTR_OPERATION_MODE: Final = "operation_mode"
ATTR_FAULT_STATUS: Final = "fault_status"
ATTR_INFO_MESSAGES: Final = "info_messages"

# Fan levels
FAN_LEVEL_1: Final = 1
FAN_LEVEL_2: Final = 2
FAN_LEVEL_3: Final = 3
FAN_LEVEL_4: Final = 4
FAN_LEVELS: Final[list[int]] = [FAN_LEVEL_1, FAN_LEVEL_2, FAN_LEVEL_3, FAN_LEVEL_4]

# Operation modes based on official documentation
# 0=Off, 1=Manual, 2=Auto-Time, 3=Auto-Sensor, 4=Eco-Supply Air, 5=Eco-Extract Air
OPERATION_MODE_OFF: Final = "off"
OPERATION_MODE_MANUAL: Final = "manual"
OPERATION_MODE_AUTO_TIME: Final = "auto_time"
OPERATION_MODE_AUTO_SENSOR: Final = "auto_sensor"
OPERATION_MODE_ECO_SUPPLY: Final = "eco_supply"
OPERATION_MODE_ECO_EXTRACT: Final = "eco_extract"
OPERATION_MODES: Final[list[str]] = [
    OPERATION_MODE_OFF,
    OPERATION_MODE_MANUAL,
    OPERATION_MODE_AUTO_TIME,
    OPERATION_MODE_AUTO_SENSOR,
    OPERATION_MODE_ECO_SUPPLY,
    OPERATION_MODE_ECO_EXTRACT,
]

# Ventilation levels based on official documentation
# 0=Off, 1=Humidity protection, 2=Reduced, 3=Nominal, 4=Intensive
VENTILATION_LEVEL_OFF: Final = 0
VENTILATION_LEVEL_HUMIDITY_PROTECTION: Final = 1
VENTILATION_LEVEL_REDUCED: Final = 2
VENTILATION_LEVEL_NORMAL: Final = 3
VENTILATION_LEVEL_INTENSIVE: Final = 4
VENTILATION_LEVELS: Final[list[int]] = [
    VENTILATION_LEVEL_OFF,
    VENTILATION_LEVEL_HUMIDITY_PROTECTION,
    VENTILATION_LEVEL_REDUCED,
    VENTILATION_LEVEL_NORMAL,
    VENTILATION_LEVEL_INTENSIVE,
]

# Season settings
SEASON_WINTER: Final = "winter"
SEASON_SUMMER: Final = "summer"
SEASONS: Final[list[str]] = [SEASON_WINTER, SEASON_SUMMER]

# Filter change registers
FILTER_CHANGE_DEVICE: Final = "filter_change_device"
FILTER_CHANGE_OUTDOOR: Final = "filter_change_outdoor"
FILTER_CHANGE_ROOM: Final = "filter_change_room"

# Temperature settings
ROOM_TEMP_ADJUST: Final = "room_temp_adjust"
SUPPLY_TEMP_MIN_COOL: Final = "supply_temp_min_cool"
ROOM_TEMP_MAX: Final = "room_temp_max"

# Volume flow settings
VOLUME_FLOW_REDUCED: Final = "volume_flow_reduced"
VOLUME_FLOW_NORMAL: Final = "volume_flow_normal"
VOLUME_FLOW_INTENSIVE: Final = "volume_flow_intensive"

# Filter duration settings
FILTER_DURATION_VENTILATION: Final = "filter_duration_ventilation"

# Filter status
FILTER_STATUS_OK: Final = "ok"
FILTER_STATUS_REPLACE: Final = "replace"
FILTER_STATUS_ALARM: Final = "alarm"

# Default scan interval (in seconds)
DEFAULT_SCAN_INTERVAL: Final = 30
