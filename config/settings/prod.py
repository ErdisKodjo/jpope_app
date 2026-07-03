"""
Settings spécifiques à la production.
"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa

DEBUG = False

# Render termine le SSL au load balancer et transmet en HTTP en interne.
# Sans cela, SECURE_SSL_REDIRECT crée une boucle infinie de redirections.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Sécurité renforcée
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = "DENY"

# Static files via WhiteNoise (déjà configuré en base)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Stockage média S3/MinIO en production
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")  # noqa: F405
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")  # noqa: F405
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME", "avensu-media")  # noqa: F405
AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "eu-west-3")  # noqa: F405
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")  # noqa: F405
AWS_DEFAULT_ACL = "private"
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True

# Logging JSON structuré
LOGGING["formatters"]["default"] = LOGGING["formatters"]["json"]  # noqa: F405
LOGGING["handlers"]["console"]["formatter"] = "json"  # noqa: F405

# Sentry
if SENTRY_DSN := os.environ.get("SENTRY_DSN"):  # noqa: F405
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment="production",
    )
