"""
Service Flooz (Togocom) — paiements Mobile Money Togo.
"""
import logging

from django.conf import settings

from .utils import normaliser_telephone

logger = logging.getLogger(__name__)


class FloozService:
    """
    Intégration avec l'API Flooz de Togocom.
    Documentation : https://developer.togocom.tg/flooz/
    """

    @classmethod
    def _get_settings(cls):
        return getattr(settings, "PAYMENTS", {})

    @classmethod
    def _get_api_url(cls):
        return cls._get_settings().get("FLOOZ_API_URL", "https://api.togocom.tg/flooz/v1")

    @classmethod
    def _get_api_key(cls):
        return cls._get_settings().get("FLOOZ_API_KEY", "")

    @classmethod
    def _get_api_secret(cls):
        return cls._get_settings().get("FLOOZ_API_SECRET", "")

    @classmethod
    def _get_merchant_code(cls):
        return cls._get_settings().get("FLOOZ_MERCHANT_CODE", "")

    @classmethod
    def _is_mock_mode(cls):
        return cls._get_settings().get("FLOOZ_MOCK_MODE", False)

    @classmethod
    def initier_paiement(cls, paiement, telephone: str) -> dict:
        """
        Initie un paiement Flooz.

        Returns:
            dict avec code_ussd, telephone, message
        """
        telephone_normalized = normaliser_telephone(telephone)

        if cls._is_mock_mode() or not cls._get_api_key():
            return cls._mock_paiement(paiement, telephone_normalized)

        try:
            result = cls._appel_api(paiement, telephone_normalized)
            return result
        except Exception as e:
            logger.error(f"Erreur Flooz API: {e}", exc_info=True)
            raise ValueError("Le service Flooz est temporairement indisponible. Veuillez réessayer.") from e

    @classmethod
    def verifier_statut(cls, reference: str) -> dict:
        """Vérifie le statut d'une transaction Flooz."""
        if cls._is_mock_mode() or not cls._get_api_key():
            return {"statut": "PENDING", "message": "Mode mock actif"}

        try:
            import requests
            response = requests.get(
                f"{cls._get_api_url()}/transactions/{reference}",
                headers={"Authorization": f"Bearer {cls._get_api_key()}"},
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
            logger.error(f"Erreur vérification Flooz: {e}")

        return {"statut": "PENDING", "message": "Erreur lors de la vérification"}

    @classmethod
    def _appel_api(cls, paiement, telephone: str) -> dict:
        """Appel réel à l'API Flooz."""
        import requests

        payload = {
            "merchant_code": cls._get_merchant_code(),
            "phone": telephone,
            "amount": int(paiement.montant),
            "currency": paiement.devise,
            "reference": paiement.reference,
            "description": paiement.description or "Abonnement AvenSU-Orienta",
            "callback_url": cls._get_settings().get("FLOOZ_CALLBACK_URL", ""),
        }

        response = requests.post(
            f"{cls._get_api_url()}/payments/initiate",
            json=payload,
            headers={
                "Authorization": f"Bearer {cls._get_api_key()}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if response.status_code in [200, 201, 202]:
            data = response.json()
            return {
                "code_ussd": data.get("ussd_code", ""),
                "telephone": telephone,
                "message": data.get("message", "Composez le code USSD pour confirmer."),
                "flooz_reference": data.get("flooz_reference", ""),
            }
        else:
            raise Exception(
                f"Flooz API error {response.status_code}: {response.text[:200]}"
            )

    @classmethod
    def _mock_paiement(cls, paiement, telephone: str) -> dict:
        """Mode mock pour développement et test."""
        logger.info(
            f"[FLOOZ MOCK] Paiement {paiement.reference} — "
            f"{paiement.montant} XOF → {telephone}"
        )
        code_ussd = f"*145*2*{int(paiement.montant)}*{paiement.reference[-6:]}#"
        return {
            "code_ussd": code_ussd,
            "telephone": telephone,
            "message": (
                f"[TEST] Composez {code_ussd} depuis votre téléphone Flooz "
                f"pour confirmer le paiement de {int(paiement.montant)} XOF."
            ),
        }

    @staticmethod
    def _mapper_statut(statut_api: str) -> str:
        """Mappe le statut Flooz vers le statut interne."""
        mapping = {
            "success": "COMPLETED",
            "failed": "FAILED",
            "pending": "PENDING",
            "expired": "FAILED",
        }
        return mapping.get(str(statut_api).lower(), "PENDING")