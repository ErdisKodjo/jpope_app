"""
Modèle EvaluationConseiller — fiche d'orientation soumise par un conseiller.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class StatutEvaluation(models.TextChoices):
    BROUILLON          = "BROUILLON", _("Brouillon")
    SOUMISE            = "SOUMISE",   _("Soumise à l'admin")
    VALIDEE            = "VALIDEE",   _("Validée")
    REVISION_DEMANDEE  = "REVISION",  _("Révision demandée")
    ARCHIVEE           = "ARCHIVEE",  _("Archivée")


class EvaluationConseiller(models.Model):
    """
    Fiche d'évaluation d'orientation rédigée par un conseiller pour un étudiant.
    Workflow : BROUILLON → SOUMISE → VALIDEE (ou REVISION → SOUMISE → …)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Acteurs
    conseiller = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="evaluations_conseiller",
        limit_choices_to={"role": "COUNSELOR"},
        verbose_name=_("conseiller"),
    )
    etudiant = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="evaluations_recues",
        limit_choices_to={"role": "STUDENT"},
        verbose_name=_("étudiant"),
    )

    # Contenu de la fiche
    bilan_scolaire = models.TextField(
        _("bilan scolaire"),
        help_text=_("Résumé du parcours académique de l'étudiant"),
    )
    points_forts = models.JSONField(
        _("points forts"),
        default=list,
        blank=True,
        help_text=_("Liste de points forts identifiés"),
    )
    points_attention = models.JSONField(
        _("points d'attention"),
        default=list,
        blank=True,
        help_text=_("Axes de progrès ou obstacles à surveiller"),
    )
    formations_suggerees = models.JSONField(
        _("formations suggérées"),
        default=list,
        blank=True,
        help_text=_("Noms de formations recommandées par le conseiller"),
    )

    # Workflow
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutEvaluation.choices,
        default=StatutEvaluation.BROUILLON,
        db_index=True,
    )
    note_admin = models.TextField(
        _("note de l'admin"),
        blank=True,
        help_text=_("Commentaire de l'admin (visible par le conseiller)"),
    )

    # Traçabilité
    date_soumission = models.DateTimeField(
        _("date de soumission"),
        null=True,
        blank=True,
    )
    date_traitement = models.DateTimeField(
        _("date de traitement"),
        null=True,
        blank=True,
    )
    traite_par = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluations_traitees",
        verbose_name=_("traitée par"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("évaluation conseiller")
        verbose_name_plural = _("évaluations conseillers")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["conseiller", "statut"]),
            models.Index(fields=["etudiant"]),
            models.Index(fields=["statut"]),
        ]

    def __str__(self):
        return (
            f"Éval. {self.get_statut_display()} — "
            f"{self.etudiant.get_full_name()} par {self.conseiller.get_full_name()}"
        )

    @property
    def est_editable(self) -> bool:
        return self.statut in (
            StatutEvaluation.BROUILLON,
            StatutEvaluation.REVISION_DEMANDEE,
        )

    @property
    def peut_etre_soumise(self) -> bool:
        return self.statut in (
            StatutEvaluation.BROUILLON,
            StatutEvaluation.REVISION_DEMANDEE,
        )
