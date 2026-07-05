"""
Tâches Celery pour l'app orientation.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(queue="orientation")
def calculer_resultat_et_recommandations(reponse_id: str):
    """
    Tâche asynchrone : calcule le résultat d'un test puis génère les recommandations.
    """
    from apps.orientation.services import ScoringService
    from apps.orientation.models import ReponseUtilisateur

    try:
        # 1. Calculer le résultat
        resultat = ScoringService.calculer_resultat(reponse_id)

        # 2. Générer les recommandations (shared helper handles profile extraction)
        from apps.orientation.services.recommendation_utils import generate_recommendations_for_resultat
        recommandations = generate_recommendations_for_resultat(resultat) or []

        reponse = ReponseUtilisateur.objects.select_related("etudiant").get(id=reponse_id)
        logger.info(
            f"Test traité : {reponse.etudiant.email} -> "
            f"{len(recommandations)} recommandations"
        )

        return {
            "resultat_id": str(resultat.id),
            "nb_recommandations": len(recommandations),
        }

    except Exception as e:
        logger.error(f"Erreur traitement test {reponse_id}: {e}", exc_info=True)
        raise

@shared_task(queue="orientation")
def expirer_sessions_inactives():
    """Expire les sessions de test en cours depuis plus de 24h."""
    from apps.orientation.models import ReponseUtilisateur, StatutTest

    seuil = timezone.now() - timezone.timedelta(hours=24)
    count = ReponseUtilisateur.objects.filter(
        statut=StatutTest.EN_COURS,
        date_debut__lt=seuil,
    ).update(statut=StatutTest.EXPIRE)

    if count:
        logger.info(f"{count} sessions de test expirées")

    return count
