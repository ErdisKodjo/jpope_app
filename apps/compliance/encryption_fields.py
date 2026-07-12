"""
Champs de chiffrement de bout en bout pour les données sensibles.

Cahier des charges (section 3 — Sécurité) :
"Chiffrement de bout en bout des données sensibles (notes scolaires, rapports psychologiques)."

Utilise cryptography (Fernet — AES 128 en mode CBC + HMAC SHA256).
La clé de chiffrement est configurable via DJANGO_FERNET_KEY (générée avec
`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`).

⚠️ En production, la clé DOIT être stockée dans un KMS (AWS KMS, HashiCorp Vault).
"""
import os
import json
import logging
from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


# ─── Clé de chiffrement ───

def _get_fernet() -> Fernet:
    """Retourne une instance Fernet configurée avec la clé."""
    key = os.environ.get("DJANGO_FERNET_KEY") or getattr(settings, "FERNET_KEY", None)
    if not key:
        # DEV ONLY — génère une clé à la volée
        # ⚠️ En prod, ceci ferait perdre les données chiffrées à chaque redémarrage
        key = Fernet.generate_key().decode()
        logger.warning("⚠️ DJANGO_FERNET_KEY non configurée — utilisation d'une clé éphémère (DEV ONLY)")
    return Fernet(key.encode() if isinstance(key, str) else key)


_fernet_instance = None


def get_fernet() -> Fernet:
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = _get_fernet()
    return _fernet_instance


def encrypt_value(value: str) -> str:
    """Chiffre une chaîne et retourne le token base64."""
    if value is None:
        return None
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_value(token: str) -> str:
    """Déchiffre un token et retourne la chaîne d'origine."""
    if not token:
        return None
    return get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")


# ─── Champs personnalisés ───

class EncryptedTextField(models.TextField):
    """
    TextField chiffré au repos (Fernet).
    Stocke le token base64 dans la DB, déchiffre à la lecture.
    """

    description = "TextField chiffré au repos avec Fernet (AES 128 + HMAC SHA256)"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        try:
            return decrypt_value(value)
        except Exception:
            # Si la valeur n'est pas un token valide (par ex. legacy non chiffré), retourne tel quel
            return value

    def to_python(self, value):
        if value is None:
            return None
        # Si la valeur est déjà déchiffrée (Python object), la retourne telle quelle
        return value

    def get_prep_value(self, value):
        if value is None:
            return None
        # Si la valeur est déjà un token (commence par gAAAAA), ne pas rechiffrer
        if isinstance(value, str) and value.startswith("gAAAAA"):
            return value
        return encrypt_value(value)


class EncryptedJSONField(models.JSONField):
    """
    JSONField chiffré au repos.
    Sérialise en JSON avant de chiffrer.
    """

    description = "JSONField chiffré au repos avec Fernet"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        try:
            decrypted = decrypt_value(value)
            return json.loads(decrypted)
        except Exception:
            # Legacy non chiffré — tente de parser le JSON tel quel
            try:
                return json.loads(value) if isinstance(value, str) else value
            except (json.JSONDecodeError, TypeError):
                return value

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, str) and value.startswith("gAAAAA"):
            return value  # déjà chiffré
        return encrypt_value(json.dumps(value, default=str))


class EncryptedCharField(models.CharField):
    """CharField chiffré au repos."""

    description = "CharField chiffré au repos avec Fernet"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        try:
            return decrypt_value(value)
        except Exception:
            return value

    def to_python(self, value):
        return value if value is None else value

    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, str) and value.startswith("gAAAAA"):
            return value
        return encrypt_value(value)


# ─── Helper ───

def is_encryption_enabled() -> bool:
    """Indique si le chiffrement est configuré (clé présente)."""
    return bool(
        os.environ.get("DJANGO_FERNET_KEY")
        or getattr(settings, "FERNET_KEY", None)
    )
