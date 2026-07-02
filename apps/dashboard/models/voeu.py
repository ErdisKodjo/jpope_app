"""
Modèle Voeu — candidatures / choix d'inscription de l'étudiant.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from .enums import StatutVoeu, PrioriteVoeu
from ..managers import VoeuManager

class Voeu(models.Model):
    """
    Voeu d'inscription à une formation.
    Un étudiant peut avoir plusieurs voeux classés par priorité.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Liens
    etudiant = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="voeux",
        verbose_name=_("étudiant"),
        limit_choices_to={"role": "STUDENT"},
    )
    formation = models.ForeignKey(
        "catalog.Formation",
        on_delete=models.CASCADE,
        related_name="voeux",
        verbose_name=_("formation visée"),
    )

    # Classement
    priorite = models.PositiveIntegerField(
        _("ordre de priorité"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text=_("1 = choix n°1, 2 = choix n°2, etc."),
    )
    niveau_priorite = models.CharField(
        _("niveau de priorité"),
        max_length=20,
        choices=PrioriteVoeu.choices,
        default=PrioriteVoeu.SOUHAITE,
    )

    # Statut
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutVoeu.choices,
        default=StatutVoeu.BROUILLON,
    )

    # Détails de la candidature
    date_soumission = models.DateTimeField(
        _("date de soumission"),
        blank=True,
        null=True,
    )
    date_reponse = models.DateTimeField(
        _("date de réponse"),
        blank=True,
        null=True,
    )
    numero_candidature = models.CharField(
        _("numéro de candidature"),
        max_length=100,
        blank=True,
    )
    lettre_motivation = models.TextField(
        _("lettre de motivation"),
        blank=True,
    )

    # Commentaires / retours
    commentaire_etablissement = models.TextField(
        _("commentaire de l'établissement"),
        blank=True,
    )
    motif_refus = models.TextField(
        _("motif de refus"),
        blank=True,
    )

    # Engagement
    est_principal = models.BooleanField(
        _("voeu principal (définitif)"),
        default=False,
        help_text=_("Le voeu choisi en dernier lieu pour inscription finale"),
    )

    # Suivi
    notes_etudiant = models.TextField(
        _("notes personnelles"),
        blank=True,
    )
    derniere_action = models.DateTimeField(
        _("dernière action"),
        blank=True,
        null=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VoeuManager()

    class Meta:
        verbose_name = _("voeu")
        verbose_name_plural = _("voeux")
        ordering = ["priorite", "-created_at"]
        constraints = [
            # Un étudiant ne peut pas postuler deux fois à la même formation
            models.UniqueConstraint(
                fields=["etudiant", "formation"],
                name="unique_voeu_par_formation",
            ),
        ]
        indexes = [
            models.Index(fields=["etudiant", "statut"]),
            models.Index(fields=["etudiant", "priorite"]),
        ]

    def __str__(self):
        return f"Voeu #{self.priorite} — {self.formation.nom} ({self.get_statut_display()})"

    @property
    def etablissement(self):
        return self.formation.etablissement

    @property
    def est_actif(self) -> bool:
        return self.statut not in [
            StatutVoeu.REFUSE,
            StatutVoeu.ABANDONNE,
            StatutVoeu.INSCRIT,
        ]

    @property
    def jours_depuis_soumission(self) -> int | None:
        if not self.date_soumission:
            return None
        from django.utils import timezone
        return (timezone.now() - self.date_soumission).days
