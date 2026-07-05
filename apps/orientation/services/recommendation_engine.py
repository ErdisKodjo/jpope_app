"""
Moteur de recommandation : matching profil <-> formations/métiers.
"""
import logging
from dataclasses import dataclass
from typing import List, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q

from apps.catalog.models import Formation, Metier, Etablissement, Domaine
from apps.orientation.models import (
    ResultatTest,
    Recommandation,
    PlanRecommandation,
    TypeEntiteRecommandee,
)

logger = logging.getLogger(__name__)

@dataclass
class ScoreMatch:
    """Résultat du matching entre un profil et une entité."""
    entity_type: str  # FORMATION, METIER, ETABLISSEMENT
    entity_id: str
    entity_obj: object
    score: float  # 0-100
    plan: str  # PRINCIPAL, ALTERNATIF, EXPLORATOIRE
    justification: str
    points_forts: List[str]
    points_attention: List[str]

class RecommendationEngine:
    """
    Moteur de recommandation hybride.

    V1 : Règles métier (scoring par dimension x tags de domaine)
    V2 : Filtrage collaboratif (scikit-learn)
    V3 : Deep learning (embeddings)

    La V1 utilise une matrice de correspondance entre les dimensions RIASEC
    et les domaines de formation / métiers.
    """

    # MATRICE RIASEC -> DOMAINE ACADÉMIQUE (sciences / lettres / commerce)
    ACADEMIC_DOMAINES = {
        "Informatique & Numérique": "sciences",
        "Ingenierie & Industrie": "sciences",
        "Santé & Médecine": "sciences",
        "Agriculture & Environnement": "sciences",
        "Gestion & Commerce": "commerce",
        "Droit & Sciences Politiques": "lettres",
        "Lettres & Sciences Humaines": "lettres",
        "Éducation & Formation": "lettres",
    }

    # Compatibilité série BAC -> domaine académique (coefficient 0-1)
    SERIE_BAC_AFFINITE = {
        "C":    {"sciences": 1.0, "lettres": 0.25, "commerce": 0.45},
        "D":    {"sciences": 0.90, "lettres": 0.35, "commerce": 0.40},
        "E":    {"sciences": 0.80, "lettres": 0.25, "commerce": 0.40},
        "TI":   {"sciences": 0.75, "lettres": 0.25, "commerce": 0.40},
        "A":    {"sciences": 0.25, "lettres": 1.0,  "commerce": 0.50},
        "G2":   {"sciences": 0.25, "lettres": 0.45, "commerce": 1.0},
        "TGC":  {"sciences": 0.25, "lettres": 0.45, "commerce": 0.95},
        "AUTRE":{"sciences": 0.50, "lettres": 0.50, "commerce": 0.50},
    }

    # MATRICE DE CORRESPONDANCE RIASEC <-> DOMAINES
    # Pour chaque dimension RIASEC, quels domaines sont pertinents
    RIASEC_DOMAINES = {
        "R": {
            "Ingenierie & Industrie": 0.9,
            "Informatique & Numérique": 0.7,
            "Agriculture & Environnement": 0.8,
        },
        "I": {
            "Informatique & Numérique": 0.9,
            "Santé & Médecine": 0.8,
            "Ingenierie & Industrie": 0.7,
        },
        "A": {
            "Lettres & Sciences Humaines": 0.9,
            "Informatique & Numérique": 0.5,  # design, UX
        },
        "S": {
            "Santé & Médecine": 0.9,
            "Éducation & Formation": 0.95,
            "Lettres & Sciences Humaines": 0.7,
        },
        "E": {
            "Gestion & Commerce": 0.95,
            "Droit & Sciences Politiques": 0.8,
        },
        "C": {
            "Gestion & Commerce": 0.85,
            "Droit & Sciences Politiques": 0.7,
            "Informatique & Numérique": 0.5,  # data
        },
    }

    @classmethod
    @transaction.atomic
    def generer_recommandations(
        cls,
        resultat: ResultatTest,
        budget_max: Optional[int] = None,
        villes_preferees: Optional[List[str]] = None,
        max_recommandations: int = 15,
    ) -> List[Recommandation]:
        """
        Génère les recommandations pour un étudiant à partir de son résultat.

        Args:
            resultat: Le résultat du test d'orientation
            budget_max: Budget annuel max (FCFA) pour filtrer
            villes_preferees: Villes préférées pour filtrer
            max_recommandations: Nombre max de recommandations

        Returns:
            Liste des recommandations créées
        """
        etudiant = resultat.reponse_utilisateur.etudiant
        scores = resultat.scores_par_dimension

        if not scores:
            logger.warning(f"Pas de scores pour le résultat {resultat.id}")
            return []

        # Supprimer les anciennes recommandations pour ce résultat
        Recommandation.objects.filter(resultat_test=resultat).delete()

        recommandations = []

        # 1. Recommandations de MÉTIERS
        metiers_scores = cls._scorer_metiers(scores)

        # 2. Recommandations de FORMATIONS (avec profil académique si disponible)
        formations_scores = cls._scorer_formations(
            scores,
            budget_max=budget_max,
            villes_preferees=villes_preferees,
            etudiant=etudiant,
        )

        # 3. Combiner et classer
        tous_les_scores = metiers_scores + formations_scores
        tous_les_scores.sort(key=lambda m: m.score, reverse=True)

        # 4. Attribuer les plans
        tous_les_scores = cls._attribuer_plans(tous_les_scores)

        # 5. Sauvegarder en base
        for i, match in enumerate(tous_les_scores[:max_recommandations]):
            kwargs = {
                "resultat_test": resultat,
                "etudiant": etudiant,
                "type_entite": match.entity_type,
                "taux_compatibilite": match.score,
                "plan": match.plan,
                "ordre": i,
                "justification": match.justification,
                "points_forts_match": match.points_forts,
                "points_attention": match.points_attention,
            }

            if match.entity_type == TypeEntiteRecommandee.FORMATION:
                kwargs["formation"] = match.entity_obj
            elif match.entity_type == TypeEntiteRecommandee.METIER:
                kwargs["metier"] = match.entity_obj

            rec = Recommandation.objects.create(**kwargs)
            recommandations.append(rec)

        logger.info(
            f"{len(recommandations)} recommandations générées pour "
            f"{etudiant.email} (Holland: {resultat.code_holland})"
        )

        return recommandations

    @classmethod
    def _scorer_metiers(cls, scores: dict) -> List[ScoreMatch]:
        """Score tous les métiers actifs par rapport au profil."""
        metiers = Metier.objects.filter(is_active=True).select_related("domaine")
        matches = []

        for metier in metiers:
            score = cls._calculer_score_metier(scores, metier)

            if score >= 30:  # Seuil minimum
                matches.append(ScoreMatch(
                    entity_type=TypeEntiteRecommandee.METIER,
                    entity_id=str(metier.id),
                    entity_obj=metier,
                    score=score,
                    plan="",  # Attribué après
                    justification=cls._justifier_metier(scores, metier, score),
                    points_forts=cls._points_forts_metier(scores, metier),
                    points_attention=cls._points_attention_metier(metier),
                ))

        return matches

    @classmethod
    def _scorer_formations(
        cls,
        scores: dict,
        budget_max: Optional[int] = None,
        villes_preferees: Optional[List[str]] = None,
        etudiant=None,
    ) -> List[ScoreMatch]:
        """Score toutes les formations actives par rapport au profil."""
        formations = Formation.objects.filter(
            is_active=True,
        ).select_related("etablissement", "domaine")

        # Filtres hard
        if budget_max:
            formations = formations.filter(cout_annuel__lte=budget_max)
        if villes_preferees:
            formations = formations.filter(
                etablissement__ville__in=villes_preferees
            )

        matches = []

        for formation in formations:
            score = cls._calculer_score_formation(scores, formation, etudiant=etudiant)

            if score >= 30:  # Seuil minimum
                matches.append(ScoreMatch(
                    entity_type=TypeEntiteRecommandee.FORMATION,
                    entity_id=str(formation.id),
                    entity_obj=formation,
                    score=score,
                    plan="",
                    justification=cls._justifier_formation(scores, formation, score),
                    points_forts=cls._points_forts_formation(scores, formation),
                    points_attention=cls._points_attention_formation(formation),
                ))

        return matches

    @classmethod
    def _calculer_score_metier(cls, scores: dict, metier) -> float:
        """
        Calcule le score de compatibilité entre un profil et un métier.

        Formule :
        score = Somme (score_dimension x coefficient_domaine x poids)
        + bonus_demande_marche
        + bonus_taux_emploi
        """
        domaine_nom = metier.domaine.nom
        score_base = 0
        total_coef = 0

        for dim, score_dim in scores.items():
            # Coefficient de correspondance RIASEC -> domaine
            coef = cls.RIASEC_DOMAINES.get(dim, {}).get(domaine_nom, 0.1)
            score_base += (score_dim / 100) * coef
            total_coef += coef

        # Normaliser
        if total_coef > 0:
            score_domaine = (score_base / total_coef) * 70  # 70% du score
        else:
            score_domaine = 20

        # Bonus demande marché (15% du score)
        demande_bonus = {
            "TRES_FORTE": 15,
            "FORTE": 12,
            "MOYENNE": 8,
            "FAIBLE": 4,
            "EN_DECLIN": 0,
        }
        score_demande = demande_bonus.get(metier.demande_marche, 5)

        # Bonus taux emploi (15% du score)
        score_emploi = (metier.taux_emploi / 100) * 15

        return round(score_domaine + score_demande + score_emploi, 1)

    @classmethod
    def _score_academique(cls, etudiant, domaine_nom: str) -> float:
        """
        Score académique (0-20 pts) : combine notes par matière + série BAC.
        Retourne 10 (neutre) si aucune donnée académique n'est disponible.
        """
        score = 0.0
        has_data = False

        # Notes par domaine (0-12 pts)
        try:
            notes = etudiant.notes
            profil = notes.profil_academique  # {sciences: 0-1, lettres: 0-1, commerce: 0-1}
            cat = cls.ACADEMIC_DOMAINES.get(domaine_nom)
            if cat and cat in profil:
                score += profil[cat] * 12
                has_data = True
        except (ObjectDoesNotExist, AttributeError):
            # Données de notes absentes pour cet étudiant : score neutre.
            logger.debug("Notes académiques indisponibles pour l'étudiant %s", getattr(etudiant, "pk", etudiant))

        # Série BAC (0-8 pts)
        try:
            student_profile = etudiant.student_profile
            if student_profile and student_profile.serie_bac:
                affinite = cls.SERIE_BAC_AFFINITE.get(student_profile.serie_bac, {})
                cat = cls.ACADEMIC_DOMAINES.get(domaine_nom)
                if cat and cat in affinite:
                    score += affinite[cat] * 8
                    has_data = True
        except (ObjectDoesNotExist, AttributeError):
            # Profil étudiant / série BAC absent : score neutre.
            logger.debug("Profil étudiant indisponible pour l'étudiant %s", getattr(etudiant, "pk", etudiant))

        if not has_data:
            return 10.0  # score neutre sans données

        return round(min(20.0, score), 1)

    @classmethod
    def _calculer_score_formation(cls, scores: dict, formation, etudiant=None) -> float:
        """
        Calcule le score de compatibilité entre un profil et une formation.

        Formule V2 (avec profil académique) :
        score = compatibilite_domaine RIASEC (40%)
              + score_academique notes + serie_bac (20%)
              + qualite_formation (20%)
              + importance_strategique (12%)
              + accessibilite / cout (8%)

        Formule V1 (sans profil académique, scores inchangés) :
        score = compatibilite_domaine (50%) + qualite (25%) + importance (15%) + cout (10%)
        """
        domaine_nom = formation.domaine.nom
        has_academic = etudiant is not None

        # 1. Compatibilité domaine RIASEC
        score_domaine = 0
        total_coef = 0
        for dim, score_dim in scores.items():
            coef = cls.RIASEC_DOMAINES.get(dim, {}).get(domaine_nom, 0.1)
            score_domaine += (score_dim / 100) * coef
            total_coef += coef

        riasec_weight = 40 if has_academic else 50
        if total_coef > 0:
            score_domaine = (score_domaine / total_coef) * riasec_weight
        else:
            score_domaine = riasec_weight * 0.2

        # 2. Score académique (20%) — uniquement si étudiant fourni
        score_academique = 0
        if has_academic:
            raw = cls._score_academique(etudiant, domaine_nom)  # 0-20
            score_academique = (raw / 20) * 20

        # 3. Qualité formation
        qualite_weight = 20 if has_academic else 25
        score_qualite = (formation.score_qualite / 100) * qualite_weight

        # 4. Importance stratégique
        importance_weight = 12 if has_academic else 15
        importance_scores = {
            "CRITIQUE": importance_weight,
            "ELEVEE": round(importance_weight * 0.8),
            "MOYENNE": round(importance_weight * 0.53),
            "FAIBLE": round(importance_weight * 0.2),
        }
        score_importance = importance_scores.get(formation.importance_strategique, round(importance_weight * 0.33))

        # 5. Accessibilité / coût
        cout_weight = 8 if has_academic else 10
        if formation.cout_annuel > 0:
            score_cout = max(0, cout_weight - (float(formation.cout_annuel) / 300_000))
        else:
            score_cout = cout_weight

        if formation.bourses_disponibles:
            score_cout = min(score_cout + 2, cout_weight)

        return round(score_domaine + score_academique + score_qualite + score_importance + score_cout, 1)

    @classmethod
    def _attribuer_plans(cls, matches: List[ScoreMatch]) -> List[ScoreMatch]:
        """
        Attribue les plans (Principal, Alternatif, Exploratoire)
        selon les seuils de score.
        """
        for match in matches:
            if match.score >= 75:
                match.plan = PlanRecommandation.PRINCIPAL
            elif match.score >= 55:
                match.plan = PlanRecommandation.ALTERNATIF
            else:
                match.plan = PlanRecommandation.EXPLORATOIRE
        return matches

    @classmethod
    def _justifier_metier(cls, scores: dict, metier, score: float) -> str:
        """Génère une justification pour un métier recommandé."""
        profil_top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        dims = " et ".join([d for d, _ in profil_top])

        return (
            f"Ce métier correspond bien à vos affinités en {dims}. "
            f"Avec un taux d'emploi de {metier.taux_emploi}% et une demande "
            f"{metier.get_demande_marche_display().lower()}, c'est un choix "
            f"pertinent pour votre profil. Revenu moyen : {metier.revenu_moyen_formate}/mois."
        )

    @classmethod
    def _justifier_formation(cls, scores: dict, formation, score: float) -> str:
        """Génère une justification pour une formation recommandée."""
        return (
            f"Cette formation en {formation.domaine.nom} à "
            f"{formation.etablissement.nom} présente un bon taux d'insertion "
            f"({formation.taux_insertion_12mois}%) et un score qualité de "
            f"{formation.score_qualite}/100. Coût : {formation.cout_total_formate}."
        )

    @classmethod
    def _points_forts_metier(cls, scores: dict, metier) -> List[str]:
        points = []
        if metier.taux_emploi >= 80:
            points.append(f"Excellent taux d'emploi ({metier.taux_emploi}%)")
        if metier.demande_marche in ["TRES_FORTE", "FORTE"]:
            points.append("Forte demande sur le marché")
        if float(metier.revenu_moyen) >= 400000:
            points.append("Bon niveau de rémunération")
        return points

    @classmethod
    def _points_attention_metier(cls, metier) -> List[str]:
        points = []
        if metier.duree_formation_typique_annees >= 6:
            points.append(f"Formation longue ({metier.duree_formation_typique_annees} ans)")
        if metier.taux_emploi < 60:
            points.append(f"Taux d'emploi modéré ({metier.taux_emploi}%)")
        return points

    @classmethod
    def _points_forts_formation(cls, scores: dict, formation) -> List[str]:
        points = []
        if formation.score_qualite >= 70:
            points.append(f"Formation de qualité (score: {formation.score_qualite}/100)")
        if formation.bourses_disponibles:
            points.append("Bourses disponibles")
        if formation.taux_insertion_12mois >= 75:
            points.append(f"Bonne insertion professionnelle ({formation.taux_insertion_12mois}%)")
        return points

    @classmethod
    def _points_attention_formation(cls, formation) -> List[str]:
        points = []
        if float(formation.cout_annuel) > 1000000:
            points.append(f"Coût élevé ({formation.cout_total_formate})")
        if formation.date_limite_inscription:
            from django.utils import timezone
            jours_restants = (formation.date_limite_inscription - timezone.now().date()).days
            if jours_restants < 30:
                points.append(f"Inscription dans {jours_restants} jours")
        return points
