from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "Vroom Vroom API"
    SECRET_KEY: str = "vroom-insecure-development-secret-key-change-in-production-min-32-chars"

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "vroomvroom"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/vroomvroom"
    DATABASE_URL_SYNC: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/vroomvroom"

    # Security & Tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    COOKIE_NAME: str = "vroom_session"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Domain Business Defaults
    DEFAULT_CITY_CODE: str = "BLR"
    HOLD_EXPIRATION_MINUTES: int = 15
    DEFAULT_COMMISSION_PERCENT: int = 20
    FREE_CANCELLATION_HOURS: int = 24

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
