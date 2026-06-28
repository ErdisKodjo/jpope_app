"""
Modèles pour l'application ranking.
Gère les classements des établissements et formations.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Classement(models.Model):
    """
    Classement d'un établissement pour une année donnée.
    Agrège les scores et rangs (national, régional) selon une méthodologie définie.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Lien vers l'établissement
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.CASCADE,
        related_name="classements",
        verbose_name=_("établissement"),
    )

    # Période
    annee = models.PositiveIntegerField(
        _("année"),
        validators=[MinValueValidator(2000)],
        help_text=_("Année de référence du classement"),
    )

    # Rangs
    rang_national = models.PositiveIntegerField(
        _("rang national"),
        null=True,
        blank=True,
        help_text=_("Position dans le classement national"),
    )
    rang_regional = models.PositiveIntegerField(
        _("rang régional"),
        null=True,
        blank=True,
        help_text=_("Position dans le classement régional (ex: Afrique de l'Ouest)"),
    )

    # Score final
    score_final = models.FloatField(
        _("score final"),
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Score composite sur 100"),
    )

    # Détails des scores par critère
    details_scores = models.JSONField(
        _("détails des scores"),
        default=dict,
        blank=True,
        help_text=_(
            "Ex: {'qualite_enseignement': 85, 'insertion_professionnelle': 78, "
            "'recherche': 60, 'reputation': 72}"
        ),
    )

    # Méthodologie utilisée
    methodology = models.TextField(
        _("méthodologie"),
        blank=True,
        help_text=_(
            "Description de la méthode de calcul et des critères utilisés"
        ),
    )

    # Publication
    is_published = models.BooleanField(
        _("publié"),
        default=False,
        help_text=_("Rendre ce classement visible publiquement"),
    )

    # Timestamps
    created_at = models.DateTimeField(
        _("créé le"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("mis à jour le"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("classement")
        verbose_name_plural = _("classements")
        ordering = ["annee", "rang_national"]
        constraints = [
            models.UniqueConstraint(
                fields=["etablissement", "annee"],
                name="unique_classement_etablissement_annee",
            )
        ]
        indexes = [
            models.Index(fields=["annee", "rang_national"]),
            models.Index(fields=["is_published"]),
        ]

    def __str__(self):
        return (
            f"{self.etablissement} — {self.annee} "
            f"(rang national: {self.rang_national or 'N/A'})"
        )

    @property
    def score_formate(self) -> str:
        return f"{self.score_final:.1f}/100"

    @property
    def est_top_10(self) -> bool:
        return self.rang_national is not None and self.rang_national <= 10

    @property
    def criteres_principaux(self) -> list:
        """Retourne les critères triés par score décroissant."""
        if not self.details_scores:
            return []
        return sorted(
            self.details_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
