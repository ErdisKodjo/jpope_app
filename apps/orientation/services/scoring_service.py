"""
Service de scoring des tests d'orientation.
Calcule les scores par dimension à partir des réponses.
"""
import logging
from typing import Dict, List, Tuple

from django.db import transaction
from django.utils import timezone

from apps.orientation.models import (
    ReponseUtilisateur,
    DetailReponse,
    ResultatTest,
    StatutTest,
    TypeQuestion,
)

logger = logging.getLogger(__name__)

class ScoringService:
    """
    Service de calcul des scores pour un test d'orientation.

    Supporte plusieurs méthodes de scoring :
    - RIASEC_PONDERE : Somme pondérée des scores par dimension
    - LIKERT_MOYENNE : Moyenne des échelles Likert par dimension
    - HYBRIDE : Combinaison des deux
    """

    @classmethod
    @transaction.atomic
    def calculer_resultat(cls, reponse_id: str) -> ResultatTest:
        """
        Calcule le résultat final d'une session de test.

        Étapes :
        1. Récupérer toutes les réponses individuelles
        2. Calculer les scores bruts par dimension
        3. Normaliser les scores (0-100)
        4. Déterminer le code Holland (top 3)
        5. Générer l'interprétation
        6. Sauvegarder le résultat
        """
        reponse = ReponseUtilisateur.objects.select_related(
            "test", "etudiant"
        ).get(id=reponse_id)

        # Vérifier que le test est terminé
        if reponse.statut != StatutTest.TERMINE:
            raise ValueError(
                f"Le test n'est pas terminé (statut: {reponse.statut})"
            )

        # 1. Récupérer les détails de réponses
        details = (
            DetailReponse.objects
            .filter(reponse_utilisateur=reponse)
            .select_related("question", "choice_selectionne")
        )

        if not details.exists():
            raise ValueError("Aucune réponse trouvée pour cette session")

        # 2. Calculer les scores bruts par dimension
        scores_bruts = cls._calculer_scores_bruts(details, reponse.test.methode_scoring)

        # 3. Normaliser (0-100)
        scores_normalises = cls._normaliser_scores(
            scores_bruts,
            details.count(),
            reponse.test,
        )

        # 4. Code Holland (top 3 dimensions)
        code_holland, profil_dominant, profil_secondaire = cls._determiner_code_holland(
            scores_normalises
        )

        # 5. Score global (moyenne des top 3)
        top3_scores = sorted(scores_normalises.values(), reverse=True)[:3]
        score_global = round(sum(top3_scores) / len(top3_scores), 1) if top3_scores else 0

        # 6. Interprétation
        interpretation = cls._generer_interpretation(
            scores_normalises,
            code_holland,
            reponse.etudiant,
        )

        # 7. Évolution vs précédent
        evolution = cls._calculer_evolution(reponse.etudiant, reponse.test, scores_normalises)

        # 8. Créer ou mettre à jour le résultat
        resultat, created = ResultatTest.objects.update_or_create(
            reponse_utilisateur=reponse,
            defaults={
                "score_global": score_global,
                "scores_par_dimension": scores_normalises,
                "code_holland": code_holland,
                "profil_dominant": profil_dominant,
                "profil_secondaire": profil_secondaire,
                "interpretation": interpretation,
                "forces": cls._identifier_forces(scores_normalises),
                "axes_amelioration": cls._identifier_axes(scores_normalises),
                "evolution_vs_precedent": evolution,
            },
        )

        # Mettre à jour les scores agrégés sur la réponse
        reponse.score_global = score_global
        reponse.profil_dominant = profil_dominant
        reponse.profil_secondaire = profil_secondaire
        reponse.code_holland = code_holland
        reponse.scores_par_dimension = scores_normalises
        reponse.save(update_fields=[
            "score_global", "profil_dominant",
            "profil_secondaire", "code_holland", "scores_par_dimension",
        ])

        logger.info(
            f"Résultat calculé pour {reponse.etudiant.email} : "
            f"Holland={code_holland}, Score={score_global}"
        )

        return resultat

    @classmethod
    def _calculer_scores_bruts(
        cls,
        details: "QuerySet",
        methode: str,
    ) -> Dict[str, float]:
        """Calcule les scores bruts par dimension RIASEC."""
        scores: Dict[str, float] = {}

        for detail in details:
            question = detail.question
            poids = question.poids

            if question.type == TypeQuestion.ECHELLE_LIKERT:
                # Scoring Likert : valeur × poids × coefficient dimension
                valeur = detail.valeur_echelle or 0
                for dim, coef in (question.dimensions or {}).items():
                    scores[dim] = scores.get(dim, 0) + (valeur * poids * coef)

            elif question.type in [TypeQuestion.CHOIX_UNIQUE, TypeQuestion.CHOIX_MULTIPLE]:
                # Scoring par choix : points du choix × poids
                if detail.choice_selectionne:
                    for dim, points in (detail.choice_selectionne.scores or {}).items():
                        scores[dim] = scores.get(dim, 0) + (points * poids)

                # Choix multiples
                if detail.choices_selectionnes:
                    from apps.orientation.models import Choice
                    choices = Choice.objects.filter(id__in=detail.choices_selectionnes)
                    for choice in choices:
                        for dim, points in (choice.scores or {}).items():
                            scores[dim] = scores.get(dim, 0) + (points * poids)

            elif question.type == TypeQuestion.SITUATIONNELLE:
                # Même logique que choix unique
                if detail.choice_selectionne:
                    for dim, points in (detail.choice_selectionne.scores or {}).items():
                        scores[dim] = scores.get(dim, 0) + (points * poids)

            # Sauvegarder le score calculé sur le détail
            detail.score_calcule = {
                dim: scores.get(dim, 0) for dim in (question.dimensions or {})
            }
            detail.save(update_fields=["score_calcule"])

        return scores

    @classmethod
    def _normaliser_scores(
        cls,
        scores_bruts: Dict[str, float],
        nb_questions: int,
        test,
    ) -> Dict[str, float]:
        """
        Normalise les scores bruts sur une échelle 0-100.

        Méthode : score_normalisé = (score_brut / score_max_possible) × 100
        """
        if not scores_bruts or nb_questions == 0:
            return {}

        # Estimer le score max théorique
        score_max_theorique = max(nb_questions * 5 * 1.5, 1)  # Estimation conservative

        normalises = {}
        for dim, score in scores_bruts.items():
            normalise = min(round((score / score_max_theorique) * 100, 1), 100)
            normalises[dim] = max(normalise, 0)

        return normalises

    @classmethod
    def _determiner_code_holland(
        cls,
        scores: Dict[str, float],
    ) -> Tuple[str, str, str]:
        """
        Détermine le code Holland (3 lettres) à partir des scores.

        Returns:
            (code_holland, profil_dominant, profil_secondaire)
        """
        if not scores:
            return "", "", ""

        # Trier par score décroissant
        sorted_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Prendre les 3 premières lettres
        top3 = [dim for dim, _ in sorted_dims[:3]]
        code = "".join(top3)

        return code, top3[0] if len(top3) > 0 else "", top3[1] if len(top3) > 1 else ""

    @classmethod
    def _generer_interpretation(
        cls,
        scores: Dict[str, float],
        code_holland: str,
        etudiant,
    ) -> str:
        """
        Génère une interprétation textuelle du résultat.

        Note : en V2, ceci sera remplacé par une génération LLM.
        """
        if not code_holland:
            return "Résultat non disponible."

        # Descriptions des dimensions
        dim_descriptions = {
            "R": "Vous avez un profil Réaliste : vous aimez travailler avec vos mains, les outils, les machines et les activités concrètes. Les métiers techniques, l'ingénierie et l'artisanat pourraient vous convenir.",
            "I": "Vous avez un profil Investigateur : vous êtes curieux, analytique et aimez résoudre des problèmes complexes. La recherche, la science et l'informatique sont des domaines à explorer.",
            "A": "Vous avez un profil Artistique : vous êtes créatif, expressif et aimez l'innovation. Les arts, le design, la communication et l'architecture pourraient vous épanouir.",
            "S": "Vous avez un profil Social : vous aimez aider, enseigner et accompagner les autres. L'enseignement, la santé, le travail social et la psychologie sont des pistes naturelles.",
            "E": "Vous avez un profil Entreprenant : vous aimez diriger, convaincre et prendre des initiatives. Le commerce, le management, le droit et l'entrepreneuriat vous correspondent.",
            "C": "Vous avez un profil Conventionnel : vous êtes organisé, rigoureux et aimez la précision. La comptabilité, l'administration, la finance et la logistique sont des domaines adaptés.",
            "N": "Vous avez une forte affinité avec le Numérique : le développement, la data science, la cybersécurité et l'intelligence artificielle sont des domaines porteurs pour vous.",
            "ENV": "Vous êtes sensible à l'Environnement : l'agronomie, les énergies renouvelables et le développement durable correspondent à vos valeurs.",
        }

        # Générer l'interprétation
        lignes = [f"Votre profil d'orientation est : {code_holland}\n"]

        for lettre in code_holland:
            if lettre in dim_descriptions:
                score = scores.get(lettre, 0)
                lignes.append(f"\n{lettre} ({score}/100) : {dim_descriptions[lettre]}")

        lignes.append(
            "\nConseil : Consultez les recommandations ci-dessous pour découvrir "
            "les formations et métiers les plus compatibles avec votre profil."
        )

        return "\n".join(lignes)

    @classmethod
    def _identifier_forces(cls, scores: Dict[str, float]) -> List[str]:
        """Identifie les forces (dimensions > 70)."""
        forces = []
        dim_noms = {
            "R": "Esprit pratique et technique",
            "I": "Capacité d'analyse et de recherche",
            "A": "Créativité et sens artistique",
            "S": "Sens du contact et de l'entraide",
            "E": "Leadership et esprit d'initiative",
            "C": "Rigueur et sens de l'organisation",
            "N": "Aptitudes numériques",
            "ENV": "Sensibilité environnementale",
        }
        for dim, score in scores.items():
            if score >= 70:
                forces.append(f"{dim_noms.get(dim, dim)} ({score}/100)")
        return forces

    @classmethod
    def _identifier_axes(cls, scores: Dict[str, float]) -> List[str]:
        """Identifie les axes d'amélioration (dimensions < 40)."""
        axes = []
        dim_noms = {
            "R": "Développer des compétences pratiques",
            "I": "Renforcer la pensée analytique",
            "A": "Explorer sa créativité",
            "S": "Développer l'intelligence sociale",
            "E": "Travailler le leadership",
            "C": "Améliorer l'organisation personnelle",
            "N": "S'initier aux outils numériques",
            "ENV": "S'informer sur les enjeux environnementaux",
        }
        for dim, score in scores.items():
            if score < 40:
                axes.append(f"{dim_noms.get(dim, dim)} ({score}/100)")
        return axes

    @classmethod
    def _calculer_evolution(
        cls,
        etudiant,
        test,
        scores_actuels: Dict[str, float],
    ) -> Dict[str, float]:
        """Calcule l'évolution par rapport au précédent test du même type."""
        dernier_resultat = (
            ResultatTest.objects
            .filter(
                reponse_utilisateur__etudiant=etudiant,
                reponse_utilisateur__test__type=test.type,
            )
            .exclude(reponse_utilisateur__test=test)
            .order_by("-date_calcul")
            .first()
        )

        if not dernier_resultat or not dernier_resultat.scores_par_dimension:
            return {}

        evolution = {}
        for dim, score in scores_actuels.items():
            ancien = dernier_resultat.scores_par_dimension.get(dim, 0)
            diff = round(score - ancien, 1)
            if diff != 0:
                evolution[dim] = diff

        return evolution
