from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import UpSnapApiClient, UpSnapAuthError, UpSnapConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class UpSnapDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: UpSnapApiClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, dict]:
        try:
            data = await self.api.get_devices()
            return {device["id"]: device for device in data.get("items", []) if "id" in device}
        except UpSnapAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except UpSnapConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err