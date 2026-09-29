from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ORDERS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_url: str = Field(
        default="http://127.0.0.1:8000",
    )

    api_timeout: float = Field(
        default=10.0,
        gt=0,
    )

    jwt_secret: str = Field(
        min_length=32,
    )

    jwt_algorithm: str = "HS256"

    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
