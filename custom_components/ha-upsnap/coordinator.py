from __future__ import annotations

import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class UpSnapDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config_entry, api) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            data = await self.api.get_devices()
            return {device["id"]: device for device in data.get("items", []) if "id" in device}
        except Exception as err:
            raise UpdateFailed(f"Error fetching UpSnap data: {err}") from err