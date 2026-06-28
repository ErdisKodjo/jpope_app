"""
Service de paiement — orchestrateur principal.
Intègre Flooz (Togocom) et TMoney.
"""
import logging
import secrets

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Orchestrateur de paiements mobile money (Flooz, TMoney).
    """

    @classmethod
    @transaction.atomic
    def initier_paiement(
        cls,
        utilisateur,
        plan_id: str,
        methode_paiement: str,
        telephone: str = "",
        description: str = "",
        metadata: dict = None,
    ):
        """
        Initie un paiement pour un plan d'abonnement.

        Args:
            utilisateur: User effectuant le paiement
            plan_id: UUID du plan d'abonnement
            methode_paiement: FLOOZ, TMONEY, MOOV_MONEY, CARTE
            telephone: Numéro de téléphone (requis pour Mobile Money)
            description: Description du paiement
            metadata: Données additionnelles

        Returns:
            dict avec reference, statut, code_ussd (si MM)
        """
        from apps.payments.models import PlanAbonnement, Paiement

        try:
            plan = PlanAbonnement.objects.get(id=plan_id, is_active=True)
        except PlanAbonnement.DoesNotExist:
            raise ValueError(f"Plan {plan_id} introuvable ou inactif.")

        # Générer une référence unique
        today = timezone.now().strftime("%Y%m%d")
        reference = f"PAY-{today}-{secrets.token_hex(4).upper()}"

        # Créer le paiement en attente
        paiement = Paiement.objects.create(
            user=utilisateur,
            montant=plan.prix_actuel,
            devise=plan.devise,
            statut="PENDING",
            provider=methode_paiement,
            reference=reference,
            description=description or f"Abonnement {plan.nom}",
            metadata=metadata or {
                "plan_id": str(plan.id),
                "plan_code": plan.code,
                "utilisateur_email": utilisateur.email,
                "ip": metadata.get("ip", "") if metadata else "",
            },
        )

        result = {
            "reference": reference,
            "statut": "PENDING",
            "montant": int(plan.prix_actuel),
            "montant_formate": paiement.montant_formate,
            "methode_paiement": methode_paiement,
            "message": "Paiement initié avec succès.",
            "code_ussd": None,
            "telephone": None,
            "client_secret": None,
        }

        # Dispatcher vers le bon provider
        if methode_paiement in ["FLOOZ", "TMONEY", "MOOV_MONEY"]:
            if not telephone:
                raise ValueError("Le téléphone est requis pour Mobile Money.")

            mm_result = cls._initier_mobile_money(
                paiement, telephone, methode_paiement
            )
            result.update(mm_result)

        elif methode_paiement == "CARTE":
            stripe_result = cls._initier_stripe(paiement)
            result.update(stripe_result)

        logger.info(
            f"Paiement initié : {reference} — "
            f"{plan.prix_actuel} XOF — {methode_paiement}"
        )

        return result

    @classmethod
    def verifier_statut(cls, reference: str) -> dict:
        """Vérifie le statut d'une transaction."""
        from apps.payments.models import Paiement

        try:
            paiement = Paiement.objects.get(reference=reference)
        except Paiement.DoesNotExist:
            raise ValueError(f"Transaction {reference} introuvable.")

        # Vérifier auprès du provider si toujours en attente
        if paiement.statut == "PENDING" and paiement.provider in ["FLOOZ", "TMONEY"]:
            cls._verifier_aupres_provider(paiement)
            paiement.refresh_from_db()

        return {
            "reference": paiement.reference,
            "statut": paiement.statut,
            "montant": int(paiement.montant),
            "montant_formate": paiement.montant_formate,
            "provider": paiement.provider,
            "transaction_id": paiement.transaction_id,
            "created_at": str(paiement.created_at),
            "updated_at": str(paiement.updated_at),
        }

    @classmethod
    def confirmer_paiement(cls, reference: str, transaction_id: str = "") -> bool:
        """Confirme un paiement (callback du provider)."""
        from apps.payments.models import Paiement

        try:
            paiement = Paiement.objects.get(reference=reference)
        except Paiement.DoesNotExist:
            logger.error(f"Paiement {reference} introuvable pour confirmation")
            return False

        if paiement.statut == "COMPLETED":
            logger.info(f"Paiement {reference} déjà confirmé")
            return True

        paiement.statut = "COMPLETED"
        if transaction_id:
            paiement.transaction_id = transaction_id
        paiement.save(update_fields=["statut", "transaction_id", "updated_at"])

        # Créer/renouveler l'abonnement
        cls._activer_abonnement(paiement)

        logger.info(f"Paiement {reference} confirmé")
        return True

    @classmethod
    def annuler_paiement(cls, reference: str, motif: str = "") -> bool:
        """Annule un paiement en attente."""
        from apps.payments.models import Paiement

        try:
            paiement = Paiement.objects.get(reference=reference)
        except Paiement.DoesNotExist:
            return False

        if paiement.statut not in ["PENDING"]:
            logger.warning(
                f"Impossible d'annuler {reference} — statut: {paiement.statut}"
            )
            return False

        paiement.statut = "FAILED"
        if motif:
            paiement.metadata["motif_annulation"] = motif
        paiement.save(update_fields=["statut", "metadata", "updated_at"])

        logger.info(f"Paiement {reference} annulé : {motif}")
        return True

    @classmethod
    def _initier_mobile_money(
        cls,
        paiement,
        telephone: str,
        methode: str,
    ) -> dict:
        """Initie un paiement Mobile Money."""
        if methode == "FLOOZ":
            from apps.payments.services.flooz_service import FloozService
            return FloozService.initier_paiement(paiement, telephone)
        elif methode == "TMONEY":
            from apps.payments.services.tmoney_service import TMoneyService
            return TMoneyService.initier_paiement(paiement, telephone)
        else:
            # Autres opérateurs — mode mock pour l'instant
            logger.info(f"[MOCK {methode}] Paiement initié pour {telephone}")
            return {
                "code_ussd": f"*145*2*{int(paiement.montant)}*123456#",
                "telephone": telephone,
                "message": f"Composez le code USSD pour confirmer votre paiement {methode}.",
            }

    @classmethod
    def _initier_stripe(cls, paiement) -> dict:
        """Initie un paiement Stripe (carte bancaire)."""
        try:
            from apps.payments.services.stripe_service import StripeService
            return StripeService.creer_payment_intent(paiement)
        except Exception as e:
            logger.error(f"Erreur Stripe : {e}")
            return {
                "client_secret": None,
                "message": "Erreur lors de l'initiation du paiement carte.",
            }

    @classmethod
    def _verifier_aupres_provider(cls, paiement):
        """Vérifie le statut auprès du provider."""
        logger.debug(f"Vérification statut {paiement.reference} auprès du provider")
        # Implémentation provider-spécifique

    @classmethod
    def _activer_abonnement(cls, paiement):
        """Active ou renouvelle l'abonnement après paiement réussi."""
        from apps.payments.models import PlanAbonnement, Abonnement, StatutAbonnement
        from datetime import timedelta

        plan_id = paiement.metadata.get("plan_id")
        if not plan_id:
            logger.warning(f"Pas de plan_id dans metadata de {paiement.reference}")
            return

        try:
            plan = PlanAbonnement.objects.get(id=plan_id)
        except PlanAbonnement.DoesNotExist:
            logger.error(f"Plan {plan_id} introuvable")
            return

        now = timezone.now()
        date_fin = now + timedelta(days=plan.duree_mois * 30)

        abonnement, created = Abonnement.objects.get_or_create(
            utilisateur=paiement.user,
            plan=plan,
            statut__in=[StatutAbonnement.ACTIF, StatutAbonnement.EN_PERIODE_ESSAI],
            defaults={
                "statut": StatutAbonnement.ACTIF,
                "date_debut": now,
                "date_fin": date_fin,
                "date_dernier_paiement": now,
            },
        )

        if not created:
            # Renouvellement
            abonnement.date_fin = date_fin
            abonnement.statut = StatutAbonnement.ACTIF
            abonnement.date_dernier_paiement = now
            abonnement.nombre_renouvellements += 1
            abonnement.save(update_fields=[
                "date_fin", "statut", "date_dernier_paiement",
                "nombre_renouvellements", "updated_at",
            ])

        logger.info(
            f"Abonnement {'créé' if created else 'renouvelé'} pour "
            f"{paiement.user.email} — {plan.nom}"
        )
