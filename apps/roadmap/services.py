"""
Service de la roadmap évolutive.

Fonctionnalités :
- Initialisation d'une roadmap pour un étudiant (génère les étapes par défaut)
- Progression globale par phase
- Ajout d'étapes personnalisées
- Jalons à venir
"""
from datetime import date
from django.db.models import Count, Q
from django.utils import timezone
from typing import List

from apps.roadmap.models import (
    EtapeRoadmap, EtapePersonnelleEtudiant, JalonRoadmap,
    PhaseRoadmap, StatutEtape,
)


class RoadmapService:
    """Centralise la logique métier de la roadmap."""

    @staticmethod
    def determiner_phase_etudiant(etudiant) -> str:
        """
        Détermine la phase de roadmap d'un étudiant en fonction de son profil.
        """
        try:
            sp = etudiant.student_profile
            niveau = (sp.niveau_actuel or "").upper()
            if "COLLEGE" in niveau or niveau in ("6E", "5E", "4E", "3E"):
                return PhaseRoadmap.COLLEGE
            elif "SECONDE" in niveau or "PREMIERE" in niveau or "TERMINALE" in niveau:
                return PhaseRoadmap.LYCEE
            elif "POST_BAC" in niveau or "L1" in niveau or "L2" in niveau or "L3" in niveau \
                 or "MASTER" in niveau or "LICENCE" in niveau:
                return PhaseRoadmap.POST_BAC
        except Exception:
            pass
        # Défaut : Lycée
        return PhaseRoadmap.LYCEE

    @staticmethod
    def initialiser_roadmap_etudiant(etudiant, phase: str = None) -> List[EtapePersonnelleEtudiant]:
        """
        Crée les étapes personnalisées pour un étudiant à partir du template
        d'étapes génériques correspondant à sa phase.
        Idempotent : ne recrée pas les étapes déjà existantes.
        """
        if phase is None:
            phase = RoadmapService.determiner_phase_etudiant(etudiant)

        etapes_generiques = EtapeRoadmap.objects.filter(phase=phase, is_active=True)
        creees = []
        for etape_gen in etapes_generiques:
            etape, created = EtapePersonnelleEtudiant.objects.get_or_create(
                etudiant=etudiant,
                etape_generique=etape_gen,
                defaults={
                    "phase": etape_gen.phase,
                    "categorie": etape_gen.categorie,
                    "titre": etape_gen.titre,
                    "description": etape_gen.description,
                    "ordre": etape_gen.ordre,
                },
            )
            if created:
                creees.append(etape)
        return creees

    @staticmethod
    def progression_etudiant(etudiant) -> dict:
        """
        Calcule la progression globale de l'étudiant par phase.
        Retourne un dict par phase avec : total, completes, en_cours, pourcentage.
        """
        result = {}
        for phase in PhaseRoadmap.values:
            etapes = EtapePersonnelleEtudiant.objects.filter(etudiant=etudiant, phase=phase)
            total = etapes.count()
            completes = etapes.filter(statut=StatutEtape.COMPLETE).count()
            en_cours = etapes.filter(statut=StatutEtape.EN_COURS).count()
            bloques = etapes.filter(statut=StatutEtape.BLOQUE).count()
            pourcentage = round((completes / total) * 100, 1) if total > 0 else 0
            result[phase] = {
                "total": total,
                "completes": completes,
                "en_cours": en_cours,
                "bloques": bloques,
                "pourcentage": pourcentage,
            }
        return result

    @staticmethod
    def progression_phase(etudiant, phase: str) -> dict:
        """Progression détaillée pour une phase donnée."""
        return RoadmapService.progression_etudiant(etudiant).get(phase, {})

    @staticmethod
    def etapes_a_venir(etudiant, limit: int = 10) -> List[EtapePersonnelleEtudiant]:
        """Étapes non complétées triées par date objectif."""
        return list(
            EtapePersonnelleEtudiant.objects
            .filter(etudiant=etudiant)
            .exclude(statut=StatutEtape.COMPLETE)
            .exclude(statut=StatutEtape.ANNULE)
            .order_by("date_objectif", "ordre")[:limit]
        )

    @staticmethod
    def jalons_a_venir(etudiant, days_ahead: int = 90) -> List[JalonRoadmap]:
        """Jalons nationaux + personnels à venir dans les N prochains jours."""
        today = timezone.now().date()
        date_limite = today.fromordinal(today.toordinal() + days_ahead)
        qs = JalonRoadmap.objects.filter(
            date_evenement__gte=today,
            date_evenement__lte=date_limite,
        ).filter(
            Q(concerne_tous=True) | Q(etudiants_cibles=etudiant)
        ).distinct()
        return list(qs.order_by("date_evenement"))

    @staticmethod
    def creer_etape_personnalisee(
        etudiant,
        phase: str,
        categorie: str,
        titre: str,
        description: str = "",
        date_objectif=None,
        conseiller=None,
    ) -> EtapePersonnelleEtudiant:
        """Crée une étape personnalisée (sans template générique)."""
        return EtapePersonnelleEtudiant.objects.create(
            etudiant=etudiant,
            phase=phase,
            categorie=categorie,
            titre=titre,
            description=description,
            date_objectif=date_objectif,
            conseiller=conseiller,
        )


