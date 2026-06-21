"""Data coordinator for Emfit QS."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

LOGGER = logging.getLogger(__name__)


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
        self._host = host

    def async_stop(self) -> None:
        """Cancel scheduled refreshes."""
        if self._unsub_refresh is not None:
            self._unsub_refresh()
            self._unsub_refresh = None

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch data from device."""

        def _fetch() -> dict[str, str]:
            response = requests.get(f"http://{self._host}/dvmstatus.htm", timeout=10)
            response.raise_for_status()

            entries: dict[str, str] = {}
            elements = response.text.replace("<br>", "").lower().split("\r\n")
            filtered = list(filter(None, elements))
            for item in filtered:
                entry = item.split("=", 1)
                if len(entry) != 2:
                    continue
                entry_name = entry[0].replace(":", "").replace(" ", "_").replace(",", "")
                entries[entry_name] = entry[1]
            return entries

        try:
            data = await self.hass.async_add_executor_job(_fetch)
        except requests.RequestException as err:
            raise UpdateFailed(f"Error fetching Emfit QS data: {err}") from err

        if not data or "ser" not in data:
            raise UpdateFailed("Invalid Emfit QS response")

        return data
