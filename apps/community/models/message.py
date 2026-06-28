"""
Modèle MessageForum — messages dans les threads (aussi appelé Reponse).
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import TypeMessageForum


class MessageForum(models.Model):
    """
    Message/Réponse dans un thread de forum.
    Alias: Reponse
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    thread = models.ForeignKey(
        "community.Thread",
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("discussion"),
    )
    auteur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="messages_forum",
        verbose_name=_("auteur"),
    )

    contenu = models.TextField(
        _("contenu"),
        help_text=_("Texte du message (Markdown supporté)"),
    )

    type = models.CharField(
        _("type"),
        max_length=20,
        choices=TypeMessageForum.choices,
        default=TypeMessageForum.REPONSE,
    )

    reponse_a = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reponses",
        verbose_name=_("réponse à"),
    )

    pieces_jointes = models.JSONField(
        _("pièces jointes (URLs)"),
        default=list,
        blank=True,
    )

    nombre_likes = models.PositiveIntegerField(default=0)
    nombre_signalements = models.PositiveIntegerField(default=0)

    is_solution = models.BooleanField(
        _("marqué comme solution"),
        default=False,
    )
    est_valide = models.BooleanField(
        _("validé par la modération"),
        default=True,
    )
    is_edite = models.BooleanField(
        _("édité"),
        default=False,
    )
    is_supprime = models.BooleanField(
        _("supprimé"),
        default=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(
        _("date de modification"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("message forum")
        verbose_name_plural = _("messages forum")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["thread", "created_at"]),
            models.Index(fields=["auteur"]),
            models.Index(fields=["is_solution"]),
        ]

    def __str__(self):
        return f"[{self.thread.titre}] {self.contenu[:50]}..."

    @property
    def likes_count(self) -> int:
        return self.nombre_likes

    @property
    def is_best_answer(self) -> bool:
        return self.is_solution


class LikeMessageForum(models.Model):
    """Like sur un message de forum."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="likes_messages_forum",
    )
    message = models.ForeignKey(
        MessageForum,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("like message forum")
        verbose_name_plural = _("likes messages forum")
        constraints = [
            models.UniqueConstraint(
                fields=["utilisateur", "message"],
                name="unique_like_message_forum",
            )
        ]

    def __str__(self):
        return f"{self.utilisateur} → {self.message}"


# Alias for compatibility with task description
Reponse = MessageForum
