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
    from apps.orientation.services import ScoringService, RecommendationEngine
    from apps.orientation.models import ReponseUtilisateur

    try:
        # 1. Calculer le résultat
        resultat = ScoringService.calculer_resultat(reponse_id)

        # 2. Récupérer les préférences de l'étudiant
        reponse = ReponseUtilisateur.objects.select_related(
            "etudiant__student_profile"
        ).get(id=reponse_id)

        profile = getattr(reponse.etudiant, "student_profile", None)
        budget_max = None
        villes_preferees = None

        if profile:
            budget_max = (
                int(profile.budget_max_annuel) if profile.budget_max_annuel else None
            )
            villes_preferees = profile.villes_preferees or None

        # 3. Générer les recommandations
        recommandations = RecommendationEngine.generer_recommandations(
            resultat=resultat,
            budget_max=budget_max,
            villes_preferees=villes_preferees,
        )

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
