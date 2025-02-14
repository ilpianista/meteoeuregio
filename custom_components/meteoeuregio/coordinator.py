"""Support for Meteo Euregio weather."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL


@dataclass(frozen=True)
class VenueInfo:
    """Class to store venue information."""

    id: str
    name: str
    elevation: int
    latitude: float
    longitude: float

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> VenueInfo:
        """Create a VenueInfo instance from JSON data."""
        return cls(
            id=data["id"],
            name=data["name_eng"],
            elevation=int(data["elevation"]),
            latitude=float(data["lat"]),
            longitude=float(data["lon"]),
        )


class MeteoEuregioDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Meteo Euregio data."""

    def __init__(self, hass: HomeAssistant, *, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.venue = None
        self._forecast_venue_id = None

    # venue_type: 3 for observation, 2 for forecast
    async def _find_nearest_venue(
        self, lat: float, lon: float, venue_type: int
    ) -> tuple[str, VenueInfo]:
        """Find the nearest venue ID based on coordinates."""
        async with (
            aiohttp.ClientSession() as session,
            session.get(
                f"https://manager.meteo.report/api/venues/?id_venue_type={venue_type}"
            ) as response,
        ):
            venues = await response.json()

        if not venues:
            return None

        # Find nearest venue using basic distance calculation
        nearest = min(
            venues,
            key=lambda x: ((float(x["lat"]) - lat) ** 2 + (float(x["lon"]) - lon) ** 2),
        )
        return (nearest["id"], VenueInfo.from_json(nearest))

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API."""
        lat = self.config_entry.data[CONF_LATITUDE]
        lon = self.config_entry.data[CONF_LONGITUDE]

        # Get venue IDs if not already fetched
        if self.venue is None:
            _, self.venue = await self._find_nearest_venue(lat, lon, 3)

        if self._forecast_venue_id is None:
            self._forecast_venue_id, _ = await self._find_nearest_venue(lat, lon, 2)

        if not self.venue or not self._forecast_venue_id:
            raise HomeAssistantError("Could not find suitable weather stations")

        async with aiohttp.ClientSession() as session:
            # Get current conditions
            async with session.get(
                f"https://meteo.report/var/data/observations/{self.venue.id}.json"
            ) as response:
                observation = await response.json()

                latest_key = max(observation["30"].keys(), key=int)
                observation_data = observation["30"][latest_key]

            # Get forecast
            async with session.get(
                f"https://meteo.report/var/data/forecasts/{self._forecast_venue_id}.json"
            ) as response:
                forecast = await response.json()

        return {"observation": observation_data, "forecast": forecast}
