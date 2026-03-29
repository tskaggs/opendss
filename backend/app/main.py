from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings
from app.core.http import create_async_client
from app.core.middleware import SecurityHeadersMiddleware
from app.limiter import limiter
from app.routers import analyze, health

logger = logging.getLogger(__name__)
settings = get_settings()

docs_url = "/docs" if not settings.is_production else None
redoc_url = "/redoc" if not settings.is_production else None
openapi_url = "/openapi.json" if not settings.is_production else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.is_production and not settings.cors_origins_list:
        raise RuntimeError(
            "CORS_ORIGINS must list at least one browser origin when ENVIRONMENT=production"
        )
    app.state.http_client = create_async_client()
    logger.info(
        "OpenDSS API starting (environment=%s, cors_origins=%s)",
        settings.environment,
        len(settings.cors_origins_list),
    )
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(
    title="OpenDSS Field API",
    version="0.1.0",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SecurityHeadersMiddleware)

if settings.trusted_hosts_list:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts_list)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(health.router)
app.include_router(analyze.router)
