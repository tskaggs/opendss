"""Shared httpx configuration for outbound API calls (timeouts, connection limits)."""

from __future__ import annotations

import httpx

# NASA POWER / SoilGrids responses are small; cap redirect chains and pool size for stability.
_HTTP_TIMEOUT = httpx.Timeout(60.0, connect=15.0)
_HTTP_LIMITS = httpx.Limits(max_connections=32, max_keepalive_connections=10)


def create_async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=_HTTP_TIMEOUT,
        limits=_HTTP_LIMITS,
        follow_redirects=True,
        max_redirects=5,
    )
