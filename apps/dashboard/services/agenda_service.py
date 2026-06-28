"""
Service Agenda — gestion des événements et rappels.
"""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.dashboard.models import (
    EvenementAgenda, Rappel, DemarcheInscription,
    StatutRappel, CanalNotification,
)

class AgendaService:
    """Service de gestion de l'agenda et des rappels."""

    @classmethod
    @transaction.atomic
    def creer_rappels_pour_evenement(cls, evenement: EvenementAgenda) -> list:
        """
        Crée automatiquement les rappels pour un événement
        selon sa configuration.
        """
        rappels_crees = []

        # Supprimer les anciens rappels actifs
        Rappel.objects.filter(
            evenement_agenda=evenement,
            statut=StatutRappel.ACTIF,
        ).delete()

        config_rappels = [
            (evenement.rappel_j_30, 30),
            (evenement.rappel_j_7, 7),
            (evenement.rappel_j_1, 1),
            (evenement.rappel_j_0, 0),
        ]

        for actif, jours_avant in config_rappels:
            if not actif:
                continue

            date_envoi = evenement.date_debut - timedelta(days=jours_avant)

            # Ne créer que si la date d'envoi est dans le futur
            if date_envoi < timezone.now():
                continue

            titre = f"Rappel : {evenement.titre}"
            if jours_avant == 0:
                message = f"C'est aujourd'hui ! {evenement.titre}"
            elif jours_avant == 1:
                message = f"C'est demain : {evenement.titre}"
            else:
                message = f"Dans {jours_avant} jours : {evenement.titre}"

            if evenement.lieu:
                message += f"\nLieu : {evenement.lieu}"

            rappel = Rappel.objects.create(
                utilisateur=evenement.utilisateur,
                evenement_agenda=evenement,
                titre=titre,
                message=message,
                date_envoi_prevue=date_envoi,
                canal=CanalNotification.IN_APP,
                statut=StatutRappel.ACTIF,
            )
            rappels_crees.append(rappel)

        return rappels_crees

    @classmethod
    @transaction.atomic
    def creer_rappels_pour_demarche(cls, demarche: DemarcheInscription) -> list:
        """Crée un rappel pour une démarche avec échéance."""
        if not demarche.date_echeance or not demarche.rappel_actif:
            return []

        # Supprimer les anciens rappels
        Rappel.objects.filter(
            demarche=demarche,
            statut=StatutRappel.ACTIF,
        ).delete()

        rappels_crees = []

        # Rappel X jours avant
        date_rappel = demarche.date_echeance - timedelta(
            days=demarche.jours_avant_rappel
        )

        if date_rappel > timezone.now():
            rappel = Rappel.objects.create(
                utilisateur=demarche.etudiant,
                demarche=demarche,
                titre=f"Échéance proche : {demarche.titre}",
                message=(
                    f"La démarche '{demarche.titre}' est à compléter "
                    f"avant le {demarche.date_echeance.strftime('%d/%m/%Y')}."
                ),
                date_envoi_prevue=date_rappel,
                canal=CanalNotification.IN_APP,
                statut=StatutRappel.ACTIF,
            )
            rappels_crees.append(rappel)

        # Rappel la veille
        date_veille = demarche.date_echeance - timedelta(days=1)
        if date_veille > timezone.now():
            rappel = Rappel.objects.create(
                utilisateur=demarche.etudiant,
                demarche=demarche,
                titre=f"Dernier jour demain : {demarche.titre}",
                message=(
                    f"Il ne reste qu'un jour pour compléter "
                    f"'{demarche.titre}'."
                ),
                date_envoi_prevue=date_veille,
                canal=CanalNotification.IN_APP,
                statut=StatutRappel.ACTIF,
            )
            rappels_crees.append(rappel)

        return rappels_crees

    @classmethod
    def get_agenda_complet(
        cls,
        utilisateur,
        date_debut=None,
        date_fin=None,
    ) -> list:
        """
        Retourne l'agenda complet d'un utilisateur sur une période.
        Format adapté pour un calendrier visuel (FullCalendar, etc.).
        """
        if not date_debut:
            date_debut = timezone.now() - timedelta(days=7)
        if not date_fin:
            date_fin = timezone.now() + timedelta(days=60)

        evenements = EvenementAgenda.objects.filter(
            utilisateur=utilisateur,
            date_debut__gte=date_debut,
            date_debut__lte=date_fin,
        ).order_by("date_debut")

        # Ajouter les rappels comme événements virtuels
        rappels = Rappel.objects.filter(
            utilisateur=utilisateur,
            statut=StatutRappel.ACTIF,
            date_envoi_prevue__gte=date_debut,
            date_envoi_prevue__lte=date_fin,
        )

        items = []

        for evt in evenements:
            items.append({
                "id": str(evt.id),
                "title": evt.titre,
                "start": evt.date_debut.isoformat(),
                "end": evt.date_fin.isoformat() if evt.date_fin else None,
                "allDay": evt.toute_la_journee,
                "color": evt.couleur,
                "type": evt.type,
                "type_display": evt.get_type_display(),
                "lieu": evt.lieu,
                "est_termine": evt.est_termine,
                "est_annule": evt.est_annule,
                "source": "evenement",
            })

        for rappel in rappels:
            items.append({
                "id": f"rappel-{rappel.id}",
                "title": rappel.titre,
                "start": rappel.date_envoi_prevue.isoformat(),
                "allDay": True,
                "color": "#F59E0B",
                "type": "RAPPEL",
                "source": "rappel",
            })

        return items

    @classmethod
    def get_prochaines_echeances(cls, utilisateur, limit: int = 10) -> list:
        """Retourne les prochaines échéances (événements + démarches)."""
        echeances = []

        # Événements à venir
        for evt in EvenementAgenda.objects.a_venir(utilisateur, jours=60)[:limit]:
            echeances.append({
                "type": "evenement",
                "titre": evt.titre,
                "date": evt.date_debut,
                "jours_restants": evt.jours_avant,
                "type_display": evt.get_type_display(),
                "icon": "calendrier",
            })

        # Démarches avec échéance
        for dem in DemarcheInscription.objects.a_venir(utilisateur, jours=60)[:limit]:
            echeances.append({
                "type": "demarche",
                "titre": dem.titre,
                "date": dem.date_echeance,
                "jours_restants": dem.jours_restants,
                "type_display": dem.get_type_display(),
                "icon": "echeance",
                "en_retard": dem.est_en_retard,
            })

        # Trier par date
        echeances.sort(key=lambda x: x["date"])

        return [
            {**e, "date": e["date"].isoformat()}
            for e in echeances[:limit]
        ]
