"""Maico WS Modbus register definitions."""

from __future__ import annotations


class MaicoWSRegisters:
    """Register addresses for Maico WS VMC based on official documentation."""

    # Date/Time Settings
    DATE_YEAR = 100  # Year
    DATE_MONTH = 101  # Month
    DATE_DAY = 102  # Day
    TIME_HOUR = 103  # Hour
    TIME_MINUTE = 104  # Minute
    TIME_SECOND = 105  # Second

    # Basic Configuration
    LOCK_FAN_OFF = 106  # Lock fan level off (0=Off possible, 1=Off locked)
    BDE_LOCK = 107  # BDE lock (0=not locked, 1=locked)
    LANGUAGE = 108  # Language (0=German, 1=English, 2=French, 3=Italian)
    ROOM_TEMP_SELECTION = 109  # Room temp sensor selection
    # 0=Comfort-BDE, 1=External, 2=Internal, 3=Bus

    # Filter Settings
    FILTER_DEVICE_MONTHS = 150  # Filter lifespan device filter (3-12 months)
    FILTER_OUTDOOR_MONTHS = 151  # Filter lifespan outdoor filter (3-18 months)
    FILTER_ROOM_MONTHS = 152  # Filter lifespan room filter (1-6 months)
    FILTER_DURATION = 153  # Ventilation level duration (Min)
    VOLUME_FLOW_REDUCED = 154  # Volume flow reduced ventilation
    VOLUME_FLOW_NORMAL = 155  # Volume flow nominal ventilation
    VOLUME_FLOW_INTENSIVE = 156  # Volume flow intensive ventilation
    FILTER_CHANGE_DEVICE = 157  # Filter change device (0=not changed, 1=changed)
    FILTER_CHANGE_OUTDOOR = 158  # Filter change outdoor (0=not changed, 1=changed)
    FILTER_CHANGE_ROOM = 159  # Filter change room (0=not changed, 1=changed)

    # Temperature Settings
    ROOM_TEMP_ADJUST = 300  # Room temperature adjustment (-3°C to +3°C * 10)
    SUPPLY_TEMP_MIN_COOL = 301  # Supply temp min. cooling
    ROOM_TEMP_MAX = 302  # Room temp max.

    # Error and Info Messages
    CURRENT_ERROR_HI = 401  # Current error (High-Word)
    CURRENT_ERROR_LO = 402  # Current error (Low-Word)
    CURRENT_INFO_HI = 403  # Current info (High-Word)
    CURRENT_INFO_LO = 404  # Current info (Low-Word)
    ERROR_RESET = 405  # Error reset (0=normal, 1=reset)

    # Basic Settings / Operation
    OPERATION_MODE = 550  # 0=Off, 1=Manual, 2=Auto-Time, 3=Auto-Sensor,
    # 4=Eco-Supply, 5=Eco-Extract
    BOOST_VENTILATION = 551  # Boost ventilation (0=inactive, 1=active)
    SEASON = 552  # Season (0=Winter, 1=Summer)
    TARGET_ROOM_TEMP = 553  # Target room temperature (°C * 10)
    VENTILATION_LEVEL = 554  # 0=Off, 1=Humidity prot, 2=Reduced, 3=Nominal, 4=Intensive

    # Ventilation Queries
    CURRENT_VENTILATION_LEVEL = 650  # Current ventilation level
    SUPPLY_FAN_SPEED = 651  # Current supply fan speed (RPM)
    EXTRACT_FAN_SPEED = 652  # Current extract fan speed (RPM)
    SUPPLY_VOLUME_FLOW = 653  # Current supply volume flow (m³/h)
    EXTRACT_VOLUME_FLOW = 654  # Current extract volume flow (m³/h)
    FILTER_REMAIN_DEVICE = 655  # Device filter remaining time (days)
    FILTER_REMAIN_OUTDOOR = 656  # Outdoor filter remaining time (days)
    FILTER_REMAIN_ROOM = 657  # Room filter remaining time (days)

    # Current Temperatures
    ROOM_TEMP = 700  # Room temperature (°C * 10)
    ROOM_TEMP_EXT = 701  # External room temperature sensor (°C * 10) - Write
    TEMP_BEFORE_EWT = 702  # Temp before earth tube heat exchanger (°C * 10)
    INLET_AIR_TEMP = 703  # Inlet air temperature (°C * 10)
    SUPPLY_AIR_TEMP = 704  # Supply air temperature (°C * 10)
    EXTRACT_AIR_TEMP = 705  # Extract air temperature (°C * 10)
    EXHAUST_AIR_TEMP = 706  # Exhaust air temperature (°C * 10)
    ROOM_TEMP_BUS = 707  # Bus room temperature (°C * 10) - Write, cycle 10min

    # Humidity Data
    EXTRACT_AIR_HUMIDITY = 750  # Extract air humidity (% * 10)
    HUMIDITY_SENSOR_1 = 751  # Humidity sensor 1 (% * 10)
    HUMIDITY_SENSOR_2 = 752  # Humidity sensor 2 (% * 10)
    HUMIDITY_SENSOR_3 = 753  # Humidity sensor 3 (% * 10)
    HUMIDITY_SENSOR_4 = 754  # Humidity sensor 4 (% * 10)

    # CO2 Sensors
    CO2_SENSOR_1 = 755  # CO2 sensor 1 (ppm * 10)
    CO2_SENSOR_2 = 756  # CO2 sensor 2 (ppm * 10)
    CO2_SENSOR_3 = 757  # CO2 sensor 3 (ppm * 10)
    CO2_SENSOR_4 = 758  # CO2 sensor 4 (ppm * 10)

    # VOC Sensors
    VOC_SENSOR_1 = 759  # VOC sensor 1 (ppm * 10)
    VOC_SENSOR_2 = 760  # VOC sensor 2 (ppm * 10)
    VOC_SENSOR_3 = 761  # VOC sensor 3 (ppm * 10)
    VOC_SENSOR_4 = 762  # VOC sensor 4 (ppm * 10)

    # Bus Sensor Inputs (Write registers)
    HUMIDITY_BUS = 763  # Bus humidity (% RH) - Write, cycle 10min
    AIR_QUALITY_BUS = 764  # Bus air quality/CO2 (ppm) - Write, cycle 10min

    # Switch States
    SUPPLY_FAN_STATE = 800  # Supply fan state (0=off, 1=on)
    EXTRACT_FAN_STATE = 801  # Extract fan state (0=off, 1=on)
    BYPASS_ACTUATOR = 802  # Summer bypass actuator (0=closed, 1=open)
    PTC_HEATER = 803  # PTC heater (0=off, 1=on)
    SWITCH_CONTACT = 804  # Switch contact base board (0=off, 1=on)
    POST_HEATER_RELAY = 805  # Post-heater relay ZP1 (0=off, 1=on)
    BRINE_PUMP = 806  # Brine circulation pump ZP1 (0=Off, 1=heating, 2=cooling)
    THREE_WAY_DAMPER = 807  # 3-way air damper ZP1 (0=Off, 1=heating, 2=cooling)
    ZONE_DAMPER = 808  # Zone damper ZP1 (0=Off, 1=Zone1, 2=Zone2, 3=Zone Sensor)

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

    # Filter Monitoring
    FILTER_DELTA_P_LIMIT = 900  # Allowed delta p filter monitoring (10-200%)

    # Constants
    MAX_INT_16BIT = 32767
    VENTILATION_LEVEL_MIN = 0
    VENTILATION_LEVEL_MAX = 4

    # Room Temp Selection Options
    ROOM_TEMP_SEL_COMFORT_BDE = 0
    ROOM_TEMP_SEL_EXTERNAL = 1
    ROOM_TEMP_SEL_INTERNAL = 2
    ROOM_TEMP_SEL_BUS = 3
