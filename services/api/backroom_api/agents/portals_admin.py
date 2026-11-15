"""Client for the portals' admin API (CONTRACTS §2): chaos seed, state, reset.

The run's truth is the portal's own state, not what the page looked like: postconditions
read `GET /_admin/state/{portal}`, and the bench sets the chaos seed through here.
"""

from typing import Any

import httpx

from backroom_api.config import Settings


class PortalAdmin:
    def __init__(self, settings: Settings | None = None) -> None:
        s = settings or Settings()
        self._client = httpx.AsyncClient(
            base_url=s.portals_base_url,
            headers={"X-Admin-Token": s.portals_admin_token},
            timeout=10.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def state(self, portal: str) -> dict[str, Any]:
        r = await self._client.get(f"/_admin/state/{portal}")
        r.raise_for_status()
        return r.json()

    async def chaos(self) -> list[dict[str, Any]]:
        r = await self._client.get("/_admin/chaos")
        r.raise_for_status()
        return r.json()

    async def seed_of(self, portal: str) -> int:
        for row in await self.chaos():
            if row["portal"] == portal:
                return int(row["seed"])
        return 0

    async def set_chaos(self, portal: str, seed: int) -> dict[str, Any]:
        r = await self._client.post("/_admin/chaos", json={"portal": portal, "seed": seed})
        r.raise_for_status()
        return r.json()

    async def reset(self) -> None:
        (await self._client.post("/_admin/reset")).raise_for_status()
