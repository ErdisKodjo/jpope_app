"""
Service T-Money — paiements Mobile Money Togo.
"""
import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)


class TMoneyService:
    """
    Intégration avec l'API T-Money (Atlantique Telecom Togo).
    """

    @classmethod
    def _get_settings(cls):
        return getattr(settings, "PAYMENTS", {})

    @classmethod
    @property
    def API_URL(cls):
        return cls._get_settings().get("TMONEY_API_URL", "https://api.tmoney.tg/v1")

    @classmethod
    @property
    def API_KEY(cls):
        return cls._get_settings().get("TMONEY_API_KEY", "")

    @classmethod
    @property
    def MERCHANT_ID(cls):
        return cls._get_settings().get("TMONEY_MERCHANT_ID", "")

    @classmethod
    @property
    def MOCK_MODE(cls):
        return cls._get_settings().get("TMONEY_MOCK_MODE", False)

    @classmethod
    def initier_paiement(cls, paiement, telephone: str) -> dict:
        """
        Initie un paiement T-Money.

        Returns:
            dict avec code_ussd, telephone, message
        """
        telephone_normalized = cls._normaliser_telephone(telephone)

        if cls.MOCK_MODE or not cls.API_KEY:
            return cls._mock_paiement(paiement, telephone_normalized)

        try:
            return cls._appel_api(paiement, telephone_normalized)
        except Exception as e:
            logger.error(f"Erreur T-Money API: {e}", exc_info=True)
            raise ValueError("Le service T-Money est temporairement indisponible. Veuillez réessayer.") from e

    @classmethod
    def verifier_statut(cls, reference: str) -> dict:
        """Vérifie le statut d'une transaction T-Money."""
        if cls.MOCK_MODE or not cls.API_KEY:
            return {"statut": "PENDING", "message": "Mode mock actif"}

        try:
            import requests
            response = requests.get(
                f"{cls.API_URL}/transactions/{reference}",
                headers={"X-API-Key": cls.API_KEY},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "statut": cls._mapper_statut(data.get("status")),
                    "transaction_id": data.get("transaction_id", ""),
                    "message": data.get("message", ""),
                }
        except Exception as e:
            logger.error(f"Erreur vérification T-Money: {e}")

        return {"statut": "PENDING", "message": "Erreur lors de la vérification"}

    @classmethod
    def _appel_api(cls, paiement, telephone: str) -> dict:
        """Appel réel à l'API T-Money."""
        import requests

        payload = {
            "merchant_id": cls.MERCHANT_ID,
            "msisdn": telephone,
            "amount": int(paiement.montant),
            "currency": "XOF",
            "order_id": paiement.reference,
            "description": paiement.description or "Abonnement AvenSU-Orienta",
            "callback_url": getattr(settings, "TMONEY_CALLBACK_URL", ""),
        }

        response = requests.post(
            f"{cls.API_URL}/payment/request",
            json=payload,
            headers={
                "X-API-Key": cls.API_KEY,
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if response.status_code in [200, 201]:
            data = response.json()
            return {
                "code_ussd": data.get("ussd_string", ""),
                "telephone": telephone,
                "message": data.get(
                    "message",
                    "Confirmez le paiement sur votre téléphone T-Money.",
                ),
                "tmoney_session": data.get("session_id", ""),
            }
        else:
            raise Exception(
                f"T-Money API error {response.status_code}: {response.text[:200]}"
            )

    @classmethod
    def _mock_paiement(cls, paiement, telephone: str) -> dict:
        """Mode mock pour développement et test."""
        logger.info(
            f"[TMONEY MOCK] Paiement {paiement.reference} — "
            f"{paiement.montant} XOF → {telephone}"
        )
        code_ussd = f"*155*1*{int(paiement.montant)}*{paiement.reference[-6:]}#"
        return {
            "code_ussd": code_ussd,
            "telephone": telephone,
            "message": (
                f"[TEST] Composez {code_ussd} depuis votre téléphone T-Money "
                f"pour confirmer le paiement de {int(paiement.montant)} XOF."
            ),
        }

    @classmethod
    def _normaliser_telephone(cls, telephone: str) -> str:
        """Normalise un numéro au format international (+228XXXXXXXX)."""
        # Remove all non-digit characters except leading +
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

    @staticmethod
    def _mapper_statut(statut_api: str) -> str:
        """Mappe le statut T-Money vers le statut interne."""
        mapping = {
            "SUCCESSFUL": "COMPLETED",
            "FAILED": "FAILED",
            "PENDING": "PENDING",
            "TIMEOUT": "FAILED",
        }
        return mapping.get(str(statut_api).upper(), "PENDING")
