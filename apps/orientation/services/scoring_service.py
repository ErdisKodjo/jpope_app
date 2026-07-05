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

        # Pré-charger les choices pour les questions à choix multiple (éviter N+1)
        choix_multiples_ids = set()
        for detail in details:
            if detail.choices_selectionnes:
                choix_multiples_ids.update(detail.choices_selectionnes)
        choices_cache = {}
        if choix_multiples_ids:
            from apps.orientation.models import Choice
            for c in Choice.objects.filter(id__in=choix_multiples_ids):
                choices_cache[str(c.id)] = c

        # 2. Calculer les scores bruts par dimension
        scores_bruts = cls._calculer_scores_bruts(details, reponse.test.methode_scoring, choices_cache)

        # 3. Normaliser (0-100)
        scores_normalises = cls._normaliser_scores(
            scores_bruts,
            details,
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
        choices_cache: dict = None,
    ) -> Dict[str, float]:
        """Calcule les scores bruts par dimension RIASEC."""
        scores: Dict[str, float] = {}

        for detail in details:
            question = detail.question
            poids = question.poids

            # Compute THIS detail's contribution only
            detail_contribution = {}

            if question.type == TypeQuestion.ECHELLE_LIKERT:
                # Scoring Likert : valeur × poids × coefficient dimension
                valeur = detail.valeur_echelle or 0
                for dim, coef in (question.dimensions or {}).items():
                    contribution = valeur * poids * coef
                    detail_contribution[dim] = round(contribution, 4)
                    scores[dim] = scores.get(dim, 0) + contribution

            elif question.type in [TypeQuestion.CHOIX_UNIQUE, TypeQuestion.CHOIX_MULTIPLE]:
                # Scoring par choix : points du choix × poids
                if detail.choice_selectionne:
                    for dim, points in (detail.choice_selectionne.scores or {}).items():
                        contribution = points * poids
                        detail_contribution[dim] = round(contribution, 4)
                        scores[dim] = scores.get(dim, 0) + contribution

                # Choix multiples
                if detail.choices_selectionnes:
                    for choice_id in detail.choices_selectionnes:
                        choice = choices_cache.get(str(choice_id)) if choices_cache else None
                        if choice:
                            for dim, points in (choice.scores or {}).items():
                                contribution = points * poids
                                detail_contribution[dim] = round(detail_contribution.get(dim, 0) + contribution, 4)
                                scores[dim] = scores.get(dim, 0) + contribution

            elif question.type == TypeQuestion.SITUATIONNELLE:
                # Même logique que choix unique
                if detail.choice_selectionne:
                    for dim, points in (detail.choice_selectionne.scores or {}).items():
                        contribution = points * poids
                        detail_contribution[dim] = round(contribution, 4)
                        scores[dim] = scores.get(dim, 0) + contribution

            # Save THIS detail's contribution (not cumulative)
            detail.score_calcule = detail_contribution
            detail.save(update_fields=["score_calcule"])

        return scores

    @classmethod
    def _normaliser_scores(
        cls,
        scores_bruts: Dict[str, float],
        details,
        test,
    ) -> Dict[str, float]:
        """
        Normalise les scores bruts sur une échelle 0-100.

        Méthode : score_normalisé = (score_brut / score_max_possible) × 100
        Utilise le score max réel par dimension plutôt qu'une estimation théorique.
        """
        if not scores_bruts:
            return {}

        # Compute actual max possible score per dimension
        max_possible = {}
        for detail in details:
            question = detail.question
            if question.type == TypeQuestion.ECHELLE_LIKERT:
                max_val = question.echelle_max if hasattr(question, 'echelle_max') else 5
            elif question.type in (TypeQuestion.CHOIX_UNIQUE, TypeQuestion.SITUATIONNELLE, TypeQuestion.CHOIX_MULTIPLE):
                if question.type == TypeQuestion.CHOIX_MULTIPLE and detail.choices_selectionnes:
                    # For multiple choice, max = sum of max points across all active choices
                    from apps.orientation.models import Choice
                    max_val = sum(
                        max((c.scores or {}).values(), default=0)
                        for c in question.choices.filter(is_active=True)
                    )
                elif detail.choice_selectionne:
                    # For single/situational, max = max points among active choices
                    max_val = max(
                        (max((c.scores or {}).values(), default=0) for c in question.choices.filter(is_active=True)),
                        default=5,
                    )
                else:
                    max_val = 5
            else:
                max_val = 5
            poids = question.poids or 1
            for dim, coef in (question.dimensions or {}).items():
                max_possible[dim] = max_possible.get(dim, 0) + (max_val * poids * coef)

        normalises = {}
        for dim, score in scores_bruts.items():
            max_score = max(max_possible.get(dim, 1), 1)
            normalises[dim] = min(round((score / max_score) * 100, 1), 100)

        return normalises

    @classmethod
    def _determiner_code_holland(
        cls,
        scores: Dict[str, float],
    ) -> Tuple[str, str, str]:
        """
        Détermine le code profil à partir des scores.

        Pour les tests RIASEC purs (toutes dims = 1 char) : "RIA"
        Pour les tests multi-domaines (ex: N, ENV) : "N-ENV-I"

        Returns:
            (code_profil, dim_dominante, dim_secondaire)
        """
        if not scores:
            return "", "", ""

        sorted_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top3 = [dim for dim, _ in sorted_dims[:3]]

        if all(len(d) == 1 for d in top3):
            code = "".join(top3)   # RIASEC classique : "RIA"
        else:
            code = "-".join(top3)  # multi-domaine : "N-ENV-I"

        return code, top3[0] if top3 else "", top3[1] if len(top3) > 1 else ""

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

        # Parse the code into dimension tokens (handles multi-char like "ENV" and dashed codes like "N-ENV-I")
        if "-" in code_holland:
            dims = [d.strip() for d in code_holland.split("-") if d.strip()]
        else:
            dims = list(code_holland)

        lignes = [f"Votre profil d'orientation est : {code_holland}\n"]
        for dim in dims:
            if dim in dim_descriptions:
                score = scores.get(dim, 0)
                lignes.append(f"\n{dim} ({score}/100) : {dim_descriptions[dim]}")

        if len(lignes) == 1:
            lignes.append("\nProfil atypique — consultez un conseiller pour une analyse personnalisée.")
        else:
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
