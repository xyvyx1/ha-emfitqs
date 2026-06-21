"""Config flow for Emfit QS."""

from __future__ import annotations

from typing import Any

import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL

from .coordinator import fetch_dvmstatus, is_valid_host

DOMAIN = "emfitqs"
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10


async def _async_validate_host(hass, host: str) -> dict[str, str]:
    """Validate host and return parsed device data."""
    return await hass.async_add_executor_job(fetch_dvmstatus, host)


class EmfitQSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Emfit QS config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

            if not is_valid_host(host):
                errors["base"] = "cannot_connect"
            else:
                try:
                    data = await _async_validate_host(self.hass, host)
                except requests.RequestException:
                    errors["base"] = "cannot_connect"
                else:
                    serial = data.get("ser")
                    if not serial:
                        errors["base"] = "invalid_response"
                    else:
                        await self.async_set_unique_id(serial)
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title=f"Emfit QS {serial}",
                            data={
                                CONF_HOST: host,
                                CONF_SCAN_INTERVAL: scan_interval,
                            },
                        )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
