"""
Select settings module via DJANGO_ENV (development | production).
Defaults to development so local/docker workflows stay unchanged.
"""

import os

_env = os.getenv("DJANGO_ENV", "development").lower()

if _env == "production":
    from .production import *  # noqa: F403
elif _env in ("development", "dev", "local"):
    from .development import *  # noqa: F403
else:
    raise ValueError(
        f"Unknown DJANGO_ENV={_env!r}. Use 'development' or 'production'."
    )
