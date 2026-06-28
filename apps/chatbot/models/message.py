"""
Modèle Message — message individuel dans une conversation chatbot.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import RoleMessage, SourceReponse


class Message(models.Model):
    """
    Message individuel dans une conversation chatbot.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    conversation = models.ForeignKey(
        "chatbot.Conversation",
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("conversation"),
    )

    role = models.CharField(
        _("rôle"),
        max_length=20,
        choices=RoleMessage.choices,
    )
    contenu = models.TextField(
        _("contenu du message"),
        help_text=_("Texte du message (Markdown supporté)"),
    )

    metadata = models.JSONField(
        _("métadonnées"),
        default=dict,
        blank=True,
        help_text=_(
            "Données additionnelles : intent, entities, sources, "
            "latence, tokens, etc."
        ),
    )

    intent_detecte = models.CharField(
        _("intention détectée"),
        max_length=50,
        blank=True,
        help_text=_("Code de l'intention détectée pour ce message"),
    )
    confiance_intent = models.FloatField(
        _("confiance de l'intent (0-1)"),
        default=0,
    )
    source_reponse = models.CharField(
        _("source de la réponse"),
        max_length=30,
        choices=SourceReponse.choices,
        blank=True,
    )
    handler_utilise = models.CharField(
        _("handler utilisé"),
        max_length=100,
        blank=True,
    )

    tokens_prompt = models.PositiveIntegerField(
        _("tokens du prompt"),
        default=0,
    )
    tokens_completion = models.PositiveIntegerField(
        _("tokens de la complétion"),
        default=0,
    )
    tokens_total = models.PositiveIntegerField(
        _("tokens totaux"),
        default=0,
    )
    tokens_used = models.PositiveIntegerField(
        _("tokens utilisés (alias)"),
        default=0,
    )
    modele_utilise = models.CharField(
        _("modèle utilisé"),
        max_length=50,
        blank=True,
    )
    latence_ms = models.PositiveIntegerField(
        _("latence (ms)"),
        default=0,
    )

    sources_citees = models.JSONField(
        _("sources citées"),
        default=list,
        blank=True,
        help_text=_(
            "Liste des sources utilisées pour la réponse : "
            "[{'type': 'formation', 'id': '...', 'titre': '...'}]"
        ),
    )

    feedbackpositif = models.BooleanField(
        _("réponse utile"),
        blank=True,
        null=True,
    )

    entites_extraites = models.JSONField(
        _("entités extraites"),
        default=dict,
        blank=True,
        help_text=_(
            "Ex: {'domaine': 'informatique', 'ville': 'Lomé', 'budget': 500000}"
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["intent_detecte"]),
        ]

    def __str__(self):
        role_display = self.get_role_display()
        return f"[{role_display}] {self.contenu[:50]}..."

    @property
    def est_utilisateur(self):
        return self.role == RoleMessage.USER

    @property
    def est_assistant(self):
        return self.role == RoleMessage.ASSISTANT
