"""
Modèle DemarcheInscription — suivi des démarches administratives.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import TypeDemarche, StatutDemarche

class DemarcheInscription(models.Model):
    """
    Démarche administrative liée à une inscription ou candidature.
    Permet à l'étudiant de suivre l'avancement de chaque étape.
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
        related_name="demarches",
        verbose_name=_("étudiant"),
    )
    voeu = models.ForeignKey(
        "dashboard.Voeu",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="demarches",
        verbose_name=_("voeu associé"),
    )
    formation = models.ForeignKey(
        "catalog.Formation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="demarches",
        verbose_name=_("formation concernée"),
    )

    # Caractéristiques
    type = models.CharField(
        _("type de démarche"),
        max_length=20,
        choices=TypeDemarche.choices,
        default=TypeDemarche.INSCRIPTION,
    )
    titre = models.CharField(
        _("titre"),
        max_length=255,
        help_text=_("Ex: 'Constituer le dossier d\\'inscription UL'"),
    )
    description = models.TextField(
        _("description / instructions"),
        blank=True,
    )

    # Statut & progression
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutDemarche.choices,
        default=StatutDemarche.A_FAIRE,
    )
    progression = models.PositiveIntegerField(
        _("progression (%)"),
        default=0,
    )

    # Échéances
    date_echeance = models.DateTimeField(
        _("date d'échéance"),
        blank=True,
        null=True,
        help_text=_("Date limite pour compléter cette démarche"),
    )
    date_realisation = models.DateTimeField(
        _("date de réalisation"),
        blank=True,
        null=True,
    )

    # Documents
    documents_requis = models.JSONField(
        _("documents requis"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Relevé de notes', 'Copie BAC', 'Photo d\\'identité']"),
    )
    documents_fournis = models.JSONField(
        _("documents fournis"),
        default=list,
        blank=True,
    )

    # Coûts
    cout_estime = models.DecimalField(
        _("coût estimé (FCFA)"),
        max_digits=10,
        decimal_places=0,
        default=0,
    )

    # Rappels
    rappel_actif = models.BooleanField(
        _("rappel actif"),
        default=True,
    )
    jours_avant_rappel = models.PositiveIntegerField(
        _("jours avant échéance pour rappel"),
        default=7,
        help_text=_("Rappel envoyé X jours avant l'échéance"),
    )

    # Notes
    notes_etudiant = models.TextField(
        _("notes personnelles"),
        blank=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("démarche d'inscription")
        verbose_name_plural = _("démarches d'inscription")
        ordering = ["date_echeance", "-created_at"]
        indexes = [
            models.Index(fields=["etudiant", "statut"]),
            models.Index(fields=["date_echeance"]),
        ]

    def __str__(self):
        return f"{self.titre} ({self.get_statut_display()})"

    @property
    def est_en_retard(self) -> bool:
        """Vérifie si la démarche est en retard."""
        if not self.date_echeance:
            return False
        from django.utils import timezone
        return (
            self.date_echeance < timezone.now()
            and self.statut not in [StatutDemarche.COMPLETEE, StatutDemarche.ANNULEE]
        )

    @property
    def jours_restants(self) -> int | None:
        """Nombre de jours restants avant échéance."""
        if not self.date_echeance:
            return None
        from django.utils import timezone
        delta = (self.date_echeance - timezone.now()).days
        return delta

    @property
    def documents_manquants(self) -> list:
        """Documents encore à fournir."""
        return [
            d for d in (self.documents_requis or [])
            if d not in (self.documents_fournis or [])
        ]
