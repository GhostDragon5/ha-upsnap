from homeassistant import config_entries


class UpSnapConfigFlow(config_entries.ConfigFlow, domain="upsnap"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="UpSnap", data=user_input)
        return self.async_show_form(step_id="user", data_schema=None)