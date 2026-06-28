"""
Service d'orientation principal — façade combinant scoring et recommandations.
Alias / pont vers ScoringService et RecommendationEngine pour compatibilité.
"""
from .scoring_service import ScoringService
from .recommendation_engine import RecommendationEngine
from .analytics_service import OrientationAnalyticsService


class OrientationService:
    """
    Façade principale du module orientation.

    Centralise les opérations courantes :
    - Calculer un résultat de test
    - Générer des recommandations
    - Récupérer les statistiques d'un étudiant
    """

    @classmethod
    def traiter_test_complet(
        cls,
        reponse_id: str,
        budget_max: int = None,
        villes_preferees: list = None,
    ) -> dict:
        """
        Traite un test complet : calcul du résultat + génération des recommandations.

        Args:
            reponse_id: UUID de la ReponseUtilisateur
            budget_max: Budget max annuel de l'étudiant (FCFA)
            villes_preferees: Villes préférées de l'étudiant

        Returns:
            dict avec 'resultat' et 'recommandations'
        """
        # 1. Calculer le résultat RIASEC
        resultat = ScoringService.calculer_resultat(reponse_id)

        # 2. Générer les recommandations
        recommandations = RecommendationEngine.generer_recommandations(
            resultat=resultat,
            budget_max=budget_max,
            villes_preferees=villes_preferees,
        )

        return {
            "resultat": resultat,
            "recommandations": recommandations,
            "nb_recommandations": len(recommandations),
        }

    @classmethod
    def stats_etudiant(cls, etudiant) -> dict:
        """Retourne les statistiques d'orientation d'un étudiant."""
        return OrientationAnalyticsService.stats_etudiant(etudiant)

    @classmethod
    def stats_globales(cls) -> dict:
        """Retourne les statistiques globales de la plateforme."""
        return OrientationAnalyticsService.stats_globales()
