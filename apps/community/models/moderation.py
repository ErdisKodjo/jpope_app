"""
Modèles Signalement et BlocageUtilisateur — modération de la communauté.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import TypeSignalement, StatutSignalement, NiveauBlocage


class Signalement(models.Model):
    """
    Signalement d'un contenu ou d'un utilisateur pour modération.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    auteur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="signalements_envoyes",
        verbose_name=_("auteur du signalement"),
    )

    type_contenu = models.CharField(
        _("type de contenu signalé"),
        max_length=30,
        choices=[
            ("MESSAGE_FORUM", "Message de forum"),
            ("THREAD", "Discussion"),
            ("MESSAGE_PRIVE", "Message privé"),
            ("UTILISATEUR", "Utilisateur"),
            ("MENTOR", "Profil mentor"),
        ],
    )
    contenu_id = models.UUIDField(
        _("ID du contenu signalé"),
    )
    contenu_resume = models.TextField(
        _("résumé du contenu signalé"),
        blank=True,
        help_text=_("Extrait du contenu pour référence rapide"),
    )

    type = models.CharField(
        _("type de signalement"),
        max_length=20,
        choices=TypeSignalement.choices,
        default=TypeSignalement.AUTRE,
    )
    description = models.TextField(
        _("description du signalement"),
        blank=True,
        help_text=_("Explication supplémentaire du signalement"),
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutSignalement.choices,
        default=StatutSignalement.EN_ATTENTE,
    )

    traite_par = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signalements_traites",
        verbose_name=_("traité par"),
    )
    date_traitement = models.DateTimeField(
        _("date de traitement"),
        blank=True,
        null=True,
    )
    decision = models.TextField(
        _("décision prise"),
        blank=True,
    )
    action_prise = models.CharField(
        _("action prise"),
        max_length=50,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("signalement")
        verbose_name_plural = _("signalements")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["statut", "created_at"]),
            models.Index(fields=["type_contenu", "contenu_id"]),
        ]

    def __str__(self):
        return f"Signalement {self.type} — {self.auteur} ({self.get_statut_display()})"


class BlocageUtilisateur(models.Model):
    """
    Blocage d'un utilisateur par un autre.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    bloqueur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="blocages_effectues",
        verbose_name=_("utilisateur qui bloque"),
    )
    bloque = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="blocages_subis",
        verbose_name=_("utilisateur bloqué"),
    )

    niveau = models.CharField(
        _("niveau de blocage"),
        max_length=20,
        choices=NiveauBlocage.choices,
        default=NiveauBlocage.BLOQUER_CONTACT,
    )

    motif = models.TextField(_("motif du blocage"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("blocage utilisateur")
        verbose_name_plural = _("blocages utilisateurs")
        constraints = [
            models.UniqueConstraint(
                fields=["bloqueur", "bloque"],
                name="unique_blocage_utilisateur",
            )
        ]

    def __str__(self):
        return f"{self.bloqueur} bloque {self.bloque} ({self.get_niveau_display()})"
