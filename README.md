# UpSnap for Home Assistant

[![Open your Home Assistant instance and open the repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=GhostDragon5&repository=ha-upsnap&category=integration)

This custom integration connects your **UpSnap** instance to Home Assistant and adds device controls for:

- Wake
- Shutdown
- Reboot
- Sleep
- Online status sensor

It uses the UpSnap REST API to authenticate, read devices, and trigger actions.

## Features

- Add UpSnap through the Home Assistant UI
- Wake devices using UpSnap
- Shut down devices using UpSnap
- Reboot devices using UpSnap
- Put devices to sleep using UpSnap
- Show device online status as a binary sensor

## Requirements

- A working UpSnap instance
- A valid UpSnap user account
- Home Assistant with support for custom integrations
- HACS (optional, if you want to install it through HACS)

## Installation

### HACS

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository.
3. Select the category **Integration**.
4. Install **UpSnap**.
5. Restart Home Assistant.

### Manual

1. Copy the `upsnap` folder into:

   ```text
   /config/custom_components/upsnap
   ```

2. Restart Home Assistant.

### Add Integration

1. Open Home Assistant.
2. Go to:

   **Settings → Devices & services**

3. Click **Add Integration**.
4. Search for **UpSnap**.
5. Enter your UpSnap connection details:
   - UpSnap URL, for example: `http://192.168.1.8:8090`
   - Username or email
   - Password
   - SSL verification option if needed
6. Finish the setup.

## Entities

After setup, Home Assistant creates the following entities for each UpSnap device.

### Buttons

- Wake
- Shutdown
- Reboot
- Sleep

### Sensors

- Online

## Example entities

Home Assistant may create entities similar to:

- `button.device_wake`
- `button.device_shutdown`
- `button.device_reboot`
- `button.device_sleep`
- `binary_sensor.device_online`

## Troubleshooting

If the integration does not load correctly:

1. Check the Home Assistant logs.
2. Verify that `__init__.py` exists inside `/config/custom_components/upsnap/`.
3. Remove Python cache files:

   ```bash
   rm -rf /config/custom_components/upsnap/__pycache__
   find /config/custom_components/upsnap -name "*.pyc" -delete
   ```

4. Restart Home Assistant again.

## Notes

- This integration uses the UpSnap REST API.
- Device actions depend on the functionality available in your UpSnap instance.
- Button entities may appear in the entity list even if they are not immediately visible on the device overview page.

## License

This project is provided as a custom integration example and can be adapted to your own environment.