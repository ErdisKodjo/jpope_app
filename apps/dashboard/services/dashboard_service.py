"""
Service Dashboard — synthèse et logique métier.
"""
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone

from apps.dashboard.models import (
    Favori, Voeu, DemarcheInscription, EvenementAgenda,
    StatutVoeu, StatutDemarche, TypeFavori,
)

class DashboardService:
    """Service pour la synthèse du tableau de bord étudiant."""

    @classmethod
    def get_synthese(cls, etudiant) -> dict:
        """
        Retourne une synthèse complète du dashboard pour un étudiant.
        """
        # Favoris
        favoris = Favori.objects.pour_utilisateur(etudiant)

        # Voeux
        voeux = Voeu.objects.filter(etudiant=etudiant)
        voeux_actifs = voeux.exclude(
            statut__in=[StatutVoeu.REFUSE, StatutVoeu.ABANDONNE, StatutVoeu.INSCRIT]
        )

        # Démarches
        demarches = DemarcheInscription.objects.filter(etudiant=etudiant)
        demarches_actives = demarches.filter(
            statut__in=[StatutDemarche.A_FAIRE, StatutDemarche.EN_COURS, StatutDemarche.ENVOYEE]
        )
        demarches_retard = DemarcheInscription.objects.en_retard(etudiant)

        # Agenda
        evenements = EvenementAgenda.objects.a_venir(etudiant, jours=30)
        evenements_aujourdhui = EvenementAgenda.objects.aujourdhui(etudiant)

        # Dernières recommandations
        from apps.orientation.models import Recommandation
        dernieres_recommandations = (
            Recommandation.objects
            .filter(etudiant=etudiant, a_ete_vue=False)
            .order_by("-created_at")[:5]
        )

        return {
            "favoris": {
                "total": favoris.count(),
                "formations": favoris.filter(type_entite="FORMATION").count(),
                "metiers": favoris.filter(type_entite="METIER").count(),
                "etablissements": favoris.filter(type_entite="ETABLISSEMENT").count(),
            },
            "voeux": {
                "total": voeux.count(),
                "actifs": voeux_actifs.count(),
                "brouillons": voeux.filter(statut=StatutVoeu.BROUILLON).count(),
                "soumis": voeux.filter(statut=StatutVoeu.SOUMIS).count(),
                "en_attente": voeux.filter(statut=StatutVoeu.EN_ATTENTE).count(),
                "acceptes": voeux.filter(statut=StatutVoeu.ACCEPTE).count(),
                "refuses": voeux.filter(statut=StatutVoeu.REFUSE).count(),
                "inscrits": voeux.filter(statut=StatutVoeu.INSCRIT).count(),
            },
            "demarches": {
                "total": demarches.count(),
                "actives": demarches_actives.count(),
                "a_faire": demarches.filter(statut=StatutDemarche.A_FAIRE).count(),
                "en_cours": demarches.filter(statut=StatutDemarche.EN_COURS).count(),
                "completees": demarches.filter(statut=StatutDemarche.COMPLETEE).count(),
                "en_retard": demarches_retard.count(),
            },
            "agenda": {
                "evenements_30j": evenements.count(),
                "evenements_aujourdhui": evenements_aujourdhui.count(),
            },
            "recommandations_non_vues": dernieres_recommandations.count(),
            "progression_globale": cls._calculer_progression_globale(
                etudiant, voeux, demarches
            ),
        }

    @classmethod
    def _calculer_progression_globale(
        cls,
        etudiant,
        voeux,
        demarches,
    ) -> int:
        """
        Calcule un indicateur de progression globale (0-100).

        Basé sur :
        - Profil complété : 20%
        - Tests passés : 20%
        - Favoris ajoutés : 15%
        - Voeux soumis : 25%
        - Démarches complétées : 20%
        """
        score = 0

        # 1. Profil complété (20%)
        if getattr(etudiant, "profile_complete", False):
            score += 20

        # 2. Tests passés (20%)
        from apps.orientation.models import ReponseUtilisateur, StatutTest
        nb_tests = ReponseUtilisateur.objects.filter(
            etudiant=etudiant, statut=StatutTest.TERMINE
        ).count()
        score += min(nb_tests * 10, 20)

        # 3. Favoris (15%)
        nb_favoris = Favori.objects.pour_utilisateur(etudiant).count()
        score += min(nb_favoris * 3, 15)

        # 4. Voeux soumis (25%)
        nb_voeux_soumis = voeux.exclude(statut=StatutVoeu.BROUILLON).count()
        score += min(nb_voeux_soumis * 8, 25)

        # 5. Démarches (20%)
        total_demarches = demarches.count()
        if total_demarches > 0:
            demarches_faites = demarches.filter(statut=StatutDemarche.COMPLETEE).count()
            score += int((demarches_faites / total_demarches) * 20)

        return min(score, 100)

    @classmethod
    def get_timeline(cls, etudiant, limit: int = 20) -> list:
        """
        Retourne une timeline des activités récentes de l'étudiant.
        Combine favoris, voeux, démarches et événements.
        """
        timeline = []

        # Voeux récents
        for voeu in Voeu.objects.filter(etudiant=etudiant).order_by("-updated_at")[:10]:
            timeline.append({
                "type": "voeu",
                "date": voeu.updated_at,
                "titre": f"Voeu mis à jour : {voeu.formation.nom}",
                "description": f"Statut : {voeu.get_statut_display()}",
                "icon": "voeu",
                "object_id": str(voeu.id),
            })

        # Démarches complétées
        for dem in DemarcheInscription.objects.filter(
            etudiant=etudiant,
            statut=StatutDemarche.COMPLETEE,
        ).order_by("-date_realisation")[:5]:
            timeline.append({
                "type": "demarche",
                "date": dem.date_realisation or dem.updated_at,
                "titre": f"Démarche complétée : {dem.titre}",
                "description": "",
                "icon": "demarche",
                "object_id": str(dem.id),
            })

        # Favoris ajoutés
        for fav in Favori.objects.pour_utilisateur(etudiant).order_by("-created_at")[:5]:
            timeline.append({
                "type": "favori",
                "date": fav.created_at,
                "titre": f"Favori ajouté : {fav.entite_nom}",
                "description": f"Type : {fav.get_type_entite_display()}",
                "icon": "favori",
                "object_id": str(fav.id),
            })

        # Trier par date décroissante
        timeline.sort(key=lambda x: x["date"], reverse=True)

        return [
            {
                **item,
                "date": item["date"].isoformat(),
            }
            for item in timeline[:limit]
        ]
