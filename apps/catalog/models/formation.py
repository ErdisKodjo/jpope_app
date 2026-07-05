"""
Modèle Formation (programme d'études).
"""
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .enums import NiveauFormation, ImportanceStrategique, ModaliteFormation
from .domaine import Domaine
from .etablissement import Etablissement
from .metier import Metier
from ..managers import FormationManager


class Formation(models.Model):
    """
    Formation / programme d'études proposé par un établissement.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    nom = models.CharField(_("nom de la formation"), max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField(_("description détaillée"), blank=True)
    description_courte = models.CharField(
        _("description courte"),
        max_length=400,
        blank=True,
    )

    # LIENS
    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.CASCADE,
        related_name="formations",
        verbose_name=_("établissement"),
    )
    domaine = models.ForeignKey(
        Domaine,
        on_delete=models.PROTECT,
        related_name="formations",
        verbose_name=_("domaine"),
    )
    debouches = models.ManyToManyField(
        Metier,
        blank=True,
        related_name="formations_acces",
        verbose_name=_("débouchés métiers"),
    )

    # CARACTÉRISTIQUES
    niveau = models.CharField(
        _("niveau"),
        max_length=20,
        choices=NiveauFormation.choices,
        default=NiveauFormation.LICENCE,
    )
    duree_annees = models.PositiveIntegerField(
        _("durée (années)"),
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    modalite = models.CharField(
        _("modalité"),
        max_length=20,
        choices=ModaliteFormation.choices,
        default=ModaliteFormation.PRESENTIEL,
    )

    # COÛT (FCFA)
    cout_annuel = models.DecimalField(
        _("coût annuel (FCFA)"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        help_text=_("Frais de scolarité annuels"),
    )
    frais_inscription = models.DecimalField(
        _("frais d'inscription (FCFA)"),
        max_digits=12,
        decimal_places=0,
        default=0,
    )
    frais_dossier = models.DecimalField(
        _("frais de dossier (FCFA)"),
        max_digits=12,
        decimal_places=0,
        default=0,
    )

    # AIDES FINANCIÈRES
    bourses_disponibles = models.BooleanField(
        _("bourses disponibles"),
        default=False,
    )
    montant_bourse_max = models.DecimalField(
        _("montant max bourse (FCFA)"),
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
    )
    facilites_paiement = models.BooleanField(
        _("facilités de paiement"),
        default=False,
    )

    # IMPORTANCE STRATÉGIQUE
    importance_strategique = models.CharField(
        _("importance stratégique"),
        max_length=20,
        choices=ImportanceStrategique.choices,
        default=ImportanceStrategique.MOYENNE,
        help_text=_("Priorité nationale / demande marché"),
    )

    # INDICATEURS DE PERFORMANCE
    taux_reussite = models.FloatField(
        _("taux de réussite (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    taux_insertion_6mois = models.FloatField(
        _("taux d'insertion à 6 mois (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    taux_insertion_12mois = models.FloatField(
        _("taux d'insertion à 12 mois (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    salaire_sortie_moyen = models.DecimalField(
        _("salaire de sortie moyen (FCFA/mois)"),
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)],
    )

    # SCORE QUALITÉ (calculé)
    score_qualite = models.FloatField(
        _("score qualité (0-100)"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    # PRÉREQUIS & PROGRAMME
    prerequis = models.JSONField(
        _("prérequis"),
        default=list,
        blank=True,
        help_text=_("Ex: ['BAC C/D', 'Mention Assez Bien minimum']"),
    )
    serie_bac_admises = models.JSONField(
        _("séries de bac admises"),
        default=list,
        blank=True,
        help_text=_("Ex: ['C', 'D', 'G2']"),
    )
    programmes = models.JSONField(
        _("programmes / matières principales"),
        default=list,
        blank=True,
    )

    # DATES
    dates_rentree = models.JSONField(
        _("dates de rentrée"),
        default=list,
        blank=True,
        help_text=_("Ex: ['2026-10-01', '2027-02-01']"),
    )
    date_limite_inscription = models.DateField(
        _("date limite d'inscription"),
        blank=True,
        null=True,
    )

    # CAPACITÉ
    places_disponibles = models.PositiveIntegerField(
        _("nombre de places"),
        default=0,
    )
    nombre_inscrits_annee = models.PositiveIntegerField(
        _("nombre d'inscrits dernière année"),
        default=0,
    )

    # STATUT
    is_active = models.BooleanField(_("active"), default=True)
    is_featured = models.BooleanField(_("mise en avant"), default=False)
    is_sur_liste_guide = models.BooleanField(
        _("sur liste guide (formation reconnue)"),
        default=False,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FormationManager()

    class Meta:
        verbose_name = _("formation")
        verbose_name_plural = _("formations")
        ordering = ["-score_qualite", "nom"]
        indexes = [
            models.Index(fields=["etablissement"]),
            models.Index(fields=["domaine"]),
            models.Index(fields=["niveau"]),
            models.Index(fields=["-score_qualite"]),
            models.Index(fields=["importance_strategique"]),
            models.Index(fields=["cout_annuel"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["nom", "etablissement", "niveau"],
                name="unique_formation_etablissement_niveau",
            )
        ]

    def __str__(self):
        return f"{self.nom} ({self.etablissement.sigle or self.etablissement.nom})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.nom}-{self.etablissement.sigle or 'form'}")
            slug = base_slug
            counter = 1
            while Formation.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Calcul automatique du score qualité
        self.score_qualite = self._calculer_score_qualite()
        super().save(*args, **kwargs)

    def _calculer_score_qualite(self) -> float:
        """
        Score qualité basé sur :
        - Taux de réussite : 25%
        - Taux d'insertion 12 mois : 30%
        - Coût (inverse) : 20%
        - Importance stratégique : 15%
        - Salaire de sortie : 10%
        """
        # Taux de réussite (0-100)
        score_reussite = float(self.taux_reussite)

        # Taux d'insertion (0-100)
        score_insertion = float(self.taux_insertion_12mois)

        # Coût (inverse — moins cher = meilleur)
        # Max attendu : 3 000 000 FCFA/an
        if self.cout_annuel > 0:
            score_cout = max(0, 100 - (float(self.cout_annuel) / 3_000_000 * 100))
        else:
            score_cout = 100

        # Importance stratégique
        importance_scores = {
            ImportanceStrategique.CRITIQUE: 100,
            ImportanceStrategique.ELEVEE: 80,
            ImportanceStrategique.MOYENNE: 50,
            ImportanceStrategique.FAIBLE: 20,
        }
        score_importance = importance_scores.get(self.importance_strategique, 50)

        # Salaire de sortie (normalisé sur max 1 500 000 FCFA)
        score_salaire = min(float(self.salaire_sortie_moyen) / 1_500_000 * 100, 100)

        # Score final pondéré
        return round(
            score_reussite * 0.25 +
            score_insertion * 0.30 +
            score_cout * 0.20 +
            score_importance * 0.15 +
            score_salaire * 0.10,
            1
        )

    @property
    def cout_total(self) -> int:
        """Coût total de la formation (frais + scolarité × durée)."""
        return int(
            self.frais_inscription +
            self.frais_dossier +
            (self.cout_annuel * self.duree_annees)
        )

    @property
    def cout_total_formate(self) -> str:
        return f"{self.cout_total:,} FCFA".replace(",", " ")

    @property
    def est_bourse_eligible(self) -> bool:
        return self.bourses_disponibles and self.montant_bourse_max and self.montant_bourse_max > 0

    @property
    def retour_sur_investissement_annees(self) -> float | None:
        """
        Estimation du nombre d'années pour rentabiliser la formation
        en supposant un salaire de sortie constant.
        """
        if self.salaire_sortie_moyen <= 0:
            return None
        # En supposant 50% d'épargne du salaire
        epargne_annuelle = float(self.salaire_sortie_moyen) * 12 * 0.5
        if epargne_annuelle <= 0:
            return None
        return round(self.cout_total / epargne_annuelle, 1)
