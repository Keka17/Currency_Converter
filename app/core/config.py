from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Currency Converter API"
    debug: bool = True

    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    # JWT | Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 200
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # External API
    API_KEY: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    """
    Cache settings: they are created only once
    during the entipe app's runtime.
    """
    return Settings()