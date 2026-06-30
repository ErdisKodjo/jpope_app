"""
Settings pour le développement local sans Docker (SQLite).
Usage : set DJANGO_SETTINGS_MODULE=config.settings.local
"""
from .dev import *  # noqa

# SQLite — pas besoin de PostgreSQL en local
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# django.contrib.postgres utilise des types PostgreSQL non disponibles sur SQLite
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django.contrib.postgres"]  # noqa: F405
