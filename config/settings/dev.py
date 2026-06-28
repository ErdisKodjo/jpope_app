"""
Settings spécifiques au développement local.
"""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "host.docker.internal"]

# Sécurité assouplie en dev
SECRET_KEY = "django-insecure-dev-key-change-in-production-!@#$%"
CORS_ALLOW_ALL_ORIGINS = True

# Email en console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Django Debug Toolbar
INSTALLED_APPS += ["debug_toolbar", "django_browser_reload"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1", "172.0.0.0/8"]

# Logging plus verbeux
LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405

# Silk (profilage)
INSTALLED_APPS += ["silk"]  # noqa: F405
MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")  # noqa: F405
SILKY_PYTHON_PROFILER = True

# Cache en mémoire pour dev
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery en mode eager (synchrone) pour dev
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
