"""Config flow for Meteo Euregio integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "meteoeuregio"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meteo Euregio."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default="Meteo Euregio"): str,
                        vol.Required(
                            CONF_LATITUDE, default=self.hass.config.latitude
                        ): vol.Coerce(float),
                        vol.Required(
                            CONF_LONGITUDE, default=self.hass.config.longitude
                        ): vol.Coerce(float),
                    }
                ),
            )

        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
