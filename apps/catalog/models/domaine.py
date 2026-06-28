"""
Modèle Domaine d'études / professionnel.
"""
import uuid
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Domaine(models.Model):
    """
    Grand domaine d'études et professionnel.
    Ex: Informatique, Santé, Droit, Gestion, etc.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    nom = models.CharField(_("nom"), max_length=150, unique=True)
    slug = models.SlugField(_("slug"), max_length=150, unique=True, blank=True)
    description = models.TextField(_("description"), blank=True)
    icon = models.CharField(
        _("icône (emoji ou class)"),
        max_length=50,
        blank=True,
        help_text=_("Ex: 💻, 🏥, ⚖️"),
    )
    couleur = models.CharField(
        _("couleur (hex)"),
        max_length=7,
        default="#3B82F6",
        help_text=_("Code hexadécimal, ex: #3B82F6"),
    )

    # Statistiques
    nombre_formations = models.PositiveIntegerField(default=0)
    nombre_metiers = models.PositiveIntegerField(default=0)

    # Métadonnées
    is_active = models.BooleanField(_("actif"), default=True)
    ordre = models.PositiveIntegerField(_("ordre d'affichage"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("domaine")
        verbose_name_plural = _("domaines")
        ordering = ["ordre", "nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
