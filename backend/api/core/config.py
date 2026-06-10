"""Application configuration, loaded once from the environment.

Values come from the process environment, with `.env` loaded as a fallback
so local development works without exporting anything.
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Budget Planner API"
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./budget.db")
    )
    cors_origins: list[str] = field(
        default_factory=lambda: _csv_env("CORS_ORIGINS", "http://localhost:5173")
    )
    # Signs JWTs — anyone who knows it can forge logins. The default is for
    # local development only; always set SECRET_KEY in production.
    secret_key: str = field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", "insecure-dev-only-secret-change-in-production"
        )
    )
    access_token_expire_days: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "30"))
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
