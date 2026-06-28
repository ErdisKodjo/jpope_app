"""
Modèles Forum et AbonnementForum — structure des forums.
"""
import uuid
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .enums import TypeForum


class Forum(models.Model):
    """
    Forum thématique de la communauté.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nom = models.CharField(_("nom"), max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(_("description"), blank=True)
    icone = models.CharField(
        _("icône (emoji)"),
        max_length=10,
        default="💬",
    )
    couleur = models.CharField(
        _("couleur (hex)"),
        max_length=7,
        default="#3B82F6",
    )

    type = models.CharField(
        _("type de forum"),
        max_length=20,
        choices=TypeForum.choices,
        default=TypeForum.GENERAL,
    )

    domaine = models.ForeignKey(
        "catalog.Domaine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forums",
        verbose_name=_("domaine associé"),
    )
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forums",
        verbose_name=_("établissement associé"),
    )

    regles = models.TextField(
        _("règles du forum"),
        blank=True,
        help_text=_("Règles spécifiques à ce forum"),
    )
    moderation_auto = models.BooleanField(
        _("modération automatique"),
        default=False,
        help_text=_("Les messages sont publiés après validation"),
    )

    acces_restreint = models.BooleanField(
        _("accès restreint"),
        default=False,
        help_text=_("Seuls certains rôles peuvent poster"),
    )
    roles_autorises = models.JSONField(
        _("rôles autorisés à poster"),
        default=list,
        blank=True,
        help_text=_("Ex: ['STUDENT', 'COUNSELOR']"),
    )

    nombre_threads = models.PositiveIntegerField(default=0)
    nombre_messages = models.PositiveIntegerField(default=0)
    nombre_abonnes = models.PositiveIntegerField(default=0)
    dernier_message_at = models.DateTimeField(
        _("date du dernier message"),
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(_("actif"), default=True)
    is_featured = models.BooleanField(_("mis en avant"), default=False)
    ordre = models.PositiveIntegerField(_("ordre d'affichage"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("forum")
        verbose_name_plural = _("forums")
        ordering = ["ordre", "nom"]

    def __str__(self):
        return f"{self.icone} {self.nom}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class AbonnementForum(models.Model):
    """Abonnement d'un utilisateur à un forum."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="abonnements_forums",
    )
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        related_name="abonnements",
    )
    notifications_email = models.BooleanField(default=True)
    notifications_push = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("abonnement forum")
        verbose_name_plural = _("abonnements forums")
        constraints = [
            models.UniqueConstraint(
                fields=["utilisateur", "forum"],
                name="unique_abonnement_forum",
            )
        ]

    def __str__(self):
        return f"{self.utilisateur} → {self.forum}"
