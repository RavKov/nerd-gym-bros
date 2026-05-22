"""
Local development settings. Default when DJANGO_ENV is unset or "development".
"""

import os

from .base import *  # noqa: F403

DEBUG = True

# Dev-only fallback; override via DJANGO_SECRET_KEY in .env for local teams.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-do-not-use-in-production",
)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "localhost,127.0.0.1,0.0.0.0,[::1]",
    ).split(",")
    if h.strip()
]

_default_cors_origins = "http://localhost:8081,http://127.0.0.1:8081,http://10.0.2.2:8000"
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ALLOWED_ORIGINS", _default_cors_origins).split(",")
    if o.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv("CSRF_TRUSTED_ORIGINS", _default_cors_origins).split(",")
    if o.strip()
]
