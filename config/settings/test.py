"""
Settings pour les tests locaux (sans Docker/PostgreSQL).
"""
from .base import *  # noqa

DEBUG = True
SECRET_KEY = "django-insecure-test-key-only-for-local-check"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# SQLite pour les tests sans PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Cache en mémoire
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery synchrone
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Désactiver les apps optionnelles non installées (et django.contrib.postgres qui nécessite psycopg2)
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in [  # noqa: F405
    "debug_toolbar",
    "django_browser_reload",
    "silk",
    "django.contrib.postgres",
]]

# Channels sans Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Logging simplifié (sans pythonjsonlogger non installé)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}

# URL frontend pour les emails (vérification, reset password)
FRONTEND_URL = "http://localhost:8000"
