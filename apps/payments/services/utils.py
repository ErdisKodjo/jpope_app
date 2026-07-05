"""
Utilitaires partagés pour les services de paiement.
"""
import re


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