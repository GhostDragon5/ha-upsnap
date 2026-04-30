from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True)
class UpSnapButtonDescription:
    key: str
    name: str
    method: str
    icon: str


BUTTONS = [
    UpSnapButtonDescription("wake", "Wake", "wake_device", "mdi:power"),
    UpSnapButtonDescription("shutdown", "Shutdown", "shutdown_device", "mdi:power-off"),
    UpSnapButtonDescription("reboot", "Reboot", "reboot_device", "mdi:restart"),
    UpSnapButtonDescription("sleep", "Sleep", "sleep_device", "mdi:sleep"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    entities = []

    for device in coordinator.data.values():
        for description in BUTTONS:
            entities.append(
                UpSnapActionButton(
                    coordinator=coordinator,
                    api=api,
                    entry=entry,
                    device=device,
                    description=description,
                )
            )

    async_add_entities(entities)


class UpSnapActionButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, api, entry, device, description) -> None:
        super().__init__(coordinator)
        self._api = api
        self._entry = entry
        self._device_id = device["id"]
        self._device_name = device.get("name") or device.get("hostname") or self._device_id
        self.entity_description = description

        self._attr_name = f"{self._device_name} {description.name}"
        self._attr_unique_id = f"{entry.entry_id}_{self._device_id}_{description.key}"
        self._attr_icon = description.icon

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="UpSnap",
            model="Network Device",
            configuration_url=self._entry.data.get("url"),
        )

    async def async_press(self) -> None:
        await getattr(self._api, self.entity_description.method)(self._device_id)
        await self.coordinator.async_request_refresh()