class RoadmapSeedService:
    """Service de seed des étapes génériques par défaut (3 phases)."""

    ETAPES_PAR_DEFAUT = [
        # ─── Phase Collège ───
        ("COLLEGE", "DECOUVERTE", "Découvre tes centres d'intérêt", 1,
         "Identifie 3 activités que tu aimes faire et 3 que tu détestes.",
         "Liste d'activités établie", 11, 14),
        ("COLLEGE", "DECOUVERTE", "Explore les grands secteurs d'activité", 2,
         "Découvre les 10 grands secteurs (santé, tech, agriculture, art, commerce, etc.).",
         "Quiz de secteurs complété", 11, 14),
        ("COLLEGE", "DECOUVERTE", "Lis 5 fiches métiers simplifiées", 3,
         "Parcours la bibliothèque de métiers et lis au moins 5 fiches.",
         "5 fiches lues", 12, 14),
        ("COLLEGE", "ORIENTATION", "Passe un test de découverte", 4,
         "Fais le test d'orientation découverte adapté au collège.",
         "Test passé", 13, 14),
        # ─── Phase Lycée ───
        ("LYCEE", "ORIENTATION", "Passe le test RIASEC complet", 1,
         "Le test RIASEC te donne ton code Holland (3 lettres) et tes intérêts professionnels.",
         "Code Holland obtenu", 15, 18),
        ("LYCEE", "ORIENTATION", "Passe le test Ikigai", 2,
         "Le test Ikigai croise tes 4 piliers : passion, mission, vocation, profession.",
         "Score Ikigai obtenu", 15, 18),
        ("LYCEE", "ACADEMIQUE", "Choisis tes spécialités (1ère/Terminale)", 3,
         "Sélectionne 3 spécialités en première puis 2 en terminale en cohérence avec ton projet.",
         "Spécialités validées", 15, 17),
        ("LYCEE", "ACADEMIQUE", "Prépare tes examens nationaux", 4,
         "Établis un planning de révision et utilise les annales de la bibliothèque.",
         "Planning de révision + 5 annales faites", 16, 18),
        ("LYCEE", "CONCOURS", "Identifie 5 écoles cibles", 5,
         "Recherche 5 établissements alignés avec ton profil et note leurs critères d'admission.",
         "Liste de 5 écoles avec critères", 16, 18),
        ("LYCEE", "CONCOURS", "Calendrier des concours", 6,
         "Récupère les dates des concours des écoles ciblées et ajoute-les à ton agenda.",
         "Toutes les dates dans l'agenda", 16, 18),
        # ─── Phase Post-Bac ───
        ("POST_BAC", "CANDIDATURE", "Prépare ton dossier de candidature", 1,
         "Réunis : relevés de notes, lettre de motivation, CV, recommandations.",
         "Dossier complet", 18, 25),
        ("POST_BAC", "CANDIDATURE", "Soumets tes candidatures", 2,
         "Dépose tes dossiers via la plateforme et les sites des écoles.",
         "Min. 5 candidatures soumises", 18, 25),
        ("POST_BAC", "ADMISSION", "Réponds aux propositions d'admission", 3,
         "Accepte ou refuse les admissions dans les délais impartis.",
         "Décision envoyée", 18, 25),
        ("POST_BAC", "ADMISSION", "Finalise ton inscription administrative", 4,
         "Inscription, paiement des frais, carte d'étudiant.",
         "Carte d'étudiant obtenue", 18, 25),
        ("POST_BAC", "STAGE", "Recherche un stage de 1ère année", 5,
         "Identifie 10 entreprises, envoie 5 candidatures, décroche 1 stage.",
         "Stage signé", 19, 25),
        ("POST_BAC", "STAGE", "Recherche une alternance (si éligible)", 6,
         "Si tu es en formation éligible, identifie des contrats d'alternance.",
         "Contrat d'alternance signé", 18, 25),
        ("POST_BAC", "INSERTION", "Prépare ton CV et LinkedIn", 7,
         "CV à jour, profil LinkedIn optimisé, portfolio si pertinent.",
         "CV + LinkedIn publiés", 20, 25),
        ("POST_BAC", "FINANCEMENT", "Identifie des bourses", 8,
         "Recherche les bourses disponibles (gouvernement, école, privées) et postule.",
         "Min. 3 demandes de bourse soumises", 18, 25),
    ]

    @classmethod
    def seed_etapes_par_defaut(cls):
        """Crée ou met à jour les étapes génériques par défaut."""
        created_count = 0
        for phase, cat, titre, ordre, desc, critere, age_min, age_max in cls.ETAPES_PAR_DEFAUT:
            _, created = EtapeRoadmap.objects.update_or_create(
                phase=phase, titre=titre,
                defaults={
                    "categorie": cat,
                    "description": desc,
                    "ordre": ordre,
                    "critere_completion": critere,
                    "age_min": age_min,
                    "age_max": age_max,
                    "is_active": True,
                    "is_obligatoire": ordre <= 3,
                },
            )
            if created:
                created_count += 1
        return created_count
