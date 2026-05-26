import importlib
from pathlib import Path

import pytest


def load_settings_module(module_name: str):
    importlib.reload(importlib.import_module("gymProj.settings.base"))
    return importlib.reload(importlib.import_module(module_name))


def set_required_production_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DJANGO_SECRET_KEY", "test-secret")
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "api.example.com")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.example.com")
    monkeypatch.setenv("DJANGO_DEFAULT_FROM_EMAIL", "Nerd Gym Bros <no-reply@example.com>")
    monkeypatch.setenv("EMAIL_HOST", "smtp.example.com")


def clear_deployment_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [
        "DJANGO_COLLECTSTATIC",
        "DJANGO_STATIC_ROOT",
        "PORT",
        "GUNICORN_WORKERS",
        "GUNICORN_THREADS",
        "GUNICORN_TIMEOUT",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_base_configures_static_root_and_default_staticfiles_storage(
    monkeypatch: pytest.MonkeyPatch,
):
    clear_deployment_env(monkeypatch)
    monkeypatch.setenv("DJANGO_STATIC_ROOT", "/tmp/nerd-gym-bros-static")

    settings_module = load_settings_module("gymProj.settings.base")

    assert settings_module.STATIC_URL == "/static/"
    assert settings_module.STATIC_ROOT == Path("/tmp/nerd-gym-bros-static")
    assert settings_module.STORAGES["staticfiles"]["BACKEND"] == (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )


def test_production_enables_whitenoise_staticfiles_storage(monkeypatch: pytest.MonkeyPatch):
    clear_deployment_env(monkeypatch)
    set_required_production_env(monkeypatch)

    settings_module = load_settings_module("gymProj.settings.production")

    assert settings_module.MIDDLEWARE[1] == "whitenoise.middleware.WhiteNoiseMiddleware"
    assert settings_module.STORAGES["staticfiles"]["BACKEND"] == (
        "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )
