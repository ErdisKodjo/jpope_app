"""
Service de classement des établissements et formations.
"""
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import List

from django.db import transaction
from django.db.models import Avg, Count, F, Q
from django.utils import timezone

from apps.catalog.models import Etablissement, Formation

logger = logging.getLogger(__name__)


@dataclass
class CritereClassement:
    """Définition d'un critère de classement."""
    code: str
    nom: str
    ponderation: float  # Somme totale = 1.0
    description: str


# MÉTHODOLOGIE OFFICIELLE DE CLASSEMENT
# Transparence totale : tous les critères et pondérations sont publics
CRITERES_ETABLISSEMENT = [
    CritereClassement(
        code="QUALITE_PEDA",
        nom="Qualité pédagogique",
        ponderation=0.30,
        description="Taux de réussite, ratio enseignants/étudiants",
    ),
    CritereClassement(
        code="INSERTION_PRO",
        nom="Insertion professionnelle",
        ponderation=0.25,
        description="Taux d'insertion à 6 et 12 mois",
    ),
    CritereClassement(
        code="EQUIPEMENTS",
        nom="Équipements et infrastructures",
        ponderation=0.15,
        description="Bibliothèques, labos, résidences, etc.",
    ),
    CritereClassement(
        code="COUT_ACCESSIBILITE",
        nom="Coût et accessibilité",
        ponderation=0.15,
        description="Frais de scolarité, bourses disponibles",
    ),
    CritereClassement(
        code="VIE_ETUDIANTE",
        nom="Vie étudiante",
        ponderation=0.10,
        description="Clubs, sports, associations",
    ),
    CritereClassement(
        code="REPUTATION",
        nom="Réputation et avis",
        ponderation=0.05,
        description="Note moyenne des avis étudiants",
    ),
]


