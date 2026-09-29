import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_url: str
    timeout: float


def load_settings() -> Settings:
    return Settings(
        api_url=os.getenv(
            "ORDERS_API_URL",
            "http://127.0.0.1:8000",
        ),
        timeout=float(
            os.getenv(
                "ORDERS_API_TIMEOUT",
                "10",
            )
        ),
    )
