"""
Tâches Celery pour l'app events.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(queue="events")
def mettre_a_jour_statuts_evenements():
    """
    Tâche périodique : met à jour le statut des événements passés.
    """
    from apps.events.models import Evenement, StatutEvenement

    now = timezone.now()
    count = Evenement.objects.filter(
        date_debut__lt=now,
        statut=StatutEvenement.PUBLIE,
    ).exclude(statut=StatutEvenement.TERMINE).update(statut=StatutEvenement.TERMINE)

    if count:
        logger.info(f"{count} événements marqués comme terminés")

    return count


@shared_task(queue="events")
def envoyer_rappels_evenements_j7():
    """Rappels J-7."""
    from apps.events.services import ReminderService
    return ReminderService.envoyer_rappels_j7()


@shared_task(queue="events")
def envoyer_rappels_evenements_j1():
    """Rappels J-1."""
    from apps.events.services import ReminderService
    return ReminderService.envoyer_rappels_j1()


@shared_task(queue="events")
def envoyer_rappels_evenements_j0():
    """Rappels J-0."""
    from apps.events.services import ReminderService
    return ReminderService.envoyer_rappels_j0()


@shared_task(queue="events")
def envoyer_feedback_post_evenement():
    """
    Envoie un email de demande de feedback aux participants
    1 jour après l'événement.
    """
    from apps.events.models import Evenement, InscriptionEvenement, StatutInscription, StatutEvenement
    from django.core.mail import send_mail
    from django.conf import settings

    hier = timezone.now() - timezone.timedelta(days=1)
    date_debut = hier.replace(hour=0, minute=0, second=0)
    date_fin = hier.replace(hour=23, minute=59, second=59)

    evenements = Evenement.objects.filter(
        date_debut__gte=date_debut,
        date_debut__lte=date_fin,
        statut=StatutEvenement.TERMINE,
    )

    nb_envoyes = 0
    for evenement in evenements:
        inscriptions = InscriptionEvenement.objects.filter(
            evenement=evenement,
            statut__in=[StatutInscription.CONFIRME, StatutInscription.PRESENT],
        ).select_related("utilisateur")

        for inscription in inscriptions:
            if inscription.feedback:
                continue  # Déjà répondu

            try:
                send_mail(
                    subject=f"Votre avis sur {evenement.titre}",
                    message=(
                        f"Bonjour {inscription.utilisateur.first_name},\n\n"
                        f"L'événement '{evenement.titre}' a eu lieu hier. "
                        f"Nous espérons qu'il vous a été utile !\n\n"
                        f"Prenez 2 minutes pour nous donner votre avis :\n"
                        f"{getattr(settings, 'FRONTEND_URL', '')}/evenements/{evenement.slug}/feedback\n\n"
                        f"Merci !\nL'équipe AvenSU-Orienta"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[inscription.utilisateur.email],
                    fail_silently=True,
                )
                nb_envoyes += 1
            except Exception as e:
                logger.error(f"Erreur feedback: {e}")

    logger.info(f"{nb_envoyes} demandes de feedback envoyées")
    return nb_envoyes
