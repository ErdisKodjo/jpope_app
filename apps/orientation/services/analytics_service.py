"""
Service d'analytics pour les tests d'orientation.
"""
from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.orientation.models import (
    ReponseUtilisateur,
    ResultatTest,
    Recommandation,
    StatutTest,
)

class OrientationAnalyticsService:
    """Statistiques et analytics du module orientation."""

    @staticmethod
    def stats_globales() -> dict:
        """Statistiques globales de l'orientation."""
        return {
            "total_tests_passes": ReponseUtilisateur.objects.filter(
                statut=StatutTest.TERMINE
            ).count(),
            "tests_en_cours": ReponseUtilisateur.objects.filter(
                statut=StatutTest.EN_COURS
            ).count(),
            "recommandations_generees": Recommandation.objects.count(),
            "score_moyen_global": ResultatTest.objects.aggregate(
                avg=Avg("score_global")
            )["avg"] or 0,
            "repartition_codes_holland": dict(
                ResultatTest.objects.exclude(code_holland="")
                .values_list("code_holland")
                .annotate(count=Count("id"))
                .values_list("code_holland", "count")
            ),
        }

    @staticmethod
    def stats_etudiant(etudiant) -> dict:
        """Statistiques individuelles d'un étudiant."""
        reponses = ReponseUtilisateur.objects.filter(
            etudiant=etudiant,
            statut=StatutTest.TERMINE,
        )

        dernier_resultat = (
            ResultatTest.objects
            .filter(reponse_utilisateur__etudiant=etudiant)
            .order_by("-date_calcul")
            .first()
        )

        recs_stats = Recommandation.objects.filter(etudiant=etudiant)

        return {
            "nombre_tests_passes": reponses.count(),
            "dernier_test": {
                "date": dernier_resultat.date_calcul if dernier_resultat else None,
                "code_holland": dernier_resultat.code_holland if dernier_resultat else None,
                "score_global": dernier_resultat.score_global if dernier_resultat else None,
            } if dernier_resultat else None,
            "evolution_scores": OrientationAnalyticsService._calculer_evolution_scores(etudiant),
            "recommandations": {
                "total": recs_stats.count(),
                "principales": recs_stats.filter(plan="PRINCIPAL").count(),
                "favorisees": recs_stats.filter(a_ete_favorisee=True).count(),
            },
        }

    @staticmethod
    def _calculer_evolution_scores(etudiant) -> list:
        """Retourne l'historique des scores par dimension pour un étudiant."""
        resultats = (
            ResultatTest.objects
            .filter(reponse_utilisateur__etudiant=etudiant)
            .order_by("date_calcul")
        )

        evolution = []
        for r in resultats:
            evolution.append({
                "date": r.date_calcul.isoformat(),
                "code_holland": r.code_holland,
                "score_global": r.score_global,
                "scores": r.scores_par_dimension,
            })

        return evolution

    @staticmethod
    def top_domaines_recommandes(limit: int = 10) -> list:
        """Domaines les plus recommandés par le moteur."""
        return list(
            Recommandation.objects.filter(
                type_entite="FORMATION",
                formation__isnull=False,
            )
            .values("formation__domaine__nom")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit]
        )
