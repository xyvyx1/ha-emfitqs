"""Data coordinator for Emfit QS."""

from __future__ import annotations

from datetime import timedelta
import ipaddress
import logging
import re

import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

LOGGER = logging.getLogger(__name__)
HOSTNAME_PATTERN = re.compile(r"^(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)*[a-zA-Z0-9-]{1,63}$")


def is_valid_host(host: str) -> bool:
    """Return whether host is a valid IP or hostname."""
    if not host:
        return False

    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return bool(HOSTNAME_PATTERN.fullmatch(host))


def parse_dvmstatus_response(response_text: str) -> dict[str, str]:
    """Parse dvmstatus text content into key/value pairs."""
    entries: dict[str, str] = {}
    elements = response_text.replace("<br>", "").lower().split("\r\n")
    filtered = list(filter(None, elements))
    for item in filtered:
        entry = item.split("=", 1)
        if len(entry) != 2:
            continue
        entry_name = entry[0].replace(":", "").replace(" ", "_").replace(",", "")
        entries[entry_name] = entry[1]
    return entries


def fetch_dvmstatus(host: str) -> dict[str, str]:
    """Fetch and parse dvmstatus data from host."""
    response = requests.get(f"http://{host}/dvmstatus.htm", timeout=10)
    response.raise_for_status()
    return parse_dvmstatus_response(response.text)


class EmfitQSCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinate Emfit QS data updates."""

    def __init__(self, hass: HomeAssistant, host: str, scan_interval: int) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name="emfitqs",
            update_interval=timedelta(seconds=scan_interval),
        )
        if not is_valid_host(host):
            raise ValueError("Invalid Emfit QS host")
        self._host = host

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch data from device."""

        try:
            data = await self.hass.async_add_executor_job(fetch_dvmstatus, self._host)
        except requests.RequestException as err:
            raise UpdateFailed(f"Error fetching Emfit QS data: {err}") from err

        if not data or "ser" not in data:
            raise UpdateFailed("Invalid Emfit QS response")

        return data
