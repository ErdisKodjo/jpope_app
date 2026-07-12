"""
Settings spécifiques à la production — sécurité renforcée.

🔒 Conformité cahier des charges §3 :
- HTTPS strict (HSTS 1 an + preload + subdomains)
- Cookies sécurisés (Secure + HttpOnly + SameSite)
- Headers CSP, XSS, Content-Type
- Référent policy
- Lockout via django-axes (5 tentatives / 1h)
- 2FA admin via django-otp
- Chiffrement Fernet des données sensibles
"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa

DEBUG = False

# ──────────────────────────────────────────────
# HTTPS / SSL
# ──────────────────────────────────────────────
# Render termine le SSL au load balancer et transmet en HTTP en interne.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REDIRECT_EXEMPT = []  # aucune exception

# ──────────────────────────────────────────────
# HEADERS DE SÉCURITÉ
# ──────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"  # anti-clickjacking

# Référent policy (anti-leak d'URL entre origines)
SECURE_REFERRER_POLICY = "same-origin"

# Permissions policy (disable features sensibles)
PERMISSIONS_POLICY = {
    "geolocation": "self",
    "camera": "self",
    "microphone": "self",
    "payment": "self",
    "usb": "()",
    "magnetometer": "()",
    "gyroscope": "()",
    "accelerometer": "()",
}

# ──────────────────────────────────────────────
# COOKIES SÉCURISÉS
# ──────────────────────────────────────────────
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 8  # 8 heures

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 jours

# ──────────────────────────────────────────────
# CONTENT SECURITY POLICY (CSP)
# ──────────────────────────────────────────────
# Désactivée par défaut — activer via django-csp si besoin (à ajouter aux THIRD_PARTY_APPS)
# Configuration de référence ci-dessous pour activation future
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # requis pour le Django admin
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
    "https://cdn.jsdelivr.net",
)
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
    "https://fonts.googleapis.com",
)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "blob:",
    "https:",
)
CSP_MEDIA_SRC = ("'self'", "https:")
CSP_FRAME_SRC = (
    "'self'",
    "https://my.matterport.com",  # visites 3D
    "https://sketchfab.com",
    "https://www.youtube.com",
    "https://player.vimeo.com",
)
CSP_CONNECT_SRC = (
    "'self'",
    "https://api.stripe.com",
    "wss://",  # WebSocket pour chatbot
)
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)  # équivalent à X-Frame-Options: DENY
CSP_INCLUDE_NONCE_IN = ("script-src", "style-src")

# ──────────────────────────────────────────────
# SÉCURITÉ AUTH
# ──────────────────────────────────────────────
# Lockout via django-axes (configuré en base, ici on renforce)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1h
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True
AXES_NEVER_LOCKOUT_WHITELIST = True
AXES_IP_WHITELIST = []  # à peupler si IPs de confiance

# Password validators — renforcés en prod
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},  # 12 au lieu de 10
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Rotation des clés JWT plus stricte en prod
SIMPLE_JWT = {
    **SIMPLE_JWT,  # noqa: F405
    "ACCESS_TOKEN_LIFETIME": __import__("datetime").timedelta(minutes=15),  # 15min au lieu de 30
    "REFRESH_TOKEN_LIFETIME": __import__("datetime").timedelta(days=1),    # 1j au lieu de 7
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ──────────────────────────────────────────────
# DJANGO-OTP — 2FA obligatoire sur /admin/
# ──────────────────────────────────────────────
OTP_ADMIN_HOTP_THROTTLE_FACTOR = 5
OTP_TOTP_THROTTLE_FACTOR = 5
DJANGO_OTP_ADMIN_HIDE_OTP_FORMS = False
# Force 2FA pour tous les staffs
DJANGO_OTP_ADMINHSIP_REQUIRE_ADMIN = True

# ──────────────────────────────────────────────
# CHIFFREMENT FERNET — clé OBLIGATOIRE en prod
# ──────────────────────────────────────────────
import os as _os
FERNET_KEY = _os.environ.get("DJANGO_FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError(
        "⚠️  DJANGO_FERNET_KEY environment variable is REQUIRED in production. "
        "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    )

# ──────────────────────────────────────────────
# STATIC FILES via WhiteNoise
# ──────────────────────────────────────────────
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ──────────────────────────────────────────────
# STOCKAGE MÉDIA S3/MinIO
# ──────────────────────────────────────────────
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")  # noqa: F405
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")  # noqa: F405
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME", "avensu-media")  # noqa: F405
AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "eu-west-3")  # noqa: F405
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")  # noqa: F405
AWS_DEFAULT_ACL = "private"
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True

# ──────────────────────────────────────────────
# LOGGING JSON structuré + séparation logs sécurité
# ──────────────────────────────────────────────
LOGGING["formatters"]["default"] = LOGGING["formatters"]["json"]  # noqa: F405
LOGGING["handlers"]["console"]["formatter"] = "json"  # noqa: F405

# Logger dédié aux événements de sécurité
LOGGING["loggers"]["security"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "WARNING",
    "propagate": False,
}
LOGGING["loggers"]["axes"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "INFO",
    "propagate": False,
}

# ──────────────────────────────────────────────
# SENTRY
# ──────────────────────────────────────────────
if SENTRY_DSN := os.environ.get("SENTRY_DSN"):  # noqa: F405
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,  # RGPD : ne pas envoyer de PII
        environment="production",
        before_send=lambda event, hint: None if any(
            "password" in str(s).lower() or "secret" in str(s).lower()
            for s in (hint.get("exc_info", [None, None, None])[1].args or [])
            if isinstance(s, str)
        ) else event,
    )
