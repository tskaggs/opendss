"""Application settings from environment (never commit secrets)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load from process env and optional `backend/.env` for local development."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # development | production — production hides API docs by default
    environment: str = "development"

    # Comma-separated browser origins allowed to call the API (CORS)
    cors_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:3001,"
        "http://127.0.0.1:3001"
    )

    # Optional: restrict Host header (e.g. behind a reverse proxy). Empty = disabled.
    trusted_hosts: str = ""

    # slowapi limit for POST /analyze (abuse / upstream cost protection)
    rate_limit_analyze: str = "60/minute"

    # When True, rate limiting uses X-Forwarded-For (first hop). Enable only behind a
    # trusted reverse proxy that sets this header; otherwise clients can spoof IPs.
    trust_forwarded_for: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def trusted_hosts_list(self) -> list[str] | None:
        if not self.trusted_hosts.strip():
            return None
        return [h.strip() for h in self.trusted_hosts.split(",") if h.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
