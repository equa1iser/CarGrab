import json
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://cargrab:secret@localhost:5432/cargrab"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # CORS — accepts JSON array string or comma-separated plain string
    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return [str(v)]

    # Data source keys
    marketcheck_api_key: str = ""
    carvana_api_key: str = ""
    autodev_api_key: str = ""
    ebay_app_id: str = ""
    ebay_cert_id: str = ""

    # NHTSA (no key needed)
    nhtsa_api_base: str = "https://vpic.nhtsa.dot.gov/api"
    nhtsa_recalls_base: str = "https://api.nhtsa.gov/recalls"

    # Google OAuth
    google_client_id: str = ""

    # SMTP (for password reset emails — leave blank in dev to log links to console)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@cargrab.com"
    app_url: str = "http://localhost:3000"

    # Sentry
    sentry_dsn: str = ""

    # Admin access — comma-separated emails or JSON array
    admin_emails: list[str] = []

    @field_validator("admin_emails", mode="before")
    @classmethod
    def parse_admin_emails(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [e.strip().lower() for e in v.split(",") if e.strip()]
        return []


settings = Settings()
