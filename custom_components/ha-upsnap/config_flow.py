from __future__ import annotations

from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from .api import UpSnapApiClient, UpSnapAuthError, UpSnapConnectionError
from .const import CONF_VERIFY_SSL, DOMAIN


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    api = UpSnapApiClient(
        data[CONF_URL],
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
        data[CONF_VERIFY_SSL],
    )
    await api.test_connection()
    return {"title": f"UpSnap ({data[CONF_URL].rstrip('/')})"}


class UpSnapConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(user_input)
            except UpSnapAuthError:
                errors["base"] = "invalid_auth"
            except UpSnapConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                unique = user_input[CONF_URL].rstrip("/")
                await self.async_set_unique_id(unique)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_VERIFY_SSL, default=True): bool,
                }
            ),
            errors=errors,
        )