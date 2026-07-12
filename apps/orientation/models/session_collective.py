"""
Modèle SessionCollective — sessions groupe conseiller ↔ étudiants + parents.

Cahier des charges (section 2.3 — Conseiller, Espace Collaboratif et Mentorat) :
"Messagerie interne sécurisée, module de prise de rendez-vous (physique ou
visioconférence) et outils d'échange pour animer des sessions collectives
avec les étudiants et les parents."

Le modèle RendezVous existant est 1-to-1. SessionCollective permet à un conseiller
d'animer des sessions groupe (ateliers, info-collective, webinaires).
"""
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class FormatSession(models.TextChoices):
    PRESENTIEL = "PRESENTIEL", _("Présentiel")
    VISIO = "VISIO", _("Visioconférence")
    HYBRIDE = "HYBRIDE", _("Hybride (présentiel + visio)")


class StatutSession(models.TextChoices):
    PROGRAMMEE = "PROGRAMMEE", _("Programmée")
    EN_COURS = "EN_COURS", _("En cours")
    TERMINEE = "TERMINEE", _("Terminée")
    ANNULEE = "ANNULEE", _("Annulée")
    REPORTABLE = "REPORTABLE", _("À reporter")


class TypeSession(models.TextChoices):
    ATELIER_ORIENTATION = "ATELIER_ORIENTATION", _("Atelier d'orientation")
    INFO_COLLECTIVE = "INFO_COLLECTIVE", _("Info collective école/filière")
    WEBINAIRE_METIER = "WEBINAIRE_METIER", _("Webinaire métier")
    SOUTIEN_PARENTS = "SOUTIEN_PARENTS", _("Session soutien parents")
    PREP_CONCOURS = "PREP_CONCOURS", _("Préparation concours")
    COACHING_GROUPE = "COACHING_GROUPE", _("Coaching de groupe")


class SessionCollective(models.Model):
    """
    Session collective animée par un conseiller.
    Étudiants + (optionnel) parents peuvent s'inscrire.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(_("titre"), max_length=255)
    description = models.TextField(_("description"))
    type = models.CharField(
        _("type de session"),
        max_length=30,
        choices=TypeSession.choices,
        default=TypeSession.ATELIER_ORIENTATION,
    )

    #Animateur
    conseiller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions_animees",
        verbose_name=_("conseiller animateur"),
    )

    # Format
    format = models.CharField(
        _("format"),
        max_length=15,
        choices=FormatSession.choices,
        default=FormatSession.VISIO,
    )
    lieu = models.CharField(
        _("lieu (présentiel)"),
        max_length=255,
        blank=True,
        help_text=_("Adresse physique si présentiel/hybride"),
    )
    lien_visio = models.URLField(
        _("lien visio"),
        blank=True,
        help_text=_("Lien Google Meet, Zoom, Jitsi, etc."),
    )

    # Dates
    date_debut = models.DateTimeField(_("date de début"), db_index=True)
    date_fin = models.DateTimeField(_("date de fin"))
    is_recurrent = models.BooleanField(_("récurrente"), default=False)
    frequence_recurrence = models.CharField(
        _("fréquence récurrence"),
        max_length=20,
        blank=True,
        help_text=_("Ex: 'HEBDOMADAIRE', 'MENSUELLE'"),
    )

    # Capacité
    capacite_max = models.PositiveIntegerField(
        _("capacité maximale"),
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(500)],
    )
    inscription_obligatoire = models.BooleanField(
        _("inscription obligatoire"),
        default=True,
    )
    public_cible = models.CharField(
        _("public cible"),
        max_length=255,
        default="Tous",
        help_text=_("Ex: 'Terminales D', 'Parents de 3e', 'Étudiants L1'"),
    )

    # Statut
    statut = models.CharField(
        _("statut"),
        max_length=15,
        choices=StatutSession.choices,
        default=StatutSession.PROGRAMMEE,
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("session collective")
        verbose_name_plural = _("sessions collectives")
        ordering = ["-date_debut"]
        indexes = [
            models.Index(fields=["conseiller", "statut"]),
            models.Index(fields=["date_debut"]),
            models.Index(fields=["type", "statut"]),
        ]

    def __str__(self):
        return f"{self.titre} — {self.date_debut:%d/%m/%Y %H:%M}"

    @property
    def is_future(self) -> bool:
        from django.utils import timezone
        return self.date_debut > timezone.now()

    @property
    def is_complet(self) -> bool:
        return self.inscriptions.count() >= self.capacite_max


class InscriptionSession(models.Model):
    """Inscription d'un utilisateur (étudiant ou parent) à une session collective."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        SessionCollective,
        on_delete=models.CASCADE,
        related_name="inscriptions",
        verbose_name=_("session"),
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions_inscrites",
        verbose_name=_("participant"),
    )
    date_inscription = models.DateTimeField(auto_now_add=True)
    is_present = models.BooleanField(
        _("présent"),
        default=False,
        help_text=_("Marqué présent après la session"),
    )
    note_retour = models.TextField(
        _("note de retour"),
        blank=True,
        help_text=_("Retour du participant après la session"),
    )

    class Meta:
        verbose_name = _("inscription à session")
        verbose_name_plural = _("inscriptions à sessions")
        unique_together = ("session", "participant")
        ordering = ["-date_inscription"]
