"""
Tâches Celery pour l'app payments.
"""
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(queue="payments")
def verifier_transactions_en_attente():
    """
    Vérifie le statut des transactions en attente auprès des providers.
    Planifiée toutes les 5 minutes.
    """
    from apps.payments.models import Paiement
    from apps.payments.services import PaymentService

    # Transactions en attente depuis plus de 2 minutes et moins de 30 min
    seuil_min = timezone.now() - timezone.timedelta(minutes=30)
    seuil_max = timezone.now() - timezone.timedelta(minutes=2)

    transactions = Paiement.objects.filter(
        statut="PENDING",
        created_at__gte=seuil_min,
        created_at__lte=seuil_max,
        provider__in=["FLOOZ", "TMONEY", "MOOV_MONEY"],
    )

    nb_verifiees = 0
    nb_confirmees = 0

    for txn in transactions:
        try:
            result = PaymentService.verifier_statut(txn.reference)
            if result.get("statut") == "COMPLETED":
                PaymentService.confirmer_paiement(
                    txn.reference,
                    result.get("transaction_id", ""),
                )
                nb_confirmees += 1
            nb_verifiees += 1
        except Exception as e:
            logger.error(f"Erreur vérification {txn.reference}: {e}")

    logger.info(
        f"{nb_verifiees} transactions vérifiées, {nb_confirmees} confirmées"
    )
    return {"verifiees": nb_verifiees, "confirmees": nb_confirmees}


@shared_task(queue="payments")
def verifier_abonnements_expires():
    """Met à jour le statut des abonnements expirés."""
    from apps.payments.models import Abonnement, StatutAbonnement

    nb_expires = Abonnement.objects.filter(
        statut=StatutAbonnement.ACTIF,
        date_fin__lte=timezone.now(),
        renouvellement_auto=False,
    ).update(statut=StatutAbonnement.EXPIRE)

    logger.info(f"{nb_expires} abonnements marqués comme expirés")
    return nb_expires


@shared_task(queue="payments")
def notifier_abonnements_bientot_expires():
    """Notifie les utilisateurs dont l'abonnement expire dans 7 jours."""
    from apps.payments.models import Abonnement, StatutAbonnement

    limite = timezone.now() + timezone.timedelta(days=7)

    abonnements = Abonnement.objects.filter(
        statut=StatutAbonnement.ACTIF,
        date_fin__lte=limite,
        date_fin__gt=timezone.now(),
        renouvellement_auto=False,
    ).select_related("utilisateur", "plan")

    nb_notifies = 0
    for abonnement in abonnements:
        try:
            from apps.notifications.models import Notification, TypeNotification
            Notification.objects.get_or_create(
                user=abonnement.utilisateur,
                type_notification=TypeNotification.PERSONNALISEE,
                titre=f"Votre abonnement expire bientôt",
                defaults={
                    "message": (
                        f"Bonjour {abonnement.utilisateur.first_name},\n\n"
                        f"Votre abonnement {abonnement.plan.nom} expire dans "
                        f"{abonnement.jours_restants} jour(s).\n\n"
                        f"Pensez à le renouveler !"
                    ),
                    "action_url": "/payments/abonnement/",
                },
            )
            nb_notifies += 1
        except Exception as e:
            logger.error(f"Erreur notification expiration: {e}")

    logger.info(f"{nb_notifies} notifications d'expiration envoyées")
    return nb_notifies


@shared_task(queue="payments")
def renouveler_abonnements_auto():
    """Lance le renouvellement automatique des abonnements."""
    from apps.payments.models import Abonnement, StatutAbonnement

    limite = timezone.now() + timezone.timedelta(days=3)

    abonnements = Abonnement.objects.filter(
        statut=StatutAbonnement.ACTIF,
        renouvellement_auto=True,
        date_fin__lte=limite,
        date_fin__gt=timezone.now(),
    ).select_related("utilisateur", "plan")

    nb_renouveles = 0
    for abonnement in abonnements:
        try:
            # TODO: Implémenter le prélèvement automatique
            logger.info(
                f"Renouvellement automatique à traiter : "
                f"{abonnement.utilisateur.email} — {abonnement.plan.nom}"
            )
            nb_renouveles += 1
        except Exception as e:
            logger.error(f"Erreur renouvellement auto: {e}")

    logger.info(f"{nb_renouveles} renouvellements traités")
    return nb_renouveles


@shared_task(queue="payments")
def expirer_transactions_anciennes():
    """Expire les transactions en attente de plus de 30 minutes."""
    from apps.payments.models import Paiement

    seuil = timezone.now() - timezone.timedelta(minutes=30)

    count = Paiement.objects.filter(
        statut="PENDING",
        created_at__lt=seuil,
    ).update(statut="FAILED")

    logger.info(f"{count} transactions expirées")
    return count


@shared_task(queue="payments")
def statistiques_paiements():
    """Calcule les statistiques de paiements du jour."""
    from apps.payments.models import Paiement

    aujourdhui = timezone.now().date()

    stats_jour = Paiement.objects.filter(
        statut="COMPLETED",
        updated_at__date=aujourdhui,
    )

    nb_transactions = stats_jour.count()
    total_fcfa = sum(p.montant for p in stats_jour)

    logger.info(
        f"Stats paiements aujourd'hui : "
        f"{nb_transactions} transactions, {total_fcfa} XOF"
    )

    return {
        "date": str(aujourdhui),
        "nb_transactions": nb_transactions,
        "total_fcfa": float(total_fcfa),
    }
