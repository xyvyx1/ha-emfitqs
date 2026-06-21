"""Sensor platform for Emfit QS."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import EmfitQSCoordinator

CONF_ATTRIBUTION = "Data provided by Emfit QS"
DEFAULT_BRAND = "Emfit"
DEFAULT_NAME = "Emfit QS Sleep Tracker"

SENSOR_TYPES = {
    "heart_rate": ("Heart Rate", "bpm", "mdi:heart", "hr", SensorStateClass.MEASUREMENT),
    "respiratory_rate": (
        "Respiratory Rate",
        "bpm",
        "mdi:pinwheel",
        "rr",
        SensorStateClass.MEASUREMENT,
    ),
    "activity_level": ("Activity", "", "mdi:vibrate", "act", SensorStateClass.MEASUREMENT),
    "seconds_in_bed": ("Seconds in Bed", "s", "mdi:timer", "", SensorStateClass.TOTAL),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Emfit QS sensors from a config entry."""
    coordinator: EmfitQSCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[EmfitQSSensorEntity] = []
    for sensor_type in SENSOR_TYPES:
        if sensor_type == "seconds_in_bed":
            entities.append(EmfitQSTimeInBedSensor(coordinator, sensor_type))
        else:
            entities.append(EmfitQSSensorEntity(coordinator, sensor_type))

    async_add_entities(entities)


class EmfitQSBaseEntity(CoordinatorEntity[EmfitQSCoordinator]):
    """Base Emfit QS entity."""

    def __init__(self, coordinator: EmfitQSCoordinator, sensor_type: str) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        name, unit, icon, _, state_class = SENSOR_TYPES[sensor_type]
        serial = coordinator.data.get("ser", "unknown")
        self._attr_unique_id = f"{serial}_{sensor_type}"
        self._attr_name = f"EmfitQS {serial} {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_state_class = state_class

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


class EmfitQSSensorEntity(EmfitQSBaseEntity, SensorEntity):
    """Emfit QS sensor entity."""

    @property
    def native_value(self):
        """Return sensor state."""
        data_key = SENSOR_TYPES[self._sensor_type][3]
        return self.coordinator.data.get(data_key)


class EmfitQSTimeInBedSensor(EmfitQSBaseEntity, SensorEntity):
    """Emfit QS time-in-bed sensor."""

    def __init__(self, coordinator: EmfitQSCoordinator, sensor_type: str) -> None:
        """Initialize time-in-bed sensor."""
        super().__init__(coordinator, sensor_type)
        self._last_presence_change: datetime | None = None
        self._last_presence: str | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        presence = self.coordinator.data.get("pres")
        now = datetime.now()

        if presence == "1" and self._last_presence != "1":
            self._last_presence_change = now
        elif presence != "1":
            self._last_presence_change = None

        self._last_presence = presence
        super()._handle_coordinator_update()

    @property
    def native_value(self):
        """Return sensor state."""
        if self.coordinator.data.get("pres") != "1" or self._last_presence_change is None:
            return 0

        return round((datetime.now() - self._last_presence_change).total_seconds())
