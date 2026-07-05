"""
Modèle Test d'orientation.
"""
import uuid
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .enums import TypeTest

class TestOrientation(models.Model):
    """
    Test d'orientation complet.
    Peut être de type RIASEC, compétences, personnalité, etc.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    nom = models.CharField(_("nom du test"), max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(_("description"), blank=True)
    description_courte = models.CharField(
        _("description courte"),
        max_length=300,
        blank=True,
    )

    # Caractéristiques
    type = models.CharField(
        _("type de test"),
        max_length=20,
        choices=TypeTest.choices,
        default=TypeTest.MIXTE,
    )
    duree_estimee_minutes = models.PositiveIntegerField(
        _("durée estimée (minutes)"),
        default=15,
        help_text=_("Durée moyenne pour compléter le test"),
    )
    nombre_questions = models.PositiveIntegerField(
        _("nombre de questions"),
        default=0,
        help_text=_("Calculé automatiquement"),
    )

    # Configuration du scoring
    dimensions_evaluees = models.JSONField(
        _("dimensions évaluées"),
        default=list,
        help_text=_("Codes des dimensions : ['R', 'I', 'A', 'S', 'E', 'C']"),
    )
    methode_scoring = models.CharField(
        _("méthode de scoring"),
        max_length=50,
        default="RIASEC_PONDERE",
        help_text=_("Algorithme utilisé pour le calcul des scores"),
    )

    # Public cible
    niveau_minimum = models.CharField(
        _("niveau minimum requis"),
        max_length=20,
        blank=True,
        help_text=_("Ex: 'Terminale', 'L1', etc."),
    )
    age_minimum = models.PositiveIntegerField(
        _("âge minimum"),
        default=15,
    )

    # Statistiques
    nombre_passations = models.PositiveIntegerField(default=0)
    taux_completion = models.FloatField(
        _("taux de complétion (%)"),
        default=0,
    )
    score_moyen = models.FloatField(
        _("score moyen global"),
        default=0,
    )

    # Statut
    is_active = models.BooleanField(_("actif"), default=True)
    is_public = models.BooleanField(
        _("public"),
        default=True,
        help_text=_("Accessible à tous les utilisateurs"),
    )
    is_featured = models.BooleanField(_("mis en avant"), default=False)
    ordre = models.PositiveIntegerField(_("ordre d'affichage"), default=0)

    # Métadonnées
    auteur = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tests_crees",
        verbose_name=_("auteur du test"),
    )
    version = models.CharField(
        _("version"),
        max_length=20,
        default="1.0",
    )
    date_publication = models.DateField(
        _("date de publication"),
        blank=True,
        null=True,
    )
    source_scientifique = models.CharField(
        _("source / référence scientifique"),
        max_length=255,
        blank=True,
        help_text=_("Ex: 'Holland RIASEC', 'Big Five', etc."),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("test d'orientation")
        verbose_name_plural = _("tests d'orientation")
        ordering = ["ordre", "-created_at"]

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.nom)
            if TestOrientation.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{slug}-{uuid.uuid4().hex[:8]}"
            self.slug = slug
        # Mettre à jour le nombre de questions
        if self.pk:
            self.nombre_questions = self.questions.count()
        super().save(*args, **kwargs)

    @property
    def questions_actives(self):
        return self.questions.filter(is_active=True).order_by("ordre")

    @property
    def peut_etre_passe(self) -> bool:
        return self.is_active and self.questions_actives.count() > 0
