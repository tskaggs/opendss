"""Shared rate limiter instance (see `app.main` for FastAPI wiring)."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.config import get_settings


def _rate_limit_key(request: Request) -> str:
    if get_settings().trust_forwarded_for:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            client = xff.split(",")[0].strip()
            if client:
                return client
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key)
