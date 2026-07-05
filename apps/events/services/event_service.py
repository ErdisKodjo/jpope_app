"""
Service de gestion des événements.
"""
import logging
import secrets
import uuid
from typing import Optional

from django.db import transaction
from django.db.models import Count, Q, F
from django.utils import timezone

from apps.events.models import Evenement, InscriptionEvenement, StatutInscription

logger = logging.getLogger(__name__)


class EventService:
    """Service pour la gestion des événements et inscriptions."""

    @classmethod
    @transaction.atomic
    def inscrire_utilisateur(
        cls,
        utilisateur,
        evenement: Evenement,
        nombre_accompagnants: int = 0,
        besoins_speciaux: str = "",
        source: str = "site_web",
    ) -> InscriptionEvenement:
        """
        Inscrit un utilisateur à un événement.

        Gère :
        - Vérification des places disponibles
        - Liste d'attente si complet
        - Génération du token de confirmation
        - Génération du QR code
        - Mise à jour des compteurs
        - Création automatique dans l'agenda personnel
        """
        # Vérifier si déjà inscrit
        if InscriptionEvenement.objects.est_inscrit(utilisateur, evenement):
            raise ValueError("Vous êtes déjà inscrit à cet événement.")

        # Vérifier que les inscriptions sont ouvertes
        if not evenement.inscriptions_encore_ouvertes:
            if evenement.est_complet:
                raise ValueError("L'événement est complet.")
            raise ValueError("Les inscriptions sont fermées pour cet événement.")

        # Déterminer le statut (inscrit ou liste d'attente)
        statut = StatutInscription.INSCRIT
        if evenement.capacite_max > 0 and evenement.nombre_inscrits >= evenement.capacite_max:
            statut = StatutInscription.LISTE_ATTENTE

        # Créer l'inscription
        inscription = InscriptionEvenement.objects.create(
            utilisateur=utilisateur,
            evenement=evenement,
            statut=statut,
            nombre_accompagnants=nombre_accompagnants,
            besoins_speciaux=besoins_speciaux,
            source_inscription=source,
            token_confirmation=secrets.token_urlsafe(32),
            qr_code_token=uuid.uuid4().hex,
        )

        # Mettre à jour le compteur si pas en liste d'attente
        if statut == StatutInscription.INSCRIT:
            Evenement.objects.filter(pk=evenement.pk).update(nombre_inscrits=F("nombre_inscrits") + 1)

        # Créer un événement dans l'agenda personnel de l'utilisateur
        cls._creer_entree_agenda(utilisateur, evenement, inscription)

        logger.info(
            f"Inscription {statut}: {utilisateur.email} → {evenement.titre}"
        )

        return inscription

    @classmethod
    @transaction.atomic
    def annuler_inscription(
        cls,
        utilisateur,
        evenement: Evenement,
    ) -> bool:
        """Annule l'inscription d'un utilisateur à un événement."""
        try:
            inscription = InscriptionEvenement.objects.get(
                utilisateur=utilisateur,
                evenement=evenement,
            )
        except InscriptionEvenement.DoesNotExist:
            raise ValueError("Inscription introuvable.")

        if inscription.statut == StatutInscription.ANNULE:
            raise ValueError("L'inscription est déjà annulée.")

        # Annuler
        inscription.annuler()

        # Promouvoir le premier de la liste d'attente
        cls._promouvoir_liste_attente(evenement)

        # Supprimer l'entrée d'agenda
        cls._supprimer_entree_agenda(utilisateur, evenement)

        logger.info(f"Annulation inscription: {utilisateur.email} → {evenement.titre}")
        return True

    @classmethod
    @transaction.atomic
    def confirmer_inscription(cls, token: str) -> Optional[InscriptionEvenement]:
        """Confirme une inscription via le token reçu par email."""
        try:
            inscription = InscriptionEvenement.objects.get(
                token_confirmation=token,
                statut=StatutInscription.INSCRIT,
            )
            inscription.confirmer()
            return inscription
        except InscriptionEvenement.DoesNotExist:
            return None

    @classmethod
    @transaction.atomic
    def checkin_inscription(
        cls,
        qr_token: str,
    ) -> Optional[InscriptionEvenement]:
        """Check-in d'un participant via QR code."""
        try:
            inscription = InscriptionEvenement.objects.get(
                qr_code_token=qr_token,
                statut__in=[StatutInscription.INSCRIT, StatutInscription.CONFIRME],
            )
            inscription.marquer_present()
            return inscription
        except InscriptionEvenement.DoesNotExist:
            return None

    @classmethod
    def _promouvoir_liste_attente(cls, evenement: Evenement):
        """Promouvoir le premier de la liste d'attente si place disponible."""
        if evenement.capacite_max <= 0:
            return

        if evenement.nombre_inscrits >= evenement.capacite_max:
            return

        premier_liste = (
            InscriptionEvenement.objects
            .filter(evenement=evenement, statut=StatutInscription.LISTE_ATTENTE)
            .order_by("date_inscription")
            .first()
        )

        if premier_liste:
            premier_liste.statut = StatutInscription.INSCRIT
            premier_liste.save(update_fields=["statut", "updated_at"])
            Evenement.objects.filter(pk=evenement.pk).update(nombre_inscrits=F("nombre_inscrits") + 1)

            logger.info(
                f"Promotion liste attente: {premier_liste.utilisateur.email} "
                f"→ {evenement.titre}"
            )

    @classmethod
    def _creer_entree_agenda(cls, utilisateur, evenement, inscription):
        """Crée une entrée dans l'agenda personnel de l'utilisateur."""
        try:
            from apps.dashboard.models import EvenementAgenda, TypeEvenementAgenda
            from apps.dashboard.services import AgendaService

            type_mapping = {
                "JPO": TypeEvenementAgenda.JPO,
                "SALON": TypeEvenementAgenda.SALON,
                "CONFERENCE": TypeEvenementAgenda.SALON,
                "WEBINAIRE": TypeEvenementAgenda.WEBINAIRE,
                "CONCOURS": TypeEvenementAgenda.CONCOURS,
                "PRESELECTION": TypeEvenementAgenda.CONCOURS,
                "SEANCE_INFO": TypeEvenementAgenda.JPO,
                "ATELIER": TypeEvenementAgenda.SALON,
                "ORIENTATION": TypeEvenementAgenda.SALON,
                "RENCONTRE": TypeEvenementAgenda.SALON,
                "VISITE": TypeEvenementAgenda.PERSONNEL,
            }

            type_agenda = type_mapping.get(evenement.type, TypeEvenementAgenda.PERSONNEL)

            evt_agenda = EvenementAgenda.objects.create(
                utilisateur=utilisateur,
                evenement_public=evenement,
                type=type_agenda,
                titre=evenement.titre,
                description=evenement.description_courte,
                lieu=evenement.lieu_nom or evenement.adresse,
                date_debut=evenement.date_debut,
                date_fin=evenement.date_fin,
                rappel_j_7=evenement.envoi_rappel_j7,
                rappel_j_1=evenement.envoi_rappel_j1,
                rappel_j_0=evenement.envoi_rappel_j0,
                couleur="#3B82F6",
            )

            AgendaService.creer_rappels_pour_evenement(evt_agenda)

        except Exception as e:
            logger.warning(f"Erreur création entrée agenda: {e}")

    @classmethod
    def _supprimer_entree_agenda(cls, utilisateur, evenement):
        """Supprime l'entrée d'agenda associée."""
        try:
            from apps.dashboard.models import EvenementAgenda
            EvenementAgenda.objects.filter(
                utilisateur=utilisateur,
                evenement_public=evenement,
            ).delete()
        except Exception as e:
            logger.warning(f"Erreur suppression entrée agenda: {e}")

    @classmethod
    def incrementer_vues(cls, evenement: Evenement):
        """Incrémente le compteur de vues d'un événement."""
        Evenement.objects.filter(pk=evenement.pk).update(
            nombre_vues=F("nombre_vues") + 1
        )

    @classmethod
    def get_stats_evenement(cls, evenement: Evenement) -> dict:
        """Statistiques détaillées d'un événement."""
        inscriptions = InscriptionEvenement.objects.filter(evenement=evenement)

        return {
            "nombre_inscrits": evenement.nombre_inscrits,
            "nombre_confirmees": inscriptions.filter(statut="CONFIRME").count(),
            "nombre_liste_attente": inscriptions.filter(statut="LISTE_ATTENTE").count(),
            "nombre_presents": evenement.nombre_presents,
            "nombre_annulees": inscriptions.filter(statut="ANNULE").count(),
            "taux_remplissage": evenement.taux_remplissage,
            "places_restantes": evenement.places_restantes,
        }
