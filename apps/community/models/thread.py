"""
Modèle Thread — fil de discussion (aussi appelé Discussion) dans un forum.
"""
import uuid
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .enums import StatutThread


class Thread(models.Model):
    """
    Thread (fil de discussion / Discussion) dans un forum.
    Alias: Discussion
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    forum = models.ForeignKey(
        "community.Forum",
        on_delete=models.CASCADE,
        related_name="threads",
        verbose_name=_("forum"),
    )
    auteur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="threads_crees",
        verbose_name=_("auteur"),
    )

    titre = models.CharField(_("titre"), max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    contenu = models.TextField(
        _("contenu du premier message"),
        help_text=_("Contenu du message initial du thread"),
    )

    tags = models.JSONField(
        _("tags"),
        default=list,
        blank=True,
        help_text=_("Ex: ['orientation', 'informatique', 'bac+3']"),
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutThread.choices,
        default=StatutThread.OUVERT,
    )
    is_epingle = models.BooleanField(
        _("épinglé"),
        default=False,
        help_text=_("Les threads épinglés apparaissent en premier"),
    )
    is_ferme = models.BooleanField(
        _("fermé aux nouvelles réponses"),
        default=False,
    )

    nombre_reponses = models.PositiveIntegerField(default=0)
    nombre_vues = models.PositiveIntegerField(default=0)
    nombre_signalements = models.PositiveIntegerField(default=0)

    dernier_message = models.ForeignKey(
        "community.MessageForum",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("dernier message"),
    )
    dernier_message_at = models.DateTimeField(
        _("date du dernier message"),
        blank=True,
        null=True,
    )

    reponse_solution = models.ForeignKey(
        "community.MessageForum",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="threads_resolus",
        verbose_name=_("réponse marquée comme solution"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("discussion")
        verbose_name_plural = _("discussions")
        ordering = ["-is_epingle", "-dernier_message_at"]
        indexes = [
            models.Index(fields=["forum", "statut"]),
            models.Index(fields=["-dernier_message_at"]),
            models.Index(fields=["auteur"]),
        ]

    def __str__(self):
        return f"{self.titre} ({self.forum.nom})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)[:255]
        super().save(*args, **kwargs)

    @property
    def est_resolu(self) -> bool:
        return self.reponse_solution is not None


# Alias for compatibility with task description
Discussion = Thread
