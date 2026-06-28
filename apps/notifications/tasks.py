"""
Tâches Celery pour l'app notifications.

Inclut envoyer_rappels_j_1 référencé dans config/celery.py beat schedule :
  "envoyer-rappels-evenements": {
      "task": "apps.notifications.tasks.envoyer_rappels_j_1",
      "schedule": crontab(hour=8, minute=0),
  }
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(queue="notifications")
def envoyer_rappels_j_1():
    """
    Envoie les rappels J-1 pour les événements du lendemain.
    Référencé dans config/celery.py sous 'envoyer-rappels-evenements'.
    Planifié tous les jours à 8h00.
    """
    from apps.notifications.models import Notification, TypeNotification

    date_cible = timezone.now() + timedelta(days=1)
    date_debut = date_cible.replace(hour=0, minute=0, second=0, microsecond=0)
    date_fin = date_cible.replace(hour=23, minute=59, second=59, microsecond=999999)

    nb_rappels = 0

    try:
        from apps.events.models import Evenement, InscriptionEvenement, StatutInscription

        evenements = Evenement.objects.filter(
            statut="PUBLIE",
            date_debut__gte=date_debut,
            date_debut__lte=date_fin,
            envoi_rappel_j1=True,
        )

        for evenement in evenements:
            inscriptions = InscriptionEvenement.objects.filter(
                evenement=evenement,
                statut__in=[StatutInscription.INSCRIT, StatutInscription.CONFIRME],
            ).select_related("utilisateur")

            for inscription in inscriptions:
                utilisateur = inscription.utilisateur
                try:
                    Notification.objects.create(
                        user=utilisateur,
                        titre=f"Demain : {evenement.titre}",
                        message=(
                            f"Bonjour {utilisateur.first_name},\n\n"
                            f"L'événement '{evenement.titre}' a lieu DEMAIN !\n\n"
                            f"Date : {evenement.date_debut.strftime('%d/%m/%Y à %H:%M')}\n"
                            f"Lieu : {evenement.lieu_nom or evenement.adresse or 'En ligne'}"
                        ),
                        type_notification=TypeNotification.RAPPEL_EVT_J1,
                        action_url=f"/evenements/{evenement.slug}/",
                    )
                    # Envoyer aussi par email
                    send_notification_email.delay(
                        email=utilisateur.email,
                        subject=f"Demain : {evenement.titre}",
                        message=(
                            f"Bonjour {utilisateur.first_name},\n\n"
                            f"C'est demain ! L'événement '{evenement.titre}'.\n\n"
                            f"Date : {evenement.date_debut.strftime('%d/%m/%Y à %H:%M')}\n"
                            f"Lieu : {evenement.lieu_nom or evenement.adresse or 'En ligne'}"
                        ),
                    )
                    nb_rappels += 1
                except Exception as e:
                    logger.error(
                        f"Erreur envoi rappel J-1 pour {utilisateur.email}: {e}"
                    )

    except ImportError:
        logger.warning(
            "App events non disponible — rappels J-1 simulés"
        )

    logger.info(f"{nb_rappels} rappels J-1 envoyés")
    return nb_rappels


@shared_task(queue="notifications")
def send_notification_email(email: str, subject: str, message: str):
    """
    Envoie un email de notification simple.
    """
    from django.conf import settings
    from django.core.mail import send_mail

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Email envoyé à {email} : {subject}")
        return True
    except Exception as e:
        logger.error(f"Erreur envoi email à {email}: {e}")
        return False


@shared_task(queue="notifications")
def send_bulk_notifications(
    user_ids: list,
    titre: str,
    message: str,
    type_notification: str = "INFO",
    action_url: str = "",
):
    """
    Envoie des notifications en masse à une liste d'utilisateurs.
    """
    from apps.notifications.models import Notification

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        utilisateurs = User.objects.filter(id__in=user_ids, is_active=True)
    except Exception as e:
        logger.error(f"Erreur récupération utilisateurs: {e}")
        return 0

    notifications = []
    for utilisateur in utilisateurs:
        notifications.append(
            Notification(
                user=utilisateur,
                titre=titre,
                message=message,
                type_notification=type_notification,
                action_url=action_url,
            )
        )

    created = Notification.objects.bulk_create(notifications, batch_size=500)
    nb_created = len(created)

    logger.info(
        f"Envoi en masse : {nb_created} notifications créées "
        f"(type: {type_notification})"
    )
    return nb_created


@shared_task(queue="notifications")
def traiter_notifications_en_attente():
    """
    Traite les notifications en attente.
    """
    logger.info("Traitement des notifications en attente")
    return 0


@shared_task(queue="notifications")
def nettoyer_anciennes_notifications(jours: int = 90):
    """Supprime les anciennes notifications lues."""
    from apps.notifications.models import Notification

    seuil = timezone.now() - timezone.timedelta(days=jours)
    count, _ = Notification.objects.filter(
        is_read=True,
        created_at__lt=seuil,
    ).delete()

    logger.info(f"{count} anciennes notifications supprimées")
    return count
