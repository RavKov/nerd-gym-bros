import os

from django.core.exceptions import ImproperlyConfigured

TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


def env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False

    raise ImproperlyConfigured(
        f"{name} must be one of: {', '.join(sorted(TRUE_VALUES | FALSE_VALUES))}."
    )


def env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} must be an integer.") from exc


def require_env(name: str) -> str:
    raw_value = os.getenv(name, "").strip()
    if not raw_value:
        raise ImproperlyConfigured(f"{name} must be set.")
    return raw_value
