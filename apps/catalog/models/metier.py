"""
Modèle Métier avec données de revenus et perspectives.
"""
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .enums import NiveauEtudeRequis, DemandeMarche
from .domaine import Domaine
from ..managers import MetierManager


class Metier(models.Model):
    """
    Métier / profession avec données économiques.
    Les revenus sont exprimés en FCFA (mensuel brut).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    nom = models.CharField(_("nom du métier"), max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(_("description détaillée"), blank=True)
    description_courte = models.CharField(
        _("description courte"),
        max_length=300,
        blank=True,
    )

    # Lien vers le domaine
    domaine = models.ForeignKey(
        Domaine,
        on_delete=models.PROTECT,
        related_name="metiers",
        verbose_name=_("domaine"),
    )

    # DONNÉES ÉCONOMIQUES (FCFA mensuel brut)
    revenu_min = models.DecimalField(
        _("revenu minimum (FCFA/mois)"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        help_text=_("Salaire d'entrée, en FCFA brut mensuel"),
    )
    revenu_max = models.DecimalField(
        _("revenu maximum (FCFA/mois)"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        help_text=_("Salaire en fin de carrière, en FCFA brut mensuel"),
    )
    revenu_moyen = models.DecimalField(
        _("revenu moyen (FCFA/mois)"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        help_text=_("Salaire médian observé"),
    )

    # MARCHÉ DU TRAVAIL
    taux_emploi = models.FloatField(
        _("taux d'emploi à 6 mois (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text=_("Pourcentage de diplômés trouvant un emploi dans les 6 mois"),
    )
    demande_marche = models.CharField(
        _("demande sur le marché"),
        max_length=20,
        choices=DemandeMarche.choices,
        default=DemandeMarche.MOYENNE,
    )

    # FORMATION REQUISE
    niveau_etude_requis = models.CharField(
        _("niveau d'étude requis"),
        max_length=10,
        choices=NiveauEtudeRequis.choices,
        default=NiveauEtudeRequis.BAC_PLUS_3,
    )
    duree_formation_typique_annees = models.PositiveIntegerField(
        _("durée de formation typique (années)"),
        default=3,
    )

    # COMPÉTENCES & PERSPECTIVES
    competences_cles = models.JSONField(
        _("compétences clés"),
        default=list,
        blank=True,
        help_text=_("Liste des compétences principales"),
    )
    taches_principales = models.JSONField(
        _("tâches principales"),
        default=list,
        blank=True,
    )
    perspectives_evolution = models.TextField(
        _("perspectives d'évolution"),
        blank=True,
        help_text=_("Évolution de carrière possible"),
    )

    # CONTEXTE GÉOGRAPHIQUE
    pays_concernes = models.JSONField(
        _("pays concernés"),
        default=list,
        help_text=_("Ex: ['Togo', 'Bénin', 'Côte d'Ivoire']"),
    )
    villes_principales = models.JSONField(
        _("villes principales"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Lomé', 'Kara', 'Atakpamé']"),
    )

    # SCORE D'ATTRACTIVITÉ (calculé)
    score_attractivite = models.FloatField(
        _("score d'attractivité (0-100)"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Score calculé basé sur revenu, emploi, demande"),
    )

    # Métadonnées
    source_donnees = models.CharField(
        _("source des données"),
        max_length=200,
        blank=True,
        help_text=_("Ex: INS Togo 2025, Enquête emploi ANPE"),
    )
    date_mise_a_jour = models.DateField(
        _("date de dernière mise à jour"),
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MetierManager()

    class Meta:
        verbose_name = _("métier")
        verbose_name_plural = _("métiers")
        ordering = ["-score_attractivite", "nom"]
        indexes = [
            models.Index(fields=["domaine"]),
            models.Index(fields=["demande_marche"]),
            models.Index(fields=["-score_attractivite"]),
        ]

    def __str__(self):
        return f"{self.nom} ({self.domaine.nom})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        # Calcul automatique du score d'attractivité
        self.score_attractivite = self._calculer_score_attractivite()
        super().save(*args, **kwargs)

    def _calculer_score_attractivite(self) -> float:
        """
        Score d'attractivité basé sur :
        - Revenu moyen (normalisé) : 40%
        - Taux d'emploi : 35%
        - Demande marché : 25%
        """
        # Normalisation du revenu (échelle 0-100, max 2 000 000 FCFA)
        score_revenu = min(float(self.revenu_moyen) / 2_000_000 * 100, 100)

        # Taux d'emploi déjà sur 0-100
        score_emploi = float(self.taux_emploi)

        # Score demande marché
        demande_scores = {
            DemandeMarche.TRES_FORTE: 100,
            DemandeMarche.FORTE: 80,
            DemandeMarche.MOYENNE: 50,
            DemandeMarche.FAIBLE: 25,
            DemandeMarche.EN_DECLIN: 10,
        }
        score_demande = demande_scores.get(self.demande_marche, 50)

        # Score final pondéré
        return round(
            score_revenu * 0.40 +
            score_emploi * 0.35 +
            score_demande * 0.25,
            1
        )

    @property
    def revenu_moyen_formate(self) -> str:
        """Retourne le revenu moyen formaté (ex: '350 000 FCFA')."""
        return f"{int(self.revenu_moyen):,}".replace(",", " ") + " FCFA"

    @property
    def fourchette_revenu(self) -> str:
        """Retourne la fourchette formatée."""
        return f"{int(self.revenu_min):,} - {int(self.revenu_max):,} FCFA".replace(",", " ")
