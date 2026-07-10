"""
Service du simulateur d'admissions prédictif.

Conformément au cahier des charges (section 2.1 — Candidat, Simulateur d'Admissions) :
"Outil prédictif calculant le pourcentage de chances d'intégrer une formation spécifique
en croisant la moyenne pondérée de l'élève avec les critères d'admission historiques
de l'établissement."

Algorithme :
1. Si des données historiques existent pour la formation → modèle empirique basé sur
   la proportion d'admis ayant un profil similaire (moyenne ± 1 point, même série de bac).
2. Si pas de données historiques → heuristique basée sur les critères affichés de la formation
   (prérequis, séries admises, taux de réussite, places_disponibles/nombre_inscrits).
3. Le résultat inclut :
   - pourcentage de chances (0-100)
   - niveau de confiance (Faible/Moyen/Élevé — selon taille de l'échantillon historique)
   - explication détaillée (transparence du calcul)
   - recommandations pour améliorer ses chances
"""
import logging
from typing import Dict, List, Tuple
from django.db.models import Q, Avg, Count

from apps.catalog.models import (
    Formation, AdmissionHistorique, ResultatSimulateur,
)

logger = logging.getLogger(__name__)


class SimulateurAdmissionService:
    """
    Simulateur prédictif d'admission.
    """

    # ─── Seuils de confiance selon la taille de l'échantillon ───
    SEUIL_CONFIANCE_ELEVE = 50    # >= 50 enregistrements historiques
    SEUIL_CONFIANCE_MOYEN = 15    # >= 15 enregistrements
    # < 15 → confiance faible

    @classmethod
    def simuler(
        cls,
        etudiant,
        formation: Formation,
        moyenne_saisie: float,
        serie_bac_saisie: str = "",
    ) -> ResultatSimulateur:
        """
        Lance une simulation pour un étudiant sur une formation.

        Args:
            etudiant: User instance
            formation: Formation cible
            moyenne_saisie: moyenne /20 (entre 0 et 20)
            serie_bac_saisie: série du bac (C, D, G2, L, etc.)

        Returns:
            ResultatSimulateur instance persistée
        """
        # Validation
        if not (0 <= moyenne_saisie <= 20):
            raise ValueError("La moyenne doit être comprise entre 0 et 20.")

        # ── Étape 1 : vérifier l'éligibilité de base (série de bac acceptée)
        eligible_serie = True
        series_acceptees = formation.serie_bac_admises or []
        if serie_bac_saisie and series_acceptees:
            eligible_serie = serie_bac_saisie.upper() in [s.upper() for s in series_acceptees]

        # ── Étape 2 : récupérer l'historique des admissions
        historique = AdmissionHistorique.objects.filter(formation=formation)
        taille_echantillon = historique.count()

        # ── Étape 3 : calculer le pourcentage selon la disponibilité des données
        if taille_echantillon >= cls.SEUIL_CONFIANCE_MOYEN:
            pourcentage, confiance, explication = cls._mode_empirique(
                historique, moyenne_saisie, serie_bac_saisie, eligible_serie
            )
        else:
            pourcentage, confiance, explication = cls._mode_heuristique(
                formation, moyenne_saisie, serie_bac_saisie, eligible_serie, taille_echantillon
            )

        # ── Étape 4 : ajustement si série non éligible
        if not eligible_serie:
            pourcentage = min(pourcentage * 0.1, 5.0)  # Division par 10, plafonné à 5%
            explication["serie_non_eligible"] = True
            explication["series_acceptees"] = series_acceptees
            confiance = "FAIBLE"

        # ── Étape 5 : recommandations
        recommandations = cls._generer_recommandations(
            formation, moyenne_saisie, serie_bac_saisie, eligible_serie, pourcentage
        )

        # ── Étape 6 : sauvegarder la simulation
        resultat = ResultatSimulateur.objects.create(
            etudiant=etudiant,
            formation=formation,
            moyenne_saisie=moyenne_saisie,
            serie_bac_saisie=serie_bac_saisie,
            pourcentage_chances=round(pourcentage, 1),
            niveau_confiance=confiance,
            explication=explication,
            recommandations=recommandations,
        )

        logger.info(
            f"Simulation {etudiant.email} → {formation.nom} : "
            f"{resultat.pourcentage_chances}% (confiance: {confiance})"
        )

        return resultat

    # ──────────────────────────────────────────────
    # Mode empirique — basé sur les admissions historiques
    # ──────────────────────────────────────────────

    @classmethod
    def _mode_empirique(
        cls,
        historique,
        moyenne: float,
        serie_bac: str,
        eligible_serie: bool,
    ) -> Tuple[float, str, dict]:
        """
        Calcule le % à partir des admissions passées.
        - Récupère les candidats avec une moyenne similaire (± 1 point)
        - Et la même série de bac (si série saisie)
        - Calcule la proportion d'admis dans cet échantillon
        """
        # Filtre moyenne ± 1 point
        qs = historique.filter(moyenne_bac__gte=moyenne - 1, moyenne_bac__lte=moyenne + 1)
        if serie_bac:
            qs_serie = qs.filter(serie_bac__iexact=serie_bac)
            if qs_serie.exists():
                qs = qs_serie  # Privilégie le filtre par série si données disponibles

        total = qs.count()
        admis = qs.filter(a_ete_admis=True).count()

        # Détermine la confiance
        if total >= cls.SEUIL_CONFIANCE_ELEVE:
            confiance = "ELEVE"
        elif total >= cls.SEUIL_CONFIANCE_MOYEN:
            confiance = "MOYEN"
        else:
            confiance = "FAIBLE"

        if total == 0:
            # Pas de profil similaire → on élargit à tout l'historique
            total = historique.count()
            admis = historique.filter(a_ete_admis=True).count()
            confiance = "FAIBLE"

        pourcentage = (admis / total * 100) if total > 0 else 0

        # Affine par moyenne : un candidat au-dessus de la moyenne des admis a plus de chances
        moy_admis = historique.filter(
            a_ete_admis=True
        ).aggregate(m=Avg("moyenne_bac"))["m"]
        if moy_admis:
            ecart = moyenne - moy_admis
            bonus = max(min(ecart * 5, 20), -20)  # Bonus/malus plafonné ±20 points
            pourcentage = max(0, min(100, pourcentage + bonus))

        # Taux de sélection de l'établissement (admis / candidats totaux historiques)
        total_tous = historique.count()
        admis_tous = historique.filter(a_ete_admis=True).count()
        taux_selection_global = (admis_tous / total_tous * 100) if total_tous > 0 else 50

        explication = {
            "methode": "EMPIRIQUE",
            "taille_echantillon_similaire": total,
            "taille_echantillon_total": total_tous,
            "nb_admis_similaires": admis,
            "moyenne_bac_admis": round(moy_admis, 2) if moy_admis else None,
            "ecart_vs_moyenne_admis": round(moyenne - (moy_admis or 0), 2),
            "taux_selection_global_etablissement": round(taux_selection_global, 1),
            "bonus_malus_applique": round(max(min((moyenne - (moy_admis or 0)) * 5, 20), -20), 1),
        }
        return pourcentage, confiance, explication

    # ──────────────────────────────────────────────
    # Mode heuristique — basé sur les critères affichés
    # ──────────────────────────────────────────────

    @classmethod
    def _mode_heuristique(
        cls,
        formation: Formation,
        moyenne: float,
        serie_bac: str,
        eligible_serie: bool,
        taille_echantillon: int,
    ) -> Tuple[float, str, dict]:
        """
        Sans historique, on utilise une heuristique basée sur :
        - Le taux de réussite de la formation
        - Le ratio places/nombre d'inscrits (sélectivité)
        - La moyenne de l'étudiant vs prérequis
        """
        # Score de base : taux de réussite (si très bon → moins sélectif)
        score_base = max(50 - formation.taux_reussite / 2, 10)
        # Plus le taux de réussite est élevé, plus l'école accueille large

        # Ajustement places/nombre_inscrits (sélectivité)
        if formation.places_disponibles > 0 and formation.nombre_inscrits_annee > 0:
            ratio = formation.places_disponibles / formation.nombre_inscrits_annee
            # ratio proche de 1 → tout le monde est pris → 100%
            # ratio proche de 0.1 → 1 place pour 10 candidats → sélectif
            score_base = score_base * (1 + ratio) / 2

        # Ajustement moyenne vs seuil typique
        # Seuil typique estimé : 10 (Passable), 12 (AB), 14 (B)
        seuil_estime = 10
        if formation.prerequis:
            prerequis_text = " ".join(formation.prerequis).lower()
            if "très bien" in prerequis_text:
                seuil_estime = 14
            elif "bien" in prerequis_text or "mention" in prerequis_text:
                seuil_estime = 12
            elif "assez bien" in prerequis_text:
                seuil_estime = 12

        ecart_vs_seuil = moyenne - seuil_estime
        bonus = max(min(ecart_vs_seuil * 10, 30), -30)  # ±30 points max
        pourcentage = max(0, min(100, score_base + bonus))

        confiance = "FAIBLE"
        if taille_echantillon > 0:
            confiance = "MOYEN"

        explication = {
            "methode": "HEURISTIQUE",
            "taille_echantillon_historique": taille_echantillon,
            "raison_heuristique": "Données historiques insuffisantes" if taille_echantillon < cls.SEUIL_CONFIANCE_MOYEN else "Échantillon limité",
            "seuil_estime": seuil_estime,
            "ecart_vs_seuil_estime": round(ecart_vs_seuil, 2),
            "bonus_malus_applique": round(bonus, 1),
            "taux_reussite_formation": formation.taux_reussite,
            "places_disponibles": formation.places_disponibles,
            "nombre_inscrits_annee": formation.nombre_inscrits_annee,
            "score_base_calcule": round(score_base, 1),
        }
        return pourcentage, confiance, explication

    # ──────────────────────────────────────────────
    # Recommandations
    # ──────────────────────────────────────────────

    @classmethod
    def _generer_recommandations(
        cls,
        formation: Formation,
        moyenne: float,
        serie_bac: str,
        eligible_serie: bool,
        pourcentage: float,
    ) -> List[str]:
        """Génère des recommandations personnalisées pour améliorer ses chances."""
        recos = []

        if not eligible_serie:
            recos.append(
                f"⚠️ Votre série de bac ({serie_bac}) n'est pas explicitement admise. "
                "Contactez l'établissement pour vérifier les passerelles possibles ou "
                "envisagez une année de mise à niveau."
            )

        if pourcentage < 30:
            recos.append(
                "Vos chances sont faibles. Envisagez :"
            )
            recos.append("  • Postuler à des formations de backup (moins sélectives)")
            recos.append("  • Améliorer votre dossier (lettre de motivation, recommandations)")
            recos.append("  • Préparer une année de préparation ou mise à niveau")
        elif pourcentage < 60:
            recos.append(
                "Vos chances sont moyennes. Pour les améliorer :"
            )
            recos.append("  • Soignez votre lettre de motivation")
            recos.append("  • Mettez en avant vos expériences extrascolaires")
            recos.append("  • Préparez l'entretien éventuel en vous informant sur l'école")
            recos.append("  • Postulez aussi à 2-3 formations alternatives")
        else:
            recos.append(
                "✓ Vos chances sont bonnes. Maintenez votre niveau et :"
            )
            recos.append("  • Préparez un dossier solide (lettre, CV, recommandations)")
            recos.append("  • Suivez l'établissement sur les réseaux sociaux")
            recos.append("  • Participez aux journées portes ouvertes si possible")

        # Recommandation sur la moyenne
        if moyenne < 12:
            recos.append(
                f"📊 Votre moyenne ({moyenne}/20) peut être améliorée. "
                "Utilisez la bibliothèque numérique pour accéder à des annales corrigées "
                "et fiches de révision."
            )

        return recos
