from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UpSnapDataUpdateCoordinator

ONLINE_STATES: set[str | bool] = {"on", "online", "up", "awake", "running", True}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            UpSnapOnlineBinarySensor(coordinator, entry, device)
            for device in coordinator.data.values()
        ]
    )


class UpSnapOnlineBinarySensor(CoordinatorEntity[dict[str, Any]], BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: UpSnapDataUpdateCoordinator,
        entry: ConfigEntry,
        device: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._device_id = device["id"]
        self._device_name = str(device.get("name") or device.get("hostname") or self._device_id)
        self._attr_name = f"{self._device_name} Online"
        self._attr_unique_id = f"{entry.entry_id}_{self._device_id}_online"
        self._attr_icon = "mdi:lan-connect"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="UpSnap",
            model="Network Device",
            configuration_url=self._entry.data.get("url"),
        )

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.data.get(self._device_id, {})
        value = device.get("status")
        if isinstance(value, str):
            return value.strip().lower() in ONLINE_STATES
        return value in ONLINE_STATES if value is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        device = self.coordinator.data.get(self._device_id, {})
        return {
            key: device[key]
            for key in ("status", "mac", "ip", "name", "created", "updated")
            if key in device
        }