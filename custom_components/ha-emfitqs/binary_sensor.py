"""Binary sensor platform for Emfit QS."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import EmfitQSCoordinator

CONF_ATTRIBUTION = "Data provided by Emfit QS"
DEFAULT_BRAND = "Emfit"
DEFAULT_NAME = "Emfit QS Sleep Tracker"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Emfit QS binary sensors from a config entry."""
    coordinator: EmfitQSCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EmfitQSBedPresenceBinarySensor(coordinator)])


class EmfitQSBedPresenceBinarySensor(CoordinatorEntity[EmfitQSCoordinator], BinarySensorEntity):
    """Emfit QS bed presence binary sensor."""

    _attr_name = "Bed Presence"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(self, coordinator: EmfitQSCoordinator) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        serial = coordinator.data.get("ser", "unknown")
        self._attr_unique_id = f"{serial}_bed_presence"
        self._attr_name = f"EmfitQS {serial} Bed Presence"

    @property
    def is_on(self) -> bool:
        """Return true if bed is occupied."""
        return self.coordinator.data.get("pres") == "1"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return state attributes."""
        return {ATTR_ATTRIBUTION: CONF_ATTRIBUTION}

    @property
    def device_info(self):
        """Return device info for registry."""
        serial = self.coordinator.data.get("ser")
        if not serial:
            return None
        return {
            "identifiers": {(DOMAIN, serial)},
            "name": DEFAULT_NAME,
            "manufacturer": DEFAULT_BRAND,
        }
