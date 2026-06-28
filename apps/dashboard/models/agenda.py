"""
Modèles EvenementAgenda et Rappel — gestion du temps.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import TypeEvenementAgenda, StatutRappel, CanalNotification

class EvenementAgenda(models.Model):
    """
    Événement dans l'agenda personnel de l'étudiant.
    Peut être lié à une formation, un voeu, ou être personnel.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Liens
    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="evenements_agenda",
        verbose_name=_("utilisateur"),
    )
    voeu = models.ForeignKey(
        "dashboard.Voeu",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="evenements_agenda",
        verbose_name=_("voeu associé"),
    )
    formation = models.ForeignKey(
        "catalog.Formation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="evenements_agenda",
        verbose_name=_("formation associée"),
    )
    evenement_public = models.ForeignKey(
        "events.Evenement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entrees_agenda",
        verbose_name=_("événement public associé"),
    )

    # Caractéristiques
    type = models.CharField(
        _("type d'événement"),
        max_length=20,
        choices=TypeEvenementAgenda.choices,
        default=TypeEvenementAgenda.PERSONNEL,
    )
    titre = models.CharField(_("titre"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    lieu = models.CharField(_("lieu"), max_length=255, blank=True)

    # Temporalité
    date_debut = models.DateTimeField(_("date et heure de début"))
    date_fin = models.DateTimeField(
        _("date et heure de fin"),
        blank=True,
        null=True,
    )
    toute_la_journee = models.BooleanField(_("toute la journée"), default=False)

    # Rappels
    rappel_j_30 = models.BooleanField(_("rappel 30 jours avant"), default=False)
    rappel_j_7 = models.BooleanField(_("rappel 7 jours avant"), default=True)
    rappel_j_1 = models.BooleanField(_("rappel la veille"), default=True)
    rappel_j_0 = models.BooleanField(_("rappel le jour même"), default=False)

    # Statut
    est_termine = models.BooleanField(_("terminé"), default=False)
    est_annule = models.BooleanField(_("annulé"), default=False)
    couleur = models.CharField(
        _("couleur (hex)"),
        max_length=7,
        default="#3B82F6",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("événement d'agenda")
        verbose_name_plural = _("événements d'agenda")
        ordering = ["date_debut"]
        indexes = [
            models.Index(fields=["utilisateur", "date_debut"]),
            models.Index(fields=["date_debut", "date_fin"]),
        ]

    def __str__(self):
        return f"{self.titre} — {self.date_debut.strftime('%d/%m/%Y')}"

    @property
    def est_a_venir(self) -> bool:
        from django.utils import timezone
        return self.date_debut > timezone.now() and not self.est_annule

    @property
    def jours_avant(self) -> int | None:
        if not self.est_a_venir:
            return None
        from django.utils import timezone
        return (self.date_debut - timezone.now()).days

class Rappel(models.Model):
    """
    Rappel programmé pour un événement ou une démarche.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Liens
    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="rappels",
        verbose_name=_("utilisateur"),
    )
    evenement_agenda = models.ForeignKey(
        EvenementAgenda,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rappels",
        verbose_name=_("événement associé"),
    )
    demarche = models.ForeignKey(
        "dashboard.DemarcheInscription",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rappels",
        verbose_name=_("démarche associée"),
    )

    # Contenu
    titre = models.CharField(_("titre"), max_length=255)
    message = models.TextField(_("message"), blank=True)

    # Planification
    date_envoi_prevue = models.DateTimeField(
        _("date d'envoi prévue"),
        db_index=True,
    )
    date_envoi_effective = models.DateTimeField(
        _("date d'envoi effective"),
        blank=True,
        null=True,
    )

    # Canal
    canal = models.CharField(
        _("canal de notification"),
        max_length=20,
        choices=CanalNotification.choices,
        default=CanalNotification.IN_APP,
    )

    # Statut
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutRappel.choices,
        default=StatutRappel.ACTIF,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("rappel")
        verbose_name_plural = _("rappels")
        ordering = ["date_envoi_prevue"]
        indexes = [
            models.Index(fields=["statut", "date_envoi_prevue"]),
        ]

    def __str__(self):
        return f"Rappel : {self.titre} ({self.date_envoi_prevue})"
