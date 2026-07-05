"""
Utilitaires partagés pour les services de paiement.
"""
import hashlib
import hmac
import re

from django.conf import settings


def _get_webhook_secret() -> str:
    """Retourne le secret partagé configuré pour signer les callbacks."""
    return getattr(settings, "PAYMENTS", {}).get("WEBHOOK_SECRET", "") or ""


def compute_webhook_signature(raw_body: bytes, secret: str = "") -> str:
    """Calcule la signature HMAC-SHA256 hexadécimale d'un corps de requête brut."""
    secret = secret or _get_webhook_secret()
    if isinstance(raw_body, str):
        raw_body = raw_body.encode("utf-8")
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def verify_webhook_signature(raw_body: bytes, provided_signature: str) -> bool:
    """
    Vérifie la signature HMAC-SHA256 d'un callback provider en temps constant.

    Retourne False si aucun secret n'est configuré ou si la signature est absente
    ou invalide (fail-closed).
    """
    secret = _get_webhook_secret()
    if not secret or not provided_signature:
        return False

    # Certains providers préfixent la signature (ex: "sha256=..."). On normalise.
    provided = provided_signature.strip()
    if "=" in provided:
        provided = provided.split("=", 1)[1]

    expected = compute_webhook_signature(raw_body, secret)
    return hmac.compare_digest(expected, provided)


def normaliser_telephone(telephone: str) -> str:
    """Normalise un numéro au format international (+228XXXXXXXX)."""
    cleaned = re.sub(r"[\s\-\.\(\)]", "", telephone)
    if cleaned.startswith("+"):
        cleaned_digits = cleaned[1:]
    else:
        cleaned_digits = cleaned

    if cleaned_digits.startswith("00228"):
        return "+228" + cleaned_digits[5:]
    if cleaned_digits.startswith("228"):
        return "+228" + cleaned_digits[3:]
    if cleaned_digits.startswith("0"):
        return "+228" + cleaned_digits[1:]
    if len(cleaned_digits) == 8 and cleaned_digits.isdigit():
        return "+228" + cleaned_digits
    # Already international format
    return "+" + cleaned_digits