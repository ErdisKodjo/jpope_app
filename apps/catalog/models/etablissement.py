"""
Modèle Établissement d'enseignement supérieur.
"""
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .enums import TypeEtablissement, StatutEtablissement
from ..managers import EtablissementManager


class Etablissement(models.Model):
    """
    Établissement d'enseignement supérieur (université, école, institut).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    nom = models.CharField(_("nom"), max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sigle = models.CharField(
        _("sigle/acronyme"),
        max_length=20,
        blank=True,
        help_text=_("Ex: UL, ESGIS, ESIS"),
    )
    description = models.TextField(_("description"), blank=True)
    description_courte = models.CharField(
        _("description courte"),
        max_length=500,
        blank=True,
    )
    logo = models.ImageField(
        _("logo"),
        upload_to="etablissements/logos/%Y/",
        blank=True,
        null=True,
    )
    banniere = models.ImageField(
        _("image de bannière"),
        upload_to="etablissements/bannieres/%Y/",
        blank=True,
        null=True,
    )

    # TYPE ET STATUT
    type = models.CharField(
        _("type d'établissement"),
        max_length=30,
        choices=TypeEtablissement.choices,
        default=TypeEtablissement.PRIVE_LAIC,
    )
    statut = models.CharField(
        _("statut officiel"),
        max_length=30,
        choices=StatutEtablissement.choices,
        default=StatutEtablissement.AGREÉ,
    )
    date_creation = models.PositiveIntegerField(
        _("année de création"),
        blank=True,
        null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2030)],
    )

    # LOCALISATION
    adresse = models.CharField(_("adresse"), max_length=255, blank=True)
    ville = models.CharField(_("ville"), max_length=100, db_index=True)
    pays = models.CharField(_("pays"), max_length=100, default="Togo")
    code_postal = models.CharField(_("code postal"), max_length=20, blank=True)
    latitude = models.DecimalField(
        _("latitude"),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    longitude = models.DecimalField(
        _("longitude"),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    # CONTACT
    site_web = models.URLField(_("site web"), blank=True)
    email = models.EmailField(_("email de contact"), blank=True)
    telephone = models.CharField(_("téléphone"), max_length=30, blank=True)
    facebook = models.URLField(_("page Facebook"), blank=True)
    linkedin = models.URLField(_("page LinkedIn"), blank=True)

    # DONNÉES ÉCONOMIQUES (FCFA)
    frais_inscription_min = models.DecimalField(
        _("frais d'inscription minimum (FCFA)"),
        max_digits=12,
        decimal_places=0,
        default=0,
    )
    frais_inscription_max = models.DecimalField(
        _("frais d'inscription maximum (FCFA)"),
        max_digits=12,
        decimal_places=0,
        default=0,
    )
    frais_scolarite_annuel_min = models.DecimalField(
        _("scolarité annuelle minimum (FCFA)"),
        max_digits=12,
        decimal_places=0,
        default=0,
    )
    frais_scolarite_annuel_max = models.DecimalField(
        _("scolarité annuelle maximum (FCFA)"),
        max_digits=12,
        decimal_places=0,
        default=0,
    )

    # INDICATEURS DE PERFORMANCE
    nombre_etudiants = models.PositiveIntegerField(
        _("nombre d'étudiants"),
        default=0,
    )
    nombre_enseignants = models.PositiveIntegerField(
        _("nombre d'enseignants"),
        default=0,
    )
    taux_encadrement = models.FloatField(
        _("ratio étudiants/enseignant"),
        default=0,
        help_text=_("Ex: 25 = 25 étudiants pour 1 enseignant"),
    )
    taux_reussite = models.FloatField(
        _("taux de réussite aux examens (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    taux_insertion_professionnelle = models.FloatField(
        _("taux d'insertion professionnelle à 6 mois (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )

    # CLASSEMENT ET NOTES
    note_globale = models.DecimalField(
        _("note globale (0-5)"),
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    nombre_avis = models.PositiveIntegerField(default=0)
    classement_national = models.PositiveIntegerField(
        _("rang classement national"),
        blank=True,
        null=True,
    )
    classement_regional = models.PositiveIntegerField(
        _("rang classement régional"),
        blank=True,
        null=True,
    )
    score_qualite_global = models.FloatField(
        _("score qualité global (0-100)"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    # ÉQUIPEMENTS & LABELS
    equipements = models.JSONField(
        _("équipements"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Bibliothèque', 'Laboratoires', 'Wifi', 'Restaurant']"),
    )
    labels_qualite = models.JSONField(
        _("labels qualité"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Accrédité CAMES', 'ISO 9001', 'Membre AUF']"),
    )
    domaines_enseignes = models.ManyToManyField(
        "catalog.Domaine",
        blank=True,
        related_name="etablissements",
        verbose_name=_("domaines enseignés"),
    )

    # BOURSES ET AIDES
    propose_bourses = models.BooleanField(
        _("propose des bourses"),
        default=False,
    )
    montant_bourse_max = models.DecimalField(
        _("montant max bourse (FCFA)"),
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
    )
    criteres_bourses = models.JSONField(
        _("critères d'attribution bourses"),
        default=list,
        blank=True,
    )

    # VIE ÉTUDIANTE
    residences_universitaires = models.BooleanField(
        _("dispose de résidences universitaires"),
        default=False,
    )
    clubs_et_associations = models.JSONField(
        _("clubs et associations"),
        default=list,
        blank=True,
    )
    sports_proposes = models.JSONField(
        _("sports proposés"),
        default=list,
        blank=True,
    )

    # STATUT
    is_active = models.BooleanField(_("actif"), default=True)
    is_verified = models.BooleanField(
        _("vérifié par l'équipe"),
        default=False,
        help_text=_("Fiche vérifiée et validée par l'équipe AvenSU"),
    )
    is_featured = models.BooleanField(
        _("mis en avant"),
        default=False,
    )
    date_verification = models.DateTimeField(
        _("date de dernière vérification"),
        blank=True,
        null=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EtablissementManager()

    class Meta:
        verbose_name = _("établissement")
        verbose_name_plural = _("établissements")
        ordering = ["-score_qualite_global", "nom"]
        indexes = [
            models.Index(fields=["ville"]),
            models.Index(fields=["type"]),
            models.Index(fields=["-note_globale"]),
            models.Index(fields=["-score_qualite_global"]),
            models.Index(fields=["classement_national"]),
        ]

    def __str__(self):
        if self.sigle:
            return f"{self.sigle} — {self.nom}"
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            counter = 1
            while Etablissement.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def ratio_enseignant_formate(self) -> str:
        if self.taux_encadrement > 0:
            return f"1 enseignant pour {int(self.taux_encadrement)} étudiants"
        return "Non renseigné"

    @property
    def fourchette_frais(self) -> str:
        """Fourchette des frais annuels formatée."""
        if self.frais_scolarite_annuel_min == self.frais_scolarite_annuel_max:
            return f"{int(self.frais_scolarite_annuel_min):,} FCFA".replace(",", " ")
        return (
            f"{int(self.frais_scolarite_annuel_min):,} - "
            f"{int(self.frais_scolarite_annuel_max):,} FCFA"
        ).replace(",", " ")

    @property
    def est_abordable(self) -> bool:
        """Indique si l'établissement est considéré comme abordable."""
        return self.frais_scolarite_annuel_max <= 500_000  # 500 000 FCFA max
