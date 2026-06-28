"""
Tâches Celery pour l'app ranking.

Inclut recalculer_classements référencé dans config/celery.py beat schedule :
  "recalculer-classements-annuels": {
      "task": "apps.ranking.tasks.recalculer_classements",
      "schedule": crontab(day_of_month=1, month_of_year=1, hour=3, minute=0),
  }
"""
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(queue="default")
def recalculer_classements():
    """
    Recalcule les classements annuels des établissements.
    Référencé dans config/celery.py beat schedule sous 'recalculer-classements-annuels'.
    Planifié le 1er janvier à 3h00.
    """
    from apps.ranking.models import Classement

    annee = timezone.now().year
    nb_calcules = 0

    try:
        # Récupérer tous les établissements ayant eu des classements l'an passé
        classements_an_passe = Classement.objects.filter(
            annee=annee - 1
        ).select_related("etablissement")

        # Recalculer pour cette année
        for classement_precedent in classements_an_passe:
            etablissement = classement_precedent.etablissement

            # Créer/mettre à jour le classement pour l'année en cours
            # Le calcul réel dépend des données de l'établissement
            nouveau_classement, created = Classement.objects.get_or_create(
                etablissement=etablissement,
                annee=annee,
                defaults={
                    "score_final": classement_precedent.score_final,
                    "rang_national": classement_precedent.rang_national,
                    "rang_regional": classement_precedent.rang_regional,
                    "is_published": False,  # Brouillon jusqu'à validation
                },
            )

            if not created:
                # Déjà calculé cette année
                continue

            nb_calcules += 1

        logger.info(
            f"Recalcul des classements {annee} : "
            f"{nb_calcules} établissements traités"
        )

    except Exception as e:
        logger.error(f"Erreur recalcul classements {annee}: {e}")

    return {
        "annee": annee,
        "nb_etablissements": nb_calcules,
    }


@shared_task(queue="default")
def publier_classements(annee: int = None):
    """
    Publie les classements d'une année (après validation manuelle).
    """
    from apps.ranking.models import Classement

    if not annee:
        annee = timezone.now().year

    count = Classement.objects.filter(
        annee=annee,
        is_published=False,
    ).update(is_published=True)

    logger.info(f"{count} classements publiés pour {annee}")
    return count


@shared_task(queue="default")
def calculer_rang_etablissements(annee: int = None):
    """
    Calcule et ordonne les rangs nationaux et régionaux des établissements.
    """
    from apps.ranking.models import Classement

    if not annee:
        annee = timezone.now().year

    classements = Classement.objects.filter(
        annee=annee,
    ).order_by("-score_final")

    nb_mis_a_jour = 0
    for rang, classement in enumerate(classements, start=1):
        if classement.rang_national != rang:
            classement.rang_national = rang
            classement.save(update_fields=["rang_national"])
            nb_mis_a_jour += 1

    logger.info(
        f"Rangs {annee} recalculés : {nb_mis_a_jour} mises à jour"
    )
    return nb_mis_a_jour
