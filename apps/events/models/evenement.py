"""
Modèle Evenement — événements publics d'orientation.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .enums import (
    TypeEvenement, FormatEvenement, StatutEvenement,
    CibleEvenement, PrioriteEvenement,
)


class Evenement(models.Model):
    """
    Événement public lié à l'orientation post-bac.
    Peut être organisé par un établissement ou par la plateforme elle-même.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Informations générales
    titre = models.CharField(
        _("titre"),
        max_length=255,
        help_text=_("Ex: 'Journée Portes Ouvertes ESGIS 2026'"),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )
    description = models.TextField(
        _("description détaillée"),
        blank=True,
    )
    description_courte = models.CharField(
        _("description courte"),
        max_length=300,
        blank=True,
        help_text=_("Résumé pour les listes et partages"),
    )

    # Visuels
    image_principale = models.ImageField(
        _("image principale"),
        upload_to="evenements/%Y/%m/",
        blank=True,
        null=True,
    )
    image_couverture = models.ImageField(
        _("image de couverture"),
        upload_to="evenements/couvertures/%Y/%m/",
        blank=True,
        null=True,
    )
    galerie_images = models.JSONField(
        _("galerie d'images (URLs)"),
        default=list,
        blank=True,
    )

    # Classification
    type = models.CharField(
        _("type d'événement"),
        max_length=20,
        choices=TypeEvenement.choices,
        default=TypeEvenement.JPO,
    )
    format = models.CharField(
        _("format"),
        max_length=20,
        choices=FormatEvenement.choices,
        default=FormatEvenement.PRESENTIEL,
    )
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutEvenement.choices,
        default=StatutEvenement.BROUILLON,
    )
    cible = models.CharField(
        _("public cible"),
        max_length=20,
        choices=CibleEvenement.choices,
        default=CibleEvenement.TOUS,
    )
    priorite = models.CharField(
        _("priorité"),
        max_length=20,
        choices=PrioriteEvenement.choices,
        default=PrioriteEvenement.NORMALE,
    )

    # Temporalité
    date_debut = models.DateTimeField(
        _("date et heure de début"),
        db_index=True,
    )
    date_fin = models.DateTimeField(
        _("date et heure de fin"),
        blank=True,
        null=True,
    )
    date_limite_inscription = models.DateTimeField(
        _("date limite d'inscription"),
        blank=True,
        null=True,
        help_text=_("Laisser vide pour inscription libre jusqu'au début"),
    )

    # Localisation
    lieu_nom = models.CharField(
        _("nom du lieu"),
        max_length=255,
        blank=True,
        help_text=_("Ex: 'Campus principal ESGIS'"),
    )
    adresse = models.CharField(
        _("adresse complète"),
        max_length=500,
        blank=True,
    )
    ville = models.CharField(
        _("ville"),
        max_length=100,
        blank=True,
        db_index=True,
    )
    pays = models.CharField(
        _("pays"),
        max_length=100,
        default="Togo",
    )
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

    # Événement en ligne
    lien_visio = models.URLField(
        _("lien visioconférence"),
        blank=True,
        help_text=_("Lien Zoom, Google Meet, Teams, etc."),
    )
    plateforme_visio = models.CharField(
        _("plateforme de visio"),
        max_length=50,
        blank=True,
        help_text=_("Ex: 'Zoom', 'Google Meet'"),
    )
    code_acces = models.CharField(
        _("code d'accès / mot de passe"),
        max_length=100,
        blank=True,
    )

    # Capacité et inscriptions
    capacite_max = models.PositiveIntegerField(
        _("capacité maximale"),
        default=0,
        help_text=_("0 = illimité"),
    )
    nombre_inscrits = models.PositiveIntegerField(
        _("nombre d'inscrits"),
        default=0,
    )
    nombre_presents = models.PositiveIntegerField(
        _("nombre de présents (après l'événement)"),
        default=0,
    )
    inscriptions_ouvertes = models.BooleanField(
        _("inscriptions ouvertes"),
        default=True,
    )
    inscription_obligatoire = models.BooleanField(
        _("inscription obligatoire"),
        default=True,
        help_text=_("Si False, l'événement est accessible sans inscription"),
    )

    # Coût
    est_gratuit = models.BooleanField(
        _("événement gratuit"),
        default=True,
    )
    cout_participation = models.DecimalField(
        _("coût de participation (FCFA)"),
        max_digits=10,
        decimal_places=0,
        default=0,
    )
    informations_tarifs = models.TextField(
        _("informations sur les tarifs"),
        blank=True,
    )

    # Organisateurs
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evenements",
        verbose_name=_("établissement organisateur"),
    )
    organisateur_externe = models.CharField(
        _("organisateur externe"),
        max_length=255,
        blank=True,
        help_text=_("Si l'organisateur n'est pas un établissement référencé"),
    )
    createur = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evenements_crees",
        verbose_name=_("créateur de l'événement"),
    )

    # Contenu additionnel
    programme = models.JSONField(
        _("programme / agenda de l'événement"),
        default=list,
        blank=True,
        help_text=_(
            "Liste d'activités : [{'heure': '09:00', 'titre': 'Accueil', 'description': '...'}]"
        ),
    )
    intervenants = models.JSONField(
        _("intervenants"),
        default=list,
        blank=True,
        help_text=_(
            "Liste : [{'nom': 'Dr. Mensah', 'fonction': 'Directeur', 'bio': '...'}]"
        ),
    )
    tags = models.JSONField(
        _("tags / mots-clés"),
        default=list,
        blank=True,
        help_text=_("Ex: ['informatique', 'bac+3', 'lomé']"),
    )
    domaines_concernes = models.ManyToManyField(
        "catalog.Domaine",
        blank=True,
        related_name="evenements",
        verbose_name=_("domaines concernés"),
    )

    # Contact
    email_contact = models.EmailField(
        _("email de contact"),
        blank=True,
    )
    telephone_contact = models.CharField(
        _("téléphone de contact"),
        max_length=30,
        blank=True,
    )
    site_web = models.URLField(
        _("site web de l'événement"),
        blank=True,
    )
    reseaux_sociaux = models.JSONField(
        _("liens réseaux sociaux"),
        default=dict,
        blank=True,
        help_text=_("Ex: {'facebook': 'https://...', 'instagram': '...'}"),
    )

    # Rappels automatiques
    envoi_rappel_j7 = models.BooleanField(
        _("rappel automatique J-7"),
        default=True,
    )
    envoi_rappel_j1 = models.BooleanField(
        _("rappel automatique J-1"),
        default=True,
    )
    envoi_rappel_j0 = models.BooleanField(
        _("rappel automatique le jour J"),
        default=False,
    )

    # Statistiques et métadonnées
    nombre_vues = models.PositiveIntegerField(
        _("nombre de vues de la fiche"),
        default=0,
    )
    nombre_partages = models.PositiveIntegerField(
        _("nombre de partages"),
        default=0,
    )
    is_featured = models.BooleanField(
        _("mis en avant"),
        default=False,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(
        _("date de publication"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("événement")
        verbose_name_plural = _("événements")
        ordering = ["-date_debut"]
        indexes = [
            models.Index(fields=["date_debut", "statut"]),
            models.Index(fields=["type", "statut"]),
            models.Index(fields=["ville"]),
            models.Index(fields=["-published_at"]),
            models.Index(fields=["etablissement"]),
        ]

    def __str__(self):
        return f"{self.titre} ({self.date_debut.strftime('%d/%m/%Y')})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            counter = 1
            while Evenement.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Mettre à jour le statut si l'événement est passé
        if (
            self.date_fin
            and self.date_fin < timezone.now()
            and self.statut not in [StatutEvenement.ANNULE, StatutEvenement.TERMINE]
        ):
            self.statut = StatutEvenement.TERMINE

        super().save(*args, **kwargs)

    @property
    def organisateur_nom(self) -> str:
        """Nom de l'organisateur (établissement ou externe)."""
        if self.etablissement:
            return str(self.etablissement)
        return self.organisateur_externe or "Organisateur non renseigné"

    @property
    def est_a_venir(self) -> bool:
        return self.date_debut > timezone.now() and self.statut not in [
            StatutEvenement.ANNULE,
            StatutEvenement.TERMINE,
        ]

    @property
    def est_en_cours(self) -> bool:
        now = timezone.now()
        if self.date_fin:
            return self.date_debut <= now <= self.date_fin
        return False

    @property
    def est_passe(self) -> bool:
        if self.date_fin:
            return self.date_fin < timezone.now()
        return self.date_debut < timezone.now()

    @property
    def jours_avant(self) -> int | None:
        """Nombre de jours avant l'événement."""
        if not self.est_a_venir:
            return None
        return (self.date_debut - timezone.now()).days

    @property
    def inscriptions_encore_ouvertes(self) -> bool:
        """Vérifie si les inscriptions sont encore possibles."""
        if not self.inscriptions_ouvertes:
            return False
        if self.statut in [StatutEvenement.ANNULE, StatutEvenement.TERMINE]:
            return False
        if self.date_limite_inscription:
            return self.date_limite_inscription > timezone.now()
        return self.est_a_venir

    @property
    def places_restantes(self) -> int | None:
        """Nombre de places restantes (None si illimité)."""
        if self.capacite_max <= 0:
            return None
        return max(0, self.capacite_max - self.nombre_inscrits)

    @property
    def est_complet(self) -> bool:
        if self.capacite_max <= 0:
            return False
        return self.nombre_inscrits >= self.capacite_max

    @property
    def taux_remplissage(self) -> float:
        """Taux de remplissage en pourcentage."""
        if self.capacite_max <= 0:
            return 0
        return round((self.nombre_inscrits / self.capacite_max) * 100, 1)

    @property
    def duree_formatee(self) -> str:
        """Durée de l'événement formatée."""
        if not self.date_fin:
            return "Durée non renseignée"
        delta = self.date_fin - self.date_debut
        heures = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        if delta.days > 0:
            return f"{delta.days} jour(s) {heures}h"
        if heures > 0:
            return f"{heures}h {minutes}min"
        return f"{minutes} min"
