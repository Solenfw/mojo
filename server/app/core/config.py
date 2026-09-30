"""
All configuration comes from environment variables. Locally, the Makefile supplies them from the
secrets file with `uv run --env-file`; elsewhere, set them in the process environment.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = Field(min_length=32)  # signs access tokens; generate with `openssl rand -hex 32`
    algorithm: str = "HS256"
    database_url: str
    frontend_origins: list[str] = ["http://localhost:3000"]  # JSON list, e.g. ["https://app.example.com"]

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    refresh_cookie_secure: bool = False  # set true anywhere served over HTTPS
    refresh_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    gemini_api_key: str | None = None  # unset: AI features fall back to canned responses


settings = Settings()
