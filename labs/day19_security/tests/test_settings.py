import pytest

from labs.day19_security.settings import Settings


def test_settings_loads_environment_variables(
    monkeypatch,
):
    monkeypatch.setenv(
        "ORDERS_JWT_SECRET",
        "secret-with-at-least-32-characters",
    )
    monkeypatch.setenv(
        "ORDERS_API_TIMEOUT",
        "15",
    )

    settings = Settings()

    assert settings.jwt_secret == ("secret-with-at-least-32-characters")
    assert settings.api_timeout == 15.0


def test_settings_rejects_short_secret(
    monkeypatch,
):
    monkeypatch.setenv(
        "ORDERS_JWT_SECRET",
        "short",
    )

    with pytest.raises(ValueError):
        Settings()
