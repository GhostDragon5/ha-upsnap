from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class UpSnapButtonEntityDescription(ButtonEntityDescription):
    method: str


BUTTONS: tuple[UpSnapButtonEntityDescription, ...] = (
    UpSnapButtonEntityDescription(
        key="wake",
        name="Wake",
        icon="mdi:power",
        method="wake_device",
        has_entity_name=True,
    ),
    UpSnapButtonEntityDescription(
        key="shutdown",
        name="Shutdown",
        icon="mdi:power-off",
        method="shutdown_device",
        has_entity_name=True,
    ),
    UpSnapButtonEntityDescription(
        key="reboot",
        name="Reboot",
        icon="mdi:restart",
        method="reboot_device",
        has_entity_name=True,
    ),
    UpSnapButtonEntityDescription(
        key="sleep",
        name="Sleep",
        icon="mdi:sleep",
        method="sleep_device",
        has_entity_name=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    entities = [
        UpSnapActionButton(coordinator, api, entry, device, description)
        for device in coordinator.data.values()
        for description in BUTTONS
    ]

    async_add_entities(entities)


class UpSnapActionButton(CoordinatorEntity, ButtonEntity):
    entity_description: UpSnapButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator, api, entry, device, description: UpSnapButtonEntityDescription) -> None:
        super().__init__(coordinator)
        self._api = api
        self._entry = entry
        self._device_id = device["id"]
        self._device_name = device.get("name") or device.get("hostname") or self._device_id
        self.entity_description = description

        self._attr_unique_id = f"{entry.entry_id}_{self._device_id}_{description.key}"
        self._attr_translation_key = description.key

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
    def available(self) -> bool:
        return self._device_id in self.coordinator.data

    async def async_press(self) -> None:
        await getattr(self._api, self.entity_description.method)(self._device_id)
        await self.coordinator.async_request_refresh()