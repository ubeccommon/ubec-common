"""
Module: clients/hub_client.py
Service: erdpuls
Purpose: Async HTTP client for the UBEC Hub API (iot.ubec.network).
         All cross-service data requests route through the Hub (§2 dependency graph).
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import httpx
from aiolimiter import AsyncLimiter

from config import settings
from models.exceptions import HubConnectionError


# Rate limit: max 30 requests/minute to Hub API (Principle #9)
_rate_limiter = AsyncLimiter(max_rate=30, time_period=60)


class HubClient:
    """Async client for the UBEC Hub REST API."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def setup(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.HUB_API_URL,
            headers={
                "X-API-Key": settings.HUB_API_KEY,
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(10.0),
        )

    async def teardown(self) -> None:
        if self._client:
            await self._client.aclose()

    async def get(self, path: str, **kwargs) -> dict:
        """GET a Hub API endpoint with rate limiting."""
        if not self._client:
            raise HubConnectionError("HubClient not initialised — call setup() first.")
        async with _rate_limiter:
            try:
                response = await self._client.get(path, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException as exc:
                raise HubConnectionError(f"Hub API timed out: {path}") from exc
            except httpx.HTTPStatusError as exc:
                raise HubConnectionError(
                    f"Hub API returned {exc.response.status_code}: {path}"
                ) from exc
