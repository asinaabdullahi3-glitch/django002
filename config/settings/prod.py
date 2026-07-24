# flake8: noqa: F405
"""Production settings."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *

# -----------------------------------------------------------------------------
# Production
# -----------------------------------------------------------------------------

DEBUG = False

# PostgreSQL support
INSTALLED_APPS.insert(
    INSTALLED_APPS.index("django.contrib.staticfiles"),
    "django.contrib.postgres",
)

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

if "DATABASE_URL" not in env:
    raise ImproperlyConfigured("DATABASE_URL must be set in production.")

DATABASES = {
    "default": env.db("DATABASE_URL")
}

# -----------------------------------------------------------------------------
# Allowed Hosts
# -----------------------------------------------------------------------------

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[
        "localhost",
        "127.0.0.1",
        "django003.onrender.com",
    ],
)

# Automatically include Render hostname
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if (
    RENDER_EXTERNAL_HOSTNAME
    and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS
):
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# -----------------------------------------------------------------------------
# CSRF
# -----------------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://django003.onrender.com",
    ],
)

if RENDER_EXTERNAL_HOSTNAME:
    render_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)

# -----------------------------------------------------------------------------
# WhiteNoise
# -----------------------------------------------------------------------------

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

# Option 1:
# Use CompressedStaticFilesStorage instead of Manifest storage
# This prevents:
# ValueError: Missing staticfiles manifest entry ...
STORAGES["staticfiles"]["BACKEND"] = (
    "whitenoise.storage.CompressedStaticFilesStorage"
)

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

USE_HTTPS_IN_ABSOLUTE_URLS = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------

ADMINS = [
    "achinga.chris@gmail.com",
]

# -----------------------------------------------------------------------------
# Vercel
# -----------------------------------------------------------------------------

if os.environ.get("VERCEL"):
    MEDIA_ROOT = "/tmp/media"
    CELERY_TASK_ALWAYS_EAGER = True

# -----------------------------------------------------------------------------
# Debug Logging (remove after deployment succeeds)
# -----------------------------------------------------------------------------

print("DEBUG:", DEBUG)
print("ALLOWED_HOSTS:", ALLOWED_HOSTS)
print("CSRF_TRUSTED_ORIGINS:", CSRF_TRUSTED_ORIGINS)