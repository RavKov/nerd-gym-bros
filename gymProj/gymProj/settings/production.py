"""
Production settings. Activate with DJANGO_ENV=production.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from . import base as base_settings
from .base import *  # noqa: F403
from .utils import env_bool, env_int, require_env

DEBUG = False
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_ENV=production.")

_allowed = os.getenv("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS must list your domain(s) when DJANGO_ENV=production."
    )

_cors = os.getenv("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors.split(",") if o.strip()]
if not CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured("CORS_ALLOWED_ORIGINS must be set when DJANGO_ENV=production.")

_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(",") if o.strip()]
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = list(CORS_ALLOWED_ORIGINS)

DEFAULT_FROM_EMAIL = require_env("DJANGO_DEFAULT_FROM_EMAIL")
SERVER_EMAIL = os.getenv("DJANGO_SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_HOST = require_env("EMAIL_HOST")
EMAIL_PORT = env_int("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = env_int("EMAIL_TIMEOUT", 10)

if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured("EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be true.")

if EMAIL_HOST_USER and not EMAIL_HOST_PASSWORD:
    raise ImproperlyConfigured("EMAIL_HOST_PASSWORD must be set when EMAIL_HOST_USER is provided.")

MIDDLEWARE = [
    base_settings.MIDDLEWARE[0],
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *base_settings.MIDDLEWARE[1:],
]
STORAGES = {
    **base_settings.STORAGES,
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "true").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

if os.getenv("DJANGO_SECURE_HSTS", "true").lower() == "true":
    SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = os.getenv("DJANGO_SECURE_HSTS_PRELOAD", "false").lower() == "true"
