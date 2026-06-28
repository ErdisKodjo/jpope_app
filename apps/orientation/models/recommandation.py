"""
Modèle Recommandation personnalisée.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from .enums import PlanRecommandation, TypeEntiteRecommandee, NiveauConfiance

class Recommandation(models.Model):
    """
    Recommandation générée pour un étudiant suite à un test.
    Peut recommander une formation, un métier ou un établissement.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Liens
    resultat_test = models.ForeignKey(
        "orientation.ResultatTest",
        on_delete=models.CASCADE,
        related_name="recommandations",
        verbose_name=_("résultat de test"),
    )
    etudiant = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="recommandations",
        verbose_name=_("étudiant"),
    )

    # Entité recommandée (polymorphe)
    type_entite = models.CharField(
        _("type d'entité"),
        max_length=20,
        choices=TypeEntiteRecommandee.choices,
    )

    # Foreign keys optionnelles (une seule sera remplie)
    formation = models.ForeignKey(
        "catalog.Formation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recommandations",
        verbose_name=_("formation recommandée"),
    )
    metier = models.ForeignKey(
        "catalog.Metier",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recommandations",
        verbose_name=_("métier recommandé"),
    )
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recommandations",
        verbose_name=_("établissement recommandé"),
    )

    # Scoring de compatibilité
    taux_compatibilite = models.FloatField(
        _("taux de compatibilité (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Pourcentage de compatibilité entre le profil et l'entité"),
    )
    niveau_confiance = models.CharField(
        _("niveau de confiance"),
        max_length=20,
        choices=NiveauConfiance.choices,
        default=NiveauConfiance.MOYENNE,
    )

    # Classification
    plan = models.CharField(
        _("plan de recommandation"),
        max_length=20,
        choices=PlanRecommandation.choices,
        default=PlanRecommandation.ALTERNATIF,
    )
    ordre = models.PositiveIntegerField(
        _("ordre de priorité"),
        default=0,
    )

    # Justification (générée par IA ou règles)
    justification = models.TextField(
        _("justification"),
        blank=True,
        help_text=_("Pourquoi cette recommandation est pertinente pour ce profil"),
    )
    points_forts_match = models.JSONField(
        _("points forts du match"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Forte affinité analytique', 'Bon taux d\\'insertion']"),
    )
    points_attention = models.JSONField(
        _("points d'attention"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Coût élevé', 'Concours d\\'entrée sélectif']"),
    )

    # Engagement utilisateur
    a_ete_vue = models.BooleanField(_("vue par l'étudiant"), default=False)
    a_ete_favorisee = models.BooleanField(_("ajoutée aux favoris"), default=False)
    a_ete_cliquee = models.BooleanField(_("lien cliqué"), default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("recommandation")
        verbose_name_plural = _("recommandations")
        ordering = ["resultat_test", "plan", "ordre", "-taux_compatibilite"]
        indexes = [
            models.Index(fields=["etudiant", "-created_at"]),
            models.Index(fields=["type_entite"]),
            models.Index(fields=["plan"]),
            models.Index(fields=["-taux_compatibilite"]),
        ]

    def __str__(self):
        entite = self.formation or self.metier or self.etablissement
        return f"[{self.plan}] {entite} ({self.taux_compatibilite}%)"

    @property
    def entite(self):
        """Retourne l'entité recommandée."""
        return self.formation or self.metier or self.etablissement

    @property
    def entite_nom(self) -> str:
        entite = self.entite
        return str(entite) if entite else "N/A"

    def save(self, *args, **kwargs):
        # Calcul automatique du niveau de confiance
        if self.taux_compatibilite >= 85:
            self.niveau_confiance = NiveauConfiance.TRES_HAUTE
        elif self.taux_compatibilite >= 70:
            self.niveau_confiance = NiveauConfiance.HAUTE
        elif self.taux_compatibilite >= 50:
            self.niveau_confiance = NiveauConfiance.MOYENNE
        else:
            self.niveau_confiance = NiveauConfiance.FAIBLE
        super().save(*args, **kwargs)
