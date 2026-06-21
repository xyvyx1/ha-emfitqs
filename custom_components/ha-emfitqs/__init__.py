"""Emfit QS integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant

from .coordinator import EmfitQSCoordinator

DOMAIN = "emfitqs"
PLATFORMS = ["sensor", "binary_sensor"]
DEFAULT_SCAN_INTERVAL = 30


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Emfit QS from a config entry."""
    # Options override the original config data so the user can change
    # scan_interval post-setup without removing and re-adding the entry.
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    coordinator = EmfitQSCoordinator(
        hass,
        host=entry.data[CONF_HOST],
        scan_interval=scan_interval,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload the entry whenever the user saves new options so the coordinator
    # is recreated with the updated scan_interval.
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Emfit QS config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: EmfitQSCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        shutdown = getattr(coordinator, "async_shutdown", None)
        if shutdown is not None:
            await shutdown()
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok
