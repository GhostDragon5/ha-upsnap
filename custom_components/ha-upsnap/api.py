from __future__ import annotations

from typing import Any
import aiohttp


class UpSnapApiError(Exception):
    pass


class UpSnapAuthError(UpSnapApiError):
    pass


class UpSnapConnectionError(UpSnapApiError):
    pass


class UpSnapApiClient:
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True) -> None:
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._token: str | None = None

    async def authenticate(self) -> None:
        payload = {"identity": self._username, "password": self._password}
        try:
            connector = aiohttp.TCPConnector(ssl=self._verify_ssl)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    f"{self._base_url}/api/collections/users/auth-with-password",
                    json=payload,
                ) as response:
                    if response.status in (401, 403):
                        raise UpSnapAuthError("Invalid credentials")
                    response.raise_for_status()
                    data = await response.json()
                    self._token = data["token"]
        except UpSnapAuthError:
            raise
        except aiohttp.ClientError as err:
            raise UpSnapConnectionError(str(err)) from err

    async def _decode_response(self, response: aiohttp.ClientResponse) -> Any:
        if "application/json" in response.headers.get("Content-Type", ""):
            return await response.json()
        return await response.text()

    async def _request(self, method: str, path: str) -> Any:
        if not self._token:
            await self.authenticate()
        headers = {"Authorization": f"Bearer {self._token}"}
        try:
            connector = aiohttp.TCPConnector(ssl=self._verify_ssl)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.request(method, f"{self._base_url}{path}", headers=headers) as response:
                    if response.status == 401:
                        await self.authenticate()
                        headers = {"Authorization": f"Bearer {self._token}"}
                        async with session.request(method, f"{self._base_url}{path}", headers=headers) as retry:
                            if retry.status in (401, 403):
                                raise UpSnapAuthError("Re-authentication failed")
                            retry.raise_for_status()
                            return await self._decode_response(retry)
                    if response.status in (401, 403):
                        raise UpSnapAuthError("Unauthorized")
                    response.raise_for_status()
                    return await self._decode_response(response)
        except UpSnapApiError:
            raise
        except aiohttp.ClientError as err:
            raise UpSnapConnectionError(str(err)) from err

    async def test_connection(self) -> None:
        await self.authenticate()
        await self.get_devices()

    async def get_devices(self) -> dict[str, Any]:
        result = await self._request("GET", "/api/collections/devices/records")
        return result if isinstance(result, dict) else {"items": []}

    async def wake_device(self, device_id: str) -> Any:
        return await self._request("GET", f"/api/upsnap/wake/{device_id}")

    async def shutdown_device(self, device_id: str) -> Any:
        return await self._request("GET", f"/api/upsnap/shutdown/{device_id}")

    async def reboot_device(self, device_id: str) -> Any:
        return await self._request("GET", f"/api/upsnap/reboot/{device_id}")

    async def sleep_device(self, device_id: str) -> Any:
        return await self._request("GET", f"/api/upsnap/sleep/{device_id}")