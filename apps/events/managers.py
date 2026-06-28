"""
Managers personnalisés pour l'app events.
"""
from django.db import models
from django.utils import timezone


class EvenementManager(models.Manager):
    def publies(self):
        return self.filter(statut="PUBLIE")

    def a_venir(self):
        """Événements publiés et à venir."""
        return self.publies().filter(date_debut__gte=timezone.now())

    def en_cours(self):
        """Événements en cours maintenant."""
        now = timezone.now()
        return self.publies().filter(
            date_debut__lte=now,
            date_fin__gte=now,
        )

    def passes(self):
        """Événements passés."""
        return self.publies().filter(date_debut__lt=timezone.now())

    def par_type(self, type_evenement):
        return self.publies().filter(type=type_evenement)

    def par_ville(self, ville):
        return self.publies().filter(ville__iexact=ville)

    def featured(self):
        return self.publies().filter(is_featured=True)

    def avec_inscriptions_ouvertes(self):
        """Événements avec inscriptions encore ouvertes."""
        now = timezone.now()
        return self.publies().filter(
            inscriptions_ouvertes=True,
            date_debut__gte=now,
            statut__in=["PUBLIE"],
        ).filter(
            models.Q(date_limite_inscription__isnull=True)
            | models.Q(date_limite_inscription__gte=now)
        )

    def cette_semaine(self):
        """Événements des 7 prochains jours."""
        debut = timezone.now()
        fin = debut + timezone.timedelta(days=7)
        return self.publies().filter(
            date_debut__gte=debut,
            date_debut__lte=fin,
        )

    def ce_mois(self):
        """Événements des 30 prochains jours."""
        debut = timezone.now()
        fin = debut + timezone.timedelta(days=30)
        return self.publies().filter(
            date_debut__gte=debut,
            date_debut__lte=fin,
        )

    def par_domaine(self, domaine_id):
        return self.publies().filter(domaines_concernes__id=domaine_id)

    def par_etablissement(self, etablissement_id):
        return self.filter(etablissement_id=etablissement_id)

    def proches(self, latitude, longitude, rayon_km=50):
        """
        Événements proches d'une position géographique.
        Utilise la formule de Haversine simplifiée.
        """
        # Approximation simple : 1° ≈ 111 km
        delta_lat = rayon_km / 111
        delta_lon = rayon_km / (111 * 0.64)  # Ajustement cos(latitude Togo)

        return self.publies().filter(
            latitude__range=(latitude - delta_lat, latitude + delta_lat),
            longitude__range=(longitude - delta_lon, longitude + delta_lon),
        )


class InscriptionEvenementManager(models.Manager):
    def actives(self, utilisateur=None):
        """Inscriptions actives (non annulées)."""
        qs = self.exclude(statut="ANNULE")
        if utilisateur:
            qs = qs.filter(utilisateur=utilisateur)
        return qs

    def confirmees(self, utilisateur=None):
        qs = self.filter(statut="CONFIRME")
        if utilisateur:
            qs = qs.filter(utilisateur=utilisateur)
        return qs

    def pour_evenement(self, evenement):
        return self.filter(evenement=evenement).exclude(statut="ANNULE")

    def presents(self, evenement):
        return self.filter(evenement=evenement, a_participe=True)

    def liste_attente(self, evenement):
        return self.filter(
            evenement=evenement,
            statut="LISTE_ATTENTE",
        ).order_by("date_inscription")

    def est_inscrit(self, utilisateur, evenement) -> bool:
        """Vérifie si un utilisateur est inscrit à un événement."""
        return self.filter(
            utilisateur=utilisateur,
            evenement=evenement,
        ).exclude(statut="ANNULE").exists()
