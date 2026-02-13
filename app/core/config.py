from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    # JWT | Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # External API
    API_KEY: str
    EXTERNAL_API_URL: str = "https://currencyapi.net/api/v1/rates"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # For extra env variable (Docker-specific)
    )


@lru_cache
def get_settings():
    """
    Cache settings: they are created only once
    during the entipe app's runtime.
    """
    return Settings()