class RankingService:
    """
    Service de calcul des classements.

    Méthodologie transparente :
    - Normalisation min-max par critère
    - Score final = Σ (critère × pondération)
    - Publication annuelle avec historique
    """

    @classmethod
    @transaction.atomic
    def recalculer_classement_etablissements(cls, annee: int = None) -> dict:
        """
        Recalcule le classement de tous les établissements actifs et vérifiés.

        Returns:
            dict avec stats du recalcul
        """
        if annee is None:
            annee = timezone.now().year

        etablissements = list(
            Etablissement.objects.filter(is_active=True, is_verified=True)
        )

        if not etablissements:
            logger.warning("Aucun établissement vérifié à classer.")
            return {"status": "empty", "count": 0}

        # 1. Calculer les scores bruts par critère
        scores_bruts = cls._calculer_scores_bruts(etablissements)

        # 2. Normaliser (min-max) par critère
        scores_normalises = cls._normaliser_scores(scores_bruts)

        # 3. Calculer le score final pondéré
        for etab in etablissements:
            score_final = 0
            for critere in CRITERES_ETABLISSEMENT:
                score_critere = scores_normalises[etab.id].get(critere.code, 0)
                score_final += score_critere * critere.ponderation
            etab.score_qualite_global = round(score_final, 2)

        # 4. Trier et attribuer les rangs
        etablissements_tries = sorted(
            etablissements,
            key=lambda e: e.score_qualite_global,
            reverse=True,
        )

        for rang, etab in enumerate(etablissements_tries, start=1):
            etab.classement_national = rang
            # Mise à jour de la note globale (sur 5)
            etab.note_globale = round(Decimal(str(etab.score_qualite_global)) / 20, 2)

        # 5. Sauvegarder en bulk
        Etablissement.objects.bulk_update(
            etablissements_tries,
            ["score_qualite_global", "classement_national", "note_globale"],
        )

        logger.info(
            f"Classement {annee} recalculé : {len(etablissements_tries)} établissements"
        )

        return {
            "status": "success",
            "annee": annee,
            "count": len(etablissements_tries),
            "top_3": [
                {
                    "rang": e.classement_national,
                    "nom": str(e),
                    "score": e.score_qualite_global,
                }
                for e in etablissements_tries[:3]
            ],
        }

    @classmethod
    def _calculer_scores_bruts(cls, etablissements: list) -> dict:
        """Calcule les scores bruts pour chaque critère."""
        scores = {e.id: {} for e in etablissements}

        for etab in etablissements:
            # QUALITE_PEDA : taux_reussite + inverse ratio encadrement
            score_reussite = float(etab.taux_reussite)
            ratio = float(etab.taux_encadrement) if etab.taux_encadrement > 0 else 50
            score_encadrement = max(0, 100 - ratio)  # Plus le ratio est bas, mieux c'est
            scores[etab.id]["QUALITE_PEDA"] = (score_reussite * 0.6 + score_encadrement * 0.4)

            # INSERTION_PRO : taux d'insertion
            scores[etab.id]["INSERTION_PRO"] = float(etab.taux_insertion_professionnelle)

            # EQUIPEMENTS : nombre d'équipements listés
            nb_equipements = len(etab.equipements or [])
            scores[etab.id]["EQUIPEMENTS"] = min(nb_equipements * 10, 100)

            # COUT_ACCESSIBILITE : inverse du coût + bourses
            cout = float(etab.frais_scolarite_annuel_max)
            score_cout = max(0, 100 - (cout / 3_000_000 * 100))
            score_bourse = 20 if etab.propose_bourses else 0
            scores[etab.id]["COUT_ACCESSIBILITE"] = min(score_cout + score_bourse, 100)

            # VIE_ETUDIANTE : clubs + sports + résidences
            score_vie = 0
            score_vie += min(len(etab.clubs_et_associations or []) * 10, 40)
            score_vie += min(len(etab.sports_proposes or []) * 10, 30)
            score_vie += 30 if etab.residences_universitaires else 0
            scores[etab.id]["VIE_ETUDIANTE"] = score_vie

            # REPUTATION : note globale sur 5 → 0-100
            scores[etab.id]["REPUTATION"] = float(etab.note_globale) * 20

        return scores

    @classmethod
    def _normaliser_scores(cls, scores_bruts: dict) -> dict:
        """Normalisation min-max par critère."""
        if not scores_bruts:
            return {}

        criteres = CRITERES_ETABLISSEMENT
        normalises = {etab_id: {} for etab_id in scores_bruts}

        for critere in criteres:
            # Extraire les valeurs pour ce critère
            valeurs = [
                scores.get(critere.code, 0)
                for scores in scores_bruts.values()
            ]
            min_val = min(valeurs) if valeurs else 0
            max_val = max(valeurs) if valeurs else 1

            # Normaliser
            for etab_id, scores in scores_bruts.items():
                val = scores.get(critere.code, 0)
                if max_val - min_val > 0:
                    normalises[etab_id][critere.code] = (
                        (val - min_val) / (max_val - min_val) * 100
                    )
                else:
                    normalises[etab_id][critere.code] = 50  # Valeur neutre

        return normalises

    @classmethod
    def get_detail_classement(cls, etablissement: Etablissement) -> dict:
        """
        Retourne le détail du classement d'un établissement :
        score par critère + position.
        """
        scores_bruts = cls._calculer_scores_bruts([etablissement])
        # Note : pour un détail précis, il faudrait normaliser par rapport
        # à tous les établissements. Ici version simplifiée.

        detail = {
            "etablissement": str(etablissement),
            "classement_national": etablissement.classement_national,
            "score_global": etablissement.score_qualite_global,
            "note_globale": float(etablissement.note_globale),
            "criteres": [],
        }

        for critere in CRITERES_ETABLISSEMENT:
            detail["criteres"].append({
                "code": critere.code,
                "nom": critere.nom,
                "ponderation": critere.ponderation,
                "description": critere.description,
                "score_brut": scores_bruts.get(etablissement.id, {}).get(critere.code, 0),
            })

        return detail

    @classmethod
    def get_methodologie(cls) -> list:
        """Retourne la méthodologie officielle de classement (transparence)."""
        return [
            {
                "code": c.code,
                "nom": c.nom,
                "ponderation": c.ponderation,
                "description": c.description,
            }
            for c in CRITERES_ETABLISSEMENT
        ]
