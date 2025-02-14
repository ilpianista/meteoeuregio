"""Support for Meteo Euregio weather."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_SUNNY,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sun import is_up
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import ATTR_ALTITUDE, DOMAIN, SKY_CONDITION_CLASSES
from .coordinator import MeteoEuregioDataUpdateCoordinator


def _night_if_sunny(
    sky_condition: str,
    hass: HomeAssistant = None,
    time: datetime.datetime | None = None,
) -> str:
    if sky_condition == ATTR_CONDITION_SUNNY and not is_up(hass, dt_util.as_utc(time)):
        return ATTR_CONDITION_CLEAR_NIGHT

    return sky_condition


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Meteo Euregio weather entity based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MeteoEuregioWeather(coordinator, entry.title)])


class MeteoEuregioWeather(CoordinatorEntity, WeatherEntity):
    """Defines an MeteoEuregio weather entity."""

    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
        self, coordinator: MeteoEuregioDataUpdateCoordinator, name: str
    ) -> None:
        """Initialize MeteoEuregio weather entity."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.venue.id
        self._attr_name = name

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.venue.id)},
            manufacturer="Meteo Euregio",
            name=name,
        )

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if not self.coordinator.data:
            return None

        current_forecast = next(iter(self.coordinator.data["forecast"]["180"].values()))
        return _night_if_sunny(
            SKY_CONDITION_CLASSES.get(current_forecast.get("sky_condition", ""))
        )

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data["observation"].get("temperature")

    @property
    def native_precipitation(self) -> float | None:
        """Return the precipitation."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data["observation"].get("rain_fall")

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data["observation"].get("pressure")

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data["observation"].get("relative_humidity")

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data["observation"].get("wind_speed")

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data["observation"].get("wind_direction")

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        if not self.coordinator.data:
            return None

        forecast_data = []

        start_date = dt_util.parse_datetime(self.coordinator.data["forecast"]["start"])

        # Add daily forecasts
        for idx, data in enumerate(self.coordinator.data["forecast"]["1440"].values()):
            forecast_data.append(
                {
                    ATTR_FORECAST_TIME: start_date + timedelta(days=idx),
                    ATTR_FORECAST_NATIVE_TEMP: data.get("temperature_maximum"),
                    ATTR_FORECAST_NATIVE_TEMP_LOW: data.get("temperature_minimum"),
                    ATTR_FORECAST_NATIVE_PRECIPITATION: data.get("rain_fall"),
                    ATTR_FORECAST_PRECIPITATION_PROBABILITY: data.get(
                        "rain_probability"
                    ),
                    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED: data.get("wind_gust"),
                    ATTR_FORECAST_NATIVE_WIND_SPEED: data.get("wind_speed"),
                    ATTR_FORECAST_WIND_BEARING: data.get("wind_direction"),
                    ATTR_FORECAST_CONDITION: SKY_CONDITION_CLASSES.get(
                        data.get("sky_condition", "")
                    ),
                }
            )

        return forecast_data

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast."""
        if not self.coordinator.data:
            return None

        forecast_data = []

        start_date = dt_util.parse_datetime(self.coordinator.data["forecast"]["start"])
        current_time = datetime.now()

        # Add hourly forecasts
        for idx, data in enumerate(self.coordinator.data["forecast"]["180"].values()):
            for hour in range(3):
                time = start_date + timedelta(hours=(idx * 3) + hour)

                # skip past forecast
                if time < current_time:
                    continue

                forecast_data.append(
                    {
                        ATTR_FORECAST_TIME: time,
                        ATTR_FORECAST_NATIVE_TEMP: data.get("temperature"),
                        ATTR_FORECAST_NATIVE_PRECIPITATION: data.get("rain_fall"),
                        ATTR_FORECAST_PRECIPITATION_PROBABILITY: data.get(
                            "rain_probability"
                        ),
                        ATTR_FORECAST_NATIVE_WIND_SPEED: data.get("wind_speed"),
                        ATTR_FORECAST_NATIVE_WIND_GUST_SPEED: data.get("wind_gust"),
                        ATTR_FORECAST_WIND_BEARING: data.get("wind_direction"),
                        ATTR_FORECAST_CONDITION: _night_if_sunny(
                            SKY_CONDITION_CLASSES.get(data.get("sky_condition", "")),
                            self.hass,
                            time,
                        ),
                    }
                )

                # 24 hours are enough
                if len(forecast_data) >= 24:
                    return forecast_data

        return forecast_data

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.venue:
            return {}

        return {
            ATTR_ALTITUDE: self.coordinator.venue.elevation,
            ATTR_LATITUDE: self.coordinator.venue.latitude,
            ATTR_LONGITUDE: self.coordinator.venue.longitude,
        }
