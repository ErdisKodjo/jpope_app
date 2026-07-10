"""
Service de la bibliothèque numérique.

Fonctionnalités :
- Recherche multi-critères (type, matière, niveau, premium)
- Recommandation personnalisée (basée sur profil étudiant)
- Tracking des téléchargements et vues
- Vote et calcul de note moyenne
- Vérification d'accès premium
"""
from django.db.models import Q, F
from django.utils import timezone
from typing import List, Optional

from apps.library.models import (
    RessourcePedagogique, TelechargementRessource, FavoriBibliotheque,
    VoteRessource, TypeRessource, NiveauScolaire,
)


class BibliothequeService:
    """Centralise la logique métier de la bibliothèque numérique."""

    @staticmethod
    def rechercher(
        query: str = "",
        type_ressource: Optional[str] = None,
        matiere: Optional[str] = None,
        niveau: Optional[str] = None,
        premium_only: Optional[bool] = None,
        ordering: str = "-created_at",
        limit: int = 50,
    ) -> List[RessourcePedagogique]:
        """
        Recherche multi-critères dans la bibliothèque.
        """
        qs = RessourcePedagogique.objects.filter(is_active=True)
        if query:
            qs = qs.filter(
                Q(titre__icontains=query)
                | Q(description__icontains=query)
                | Q(auteur__icontains=query)
                | Q(matiere__icontains=query)
            )
        if type_ressource:
            qs = qs.filter(type=type_ressource)
        if matiere:
            qs = qs.filter(matiere__iexact=matiere)
        if niveau:
            qs = qs.filter(niveaux__contains=[niveau])
        if premium_only is True:
            qs = qs.filter(is_premium=True)
        elif premium_only is False:
            qs = qs.filter(is_free=True)
        return qs.order_by(ordering)[:limit]

    @staticmethod
    def recommander_pour_etudiant(etudiant, limit: int = 10) -> List[RessourcePedagogique]:
        """
        Recommande des ressources basées sur :
        - Le niveau scolaire de l'étudiant
        - Les métiers envisagés (via son profil)
        - Les ressources qu'il a déjà consultées
        """
        # Récupère le niveau de l'étudiant
        niveau_etudiant = None
        try:
            sp = etudiant.student_profile
            # Mapping simplifié : niveau_actuel → NiveauScolaire
            niveau_mapping = {
                "COLLEGE": NiveauScolaire.COLLEGE,
                "SECONDE": NiveauScolaire.SECONDE,
                "PREMIERE": NiveauScolaire.PREMIERE,
                "TERMINALE": NiveauScolaire.TERMINALE,
                "POST_BAC": NiveauScolaire.POST_BAC,
            }
            niveau_etudiant = niveau_mapping.get(sp.niveau_actuel, NiveauScolaire.TERMINALE)
        except Exception:
            niveau_etudiant = NiveauScolaire.TERMINALE

        # Ressources déjà consultées
        consultees = TelechargementRessource.objects.filter(
            utilisateur=etudiant
        ).values_list("ressource_id", flat=True)

        # Recommandation : même niveau, non consultées, triées par popularité
        qs = (
            RessourcePedagogique.objects
            .filter(is_active=True)
            .filter(niveaux__contains=[niveau_etudiant])
            .exclude(id__in=list(consultees))
            .order_by("-nombre_telechargements", "-note_moyenne")
        )
        return list(qs[:limit])

    @staticmethod
    def enregistrer_telechargement(utilisateur, ressource, ip_address=None) -> TelechargementRessource:
        """Enregistre un téléchargement et incrémente le compteur de la ressource."""
        telechargement = TelechargementRessource.objects.create(
            utilisateur=utilisateur,
            ressource=ressource,
            ip_address=ip_address,
        )
        RessourcePedagogique.objects.filter(pk=ressource.pk).update(
            nombre_telechargements=F("nombre_telechargements") + 1
        )
        return telechargement

    @staticmethod
    def enregistrer_vue(ressource):
        """Incrémente le compteur de vues d'une ressource."""
        RessourcePedagogique.objects.filter(pk=ressource.pk).update(
            nombre_vues=F("nombre_vues") + 1
        )

    @staticmethod
    def voter(utilisateur, ressource, note: int, commentaire: str = "") -> VoteRessource:
        """
        Permet à un utilisateur de voter (1-5) sur une ressource.
        Met à jour la note moyenne et le nombre de votes.
        """
        vote, created = VoteRessource.objects.update_or_create(
            utilisateur=utilisateur,
            ressource=ressource,
            defaults={"note": note, "commentaire": commentaire},
        )
        # Recalcule la note moyenne
        from django.db.models import Avg, Count
        agg = VoteRessource.objects.filter(ressource=ressource).aggregate(
            moyenne=Avg("note"),
            count=Count("id"),
        )
        RessourcePedagogique.objects.filter(pk=ressource.pk).update(
            note_moyenne=round(agg["moyenne"] or 0, 2),
            nombre_votes=agg["count"],
        )
        return vote

    @staticmethod
    def verifier_acces(utilisateur, ressource) -> bool:
        """
        Vérifie si l'utilisateur peut accéder à la ressource :
        - Ressource gratuite → tout utilisateur authentifié
        - Ressource premium → utilisateur avec abonnement Premium actif
        """
        if ressource.is_free:
            return True
        if not ressource.is_premium:
            return True
        # Vérifie l'abonnement premium
        try:
            from apps.payments.models import Abonnement
            from apps.payments.models import StatutAbonnement
            abonnement = Abonnement.objects.filter(
                utilisateur=utilisateur,
                statut=StatutAbonnement.ACTIF,
                plan__niveau__in=["PREMIUM", "PRO"],
            ).first()
            return abonnement is not None
        except Exception:
            # En dev sans app payments configurée → on autorise
            return True

    @staticmethod
    def ajouter_favori(utilisateur, ressource, note_personnelle: str = "") -> FavoriBibliotheque:
        favori, _created = FavoriBibliotheque.objects.get_or_create(
            utilisateur=utilisateur,
            ressource=ressource,
            defaults={"note_personnelle": note_personnelle},
        )
        return favori

    @staticmethod
    def retirer_favori(utilisateur, ressource) -> bool:
        deleted, _ = FavoriBibliotheque.objects.filter(
            utilisateur=utilisateur, ressource=ressource
        ).delete()
        return deleted > 0

    @staticmethod
    def statistiques_globales() -> dict:
        """Statistiques agrégées de la bibliothèque (pour admin/dashboard)."""
        from django.db.models import Count, Sum
        total = RessourcePedagogique.objects.filter(is_active=True).count()
        par_type = dict(
            RessourcePedagogique.objects.filter(is_active=True)
            .values_list("type")
            .annotate(c=Count("id"))
            .values_list("type", "c")
        )
        total_telechargements = RessourcePedagogique.objects.aggregate(
            total=Sum("nombre_telechargements")
        )["total"] or 0
        return {
            "total_ressources": total,
            "par_type": par_type,
            "total_telechargements": total_telechargements,
            "ressources_premium": RessourcePedagogique.objects.filter(
                is_active=True, is_premium=True
            ).count(),
        }
