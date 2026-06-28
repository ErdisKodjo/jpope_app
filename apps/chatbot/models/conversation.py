"""
Modèle Conversation — session de discussion chatbot.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import StatutConversation, CanalDiscussion


class Conversation(models.Model):
    """
    Session de discussion entre un utilisateur et le chatbot.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="conversations_chatbot",
        verbose_name=_("utilisateur"),
    )

    titre = models.CharField(
        _("titre auto-généré"),
        max_length=255,
        blank=True,
        help_text=_("Généré à partir du premier message utilisateur"),
    )
    canal = models.CharField(
        _("canal d'origine"),
        max_length=20,
        choices=CanalDiscussion.choices,
        default=CanalDiscussion.WEB,
    )
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutConversation.choices,
        default=StatutConversation.ACTIVE,
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )

    contexte_utilisateur = models.JSONField(
        _("contexte utilisateur"),
        default=dict,
        blank=True,
        help_text=_(
            "Snapshot du profil, derniers résultats de test, favoris. "
            "Injecté dans le prompt système."
        ),
    )

    nombre_messages = models.PositiveIntegerField(default=0)
    nombre_messages_utilisateur = models.PositiveIntegerField(default=0)
    nombre_messages_assistant = models.PositiveIntegerField(default=0)
    tokens_utilises = models.PositiveIntegerField(
        _("tokens consommés"),
        default=0,
    )
    cout_estime_usd = models.DecimalField(
        _("coût estimé (USD)"),
        max_digits=8,
        decimal_places=4,
        default=0,
    )
    duree_totale_secondes = models.PositiveIntegerField(
        _("durée totale de la conversation (secondes)"),
        default=0,
    )

    note_satisfaction = models.PositiveIntegerField(
        _("note de satisfaction (1-5)"),
        blank=True,
        null=True,
    )
    feedback_utilisateur = models.TextField(
        _("feedback utilisateur"),
        blank=True,
    )

    signale = models.BooleanField(
        _("conversation signalée"),
        default=False,
    )
    motif_signalement = models.TextField(
        _("motif de signalement"),
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    dernier_message_at = models.DateTimeField(
        _("date du dernier message"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("conversation")
        verbose_name_plural = _("conversations")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["utilisateur", "-updated_at"]),
            models.Index(fields=["statut"]),
        ]

    def __str__(self):
        return f"Conv. {self.titre[:30]} — {self.utilisateur.get_full_name()}"

    @property
    def dernier_message(self):
        return self.messages.order_by("-created_at").first()

    @property
    def intents_detectes(self):
        """Retourne la liste des intents détectés dans la conversation."""
        return list(
            self.messages
            .exclude(intent_detecte="")
            .values_list("intent_detecte", flat=True)
            .distinct()
        )
