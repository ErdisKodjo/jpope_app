"""
Modèle InscriptionEvenement — inscriptions des utilisateurs aux événements.
"""
import uuid
from django.db import models
from django.db.models import F
from django.db.functions import Greatest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .enums import StatutInscription
from .evenement import Evenement


class InscriptionEvenement(models.Model):
    """
    Inscription d'un utilisateur à un événement.
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
        related_name="inscriptions_evenements",
        verbose_name=_("utilisateur"),
    )
    evenement = models.ForeignKey(
        "events.Evenement",
        on_delete=models.CASCADE,
        related_name="inscriptions",
        verbose_name=_("événement"),
    )

    # Statut
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutInscription.choices,
        default=StatutInscription.INSCRIT,
    )

    # Informations d'inscription
    date_inscription = models.DateTimeField(
        _("date d'inscription"),
        auto_now_add=True,
    )
    date_confirmation = models.DateTimeField(
        _("date de confirmation"),
        blank=True,
        null=True,
    )
    date_annulation = models.DateTimeField(
        _("date d'annulation"),
        blank=True,
        null=True,
    )

    # Token de confirmation (pour email)
    token_confirmation = models.CharField(
        _("token de confirmation"),
        max_length=255,
        blank=True,
        null=True,
    )

    # Informations additionnelles
    nombre_accompagnants = models.PositiveIntegerField(
        _("nombre d'accompagnants"),
        default=0,
        help_text=_("Ex: parent qui vient avec l'étudiant"),
    )
    besoins_speciaux = models.TextField(
        _("besoins spéciaux / accessibilité"),
        blank=True,
        help_text=_("Ex: 'Besoin d'un interprète LSF', 'Accès PMR'"),
    )
    source_inscription = models.CharField(
        _("source de l'inscription"),
        max_length=50,
        blank=True,
        help_text=_("Ex: 'site_web', 'mobile_app', 'qr_code', 'recommandation'"),
    )

    # Participation (après l'événement)
    a_participe = models.BooleanField(
        _("a effectivement participé"),
        default=False,
    )
    date_checkin = models.DateTimeField(
        _("date de check-in"),
        blank=True,
        null=True,
    )
    feedback = models.TextField(
        _("retour d'expérience"),
        blank=True,
    )
    note_satisfaction = models.PositiveIntegerField(
        _("note de satisfaction (1-5)"),
        blank=True,
        null=True,
    )

    # QR Code pour check-in
    qr_code_token = models.CharField(
        _("token QR code"),
        max_length=255,
        blank=True,
        unique=True,
        null=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("inscription à un événement")
        verbose_name_plural = _("inscriptions aux événements")
        ordering = ["-date_inscription"]
        constraints = [
            models.UniqueConstraint(
                fields=["utilisateur", "evenement"],
                name="unique_inscription_evenement",
            ),
        ]
        indexes = [
            models.Index(fields=["utilisateur", "statut"]),
            models.Index(fields=["evenement", "statut"]),
            models.Index(fields=["-date_inscription"]),
        ]

    def __str__(self):
        return (
            f"{self.utilisateur.get_full_name()} → "
            f"{self.evenement.titre} ({self.get_statut_display()})"
        )

    def confirmer(self):
        """Confirme l'inscription."""
        self.statut = StatutInscription.CONFIRME
        self.date_confirmation = timezone.now()
        self.save(update_fields=["statut", "date_confirmation", "updated_at"])

    def annuler(self):
        """Annule l'inscription."""
        self.statut = StatutInscription.ANNULE
        self.date_annulation = timezone.now()
        self.save(update_fields=["statut", "date_annulation", "updated_at"])

        # Mettre à jour le compteur de l'événement
        evenement = self.evenement
        Evenement.objects.filter(pk=evenement.pk).update(
            nombre_inscrits=Greatest(F("nombre_inscrits") - 1, 0)
        )

    def marquer_present(self):
        """Marque l'utilisateur comme présent (check-in)."""
        self.a_participe = True
        self.date_checkin = timezone.now()
        self.statut = StatutInscription.PRESENT
        self.save(update_fields=[
            "a_participe", "date_checkin", "statut", "updated_at"
        ])

        # Mettre à jour le compteur de présents
        Evenement.objects.filter(pk=self.evenement.pk).update(
            nombre_presents=F("nombre_presents") + 1
        )
