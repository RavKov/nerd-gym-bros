import importlib

import pytest
from django.core.exceptions import ImproperlyConfigured


def load_settings_module(module_name: str):
    importlib.reload(importlib.import_module("gymProj.settings.base"))
    return importlib.reload(importlib.import_module(module_name))


def set_required_production_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DJANGO_SECRET_KEY", "test-secret")
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "api.example.com")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.example.com")


def clear_email_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [
        "DJANGO_DEFAULT_FROM_EMAIL",
        "DJANGO_SERVER_EMAIL",
        "DJANGO_EMAIL_SUBJECT_PREFIX",
        "EMAIL_BACKEND",
        "EMAIL_HOST",
        "EMAIL_PORT",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
        "EMAIL_USE_TLS",
        "EMAIL_USE_SSL",
        "EMAIL_TIMEOUT",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_development_uses_console_email_backend_by_default(monkeypatch: pytest.MonkeyPatch):
    clear_email_env(monkeypatch)

    settings_module = load_settings_module("gymProj.settings.development")

    assert settings_module.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend"
    assert settings_module.DEFAULT_FROM_EMAIL == "Nerd Gym Bros <no-reply@localhost>"
    assert settings_module.SERVER_EMAIL == settings_module.DEFAULT_FROM_EMAIL


def test_production_configures_smtp_email_settings(monkeypatch: pytest.MonkeyPatch):
    clear_email_env(monkeypatch)
    set_required_production_env(monkeypatch)
    monkeypatch.setenv("DJANGO_DEFAULT_FROM_EMAIL", "Nerd Gym Bros <no-reply@example.com>")
    monkeypatch.setenv("EMAIL_HOST", "smtp.example.com")
    monkeypatch.setenv("EMAIL_PORT", "587")
    monkeypatch.setenv("EMAIL_USE_TLS", "true")
    monkeypatch.setenv("EMAIL_USE_SSL", "false")

    settings_module = load_settings_module("gymProj.settings.production")

    assert settings_module.EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend"
    assert settings_module.DEFAULT_FROM_EMAIL == "Nerd Gym Bros <no-reply@example.com>"
    assert settings_module.SERVER_EMAIL == settings_module.DEFAULT_FROM_EMAIL
    assert settings_module.EMAIL_HOST == "smtp.example.com"
    assert settings_module.EMAIL_PORT == 587
    assert settings_module.EMAIL_USE_TLS is True
    assert settings_module.EMAIL_USE_SSL is False


def test_production_requires_default_from_email(monkeypatch: pytest.MonkeyPatch):
    clear_email_env(monkeypatch)
    set_required_production_env(monkeypatch)
    monkeypatch.setenv("EMAIL_HOST", "smtp.example.com")

    with pytest.raises(ImproperlyConfigured, match="DJANGO_DEFAULT_FROM_EMAIL"):
        load_settings_module("gymProj.settings.production")


def test_production_rejects_conflicting_tls_and_ssl(monkeypatch: pytest.MonkeyPatch):
    clear_email_env(monkeypatch)
    set_required_production_env(monkeypatch)
    monkeypatch.setenv("DJANGO_DEFAULT_FROM_EMAIL", "Nerd Gym Bros <no-reply@example.com>")
    monkeypatch.setenv("EMAIL_HOST", "smtp.example.com")
    monkeypatch.setenv("EMAIL_USE_TLS", "true")
    monkeypatch.setenv("EMAIL_USE_SSL", "true")

    with pytest.raises(ImproperlyConfigured, match="EMAIL_USE_TLS and EMAIL_USE_SSL"):
        load_settings_module("gymProj.settings.production")
