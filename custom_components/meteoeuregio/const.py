"""Constants for the MeteoEuregio integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Final

from homeassistant.components.weather import (
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_EXCEPTIONAL,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
)

DOMAIN: Final = "meteoeuregio"

LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)

ATTR_ALTITUDE = "altitude"

# https://manager.meteo.report/api/sky_conditions/
SKY_CONDITION_CLASSES = {
    "A": ATTR_CONDITION_SUNNY,  # Clear sky
    "B": ATTR_CONDITION_SUNNY,  # Sunny
    "C": ATTR_CONDITION_PARTLYCLOUDY,  # Partly cloudy
    "D": ATTR_CONDITION_CLOUDY,  # Mostly cloudy
    "E": ATTR_CONDITION_CLOUDY,  # Cloudy
    "F": ATTR_CONDITION_RAINY,  # Showers
    "G": ATTR_CONDITION_POURING,  # Heavy showers
    "H": ATTR_CONDITION_RAINY,  # Moderate rainfall
    "I": ATTR_CONDITION_POURING,  # Heavy rainfall
    "J": ATTR_CONDITION_RAINY,  # Light rainfall
    "K": ATTR_CONDITION_RAINY,  # Light showers
    "L": ATTR_CONDITION_SNOWY,  # Light snow and sun
    "M": ATTR_CONDITION_SNOWY,  # Snow and sun
    "N": ATTR_CONDITION_SNOWY,  # Light snow
    "O": ATTR_CONDITION_SNOWY,  # Moderate snow
    "P": ATTR_CONDITION_SNOWY,  # Heavy snow
    "Q": ATTR_CONDITION_SNOWY_RAINY,  # Wet snow and sun
    "R": ATTR_CONDITION_SNOWY_RAINY,  # Wet snow
    "S": ATTR_CONDITION_FOG,  # Haze
    "T": ATTR_CONDITION_FOG,  # Mountain haze
    "U": ATTR_CONDITION_EXCEPTIONAL,  # Unstable
    "V": ATTR_CONDITION_LIGHTNING,  # Thunderstorm
    "W": ATTR_CONDITION_SNOWY_RAINY,  # Unstable with wet snow
    "X": ATTR_CONDITION_LIGHTNING_RAINY,  # Wet snow thunderstorm
    "Y": ATTR_CONDITION_LIGHTNING_RAINY,  # Unstable with snow thunderstorm
    "Z": ATTR_CONDITION_LIGHTNING_RAINY,  # Snow thunderstorm
}

# Additional forecast attributes
ATTR_FORECAST_FRESH_SNOW = "fresh_snow"
ATTR_FORECAST_SNOW_LEVEL = "snow_level"
ATTR_FORECAST_FREEZING_LEVEL = "freezing_level"
ATTR_FORECAST_SUNSHINE_DURATION = "sunshine_duration"

# Additional states
ATTR_STATION_NAME = "station_name"
