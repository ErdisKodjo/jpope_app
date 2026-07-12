"""
Modèles ConversationPrivee, ParticipantConversation, MessagePrive — messagerie privée.

🔒 Sécurité : le contenu des messages privés est chiffré au repos (Fernet).
Conformément au cahier des charges (section 3 — Sécurité) :
"Chiffrement de bout en bout des données sensibles (notes scolaires, rapports psychologiques)."
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.compliance.encryption_fields import EncryptedTextField
from .enums import StatutMessagerie


class ConversationPrivee(models.Model):
    """
    Conversation privée entre utilisateurs.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    titre = models.CharField(
        _("titre"),
        max_length=255,
        blank=True,
        help_text=_("Titre pour les groupes, vide pour les conversations à 2"),
    )
    is_groupe = models.BooleanField(
        _("conversation de groupe"),
        default=False,
    )

    participants = models.ManyToManyField(
        "accounts.User",
        through="ParticipantConversation",
        related_name="conversations_privees",
        verbose_name=_("participants"),
    )

    dernier_message = models.ForeignKey(
        "community.MessagePrive",
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("conversation privée")
        verbose_name_plural = _("conversations privées")
        ordering = ["-dernier_message_at"]

    def __str__(self):
        return self.titre or f"Conversation {self.id}"


class ParticipantConversation(models.Model):
    """
    Participant à une conversation privée.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        ConversationPrivee,
        on_delete=models.CASCADE,
        related_name="participations",
    )
    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="participations_conversations",
    )

    nombre_non_lus = models.PositiveIntegerField(
        _("messages non lus"),
        default=0,
    )
    is_admin = models.BooleanField(
        _("administrateur du groupe"),
        default=False,
    )
    is_mute = models.BooleanField(
        _("notifications coupées"),
        default=False,
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("participant conversation")
        verbose_name_plural = _("participants conversations")
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "utilisateur"],
                name="unique_participant_conversation",
            )
        ]

    def __str__(self):
        return f"{self.utilisateur} → {self.conversation}"


class MessagePrive(models.Model):
    """
    Message dans une conversation privée.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    conversation = models.ForeignKey(
        ConversationPrivee,
        on_delete=models.CASCADE,
        related_name="messages_prives",
        verbose_name=_("conversation"),
    )
    auteur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="messages_prives_envoyes",
        verbose_name=_("auteur"),
    )

    contenu = EncryptedTextField(_("contenu"))
    type_contenu = models.CharField(
        _("type de contenu"),
        max_length=20,
        choices=[
            ("TEXTE", "Texte"),
            ("IMAGE", "Image"),
            ("FICHIER", "Fichier"),
            ("EMOJI", "Emoji"),
        ],
        default="TEXTE",
    )
    fichier_joint = models.FileField(
        _("fichier joint"),
        upload_to="messagerie/fichiers/%Y/%m/",
        blank=True,
        null=True,
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutMessagerie.choices,
        default=StatutMessagerie.ENVOYE,
    )
    is_edite = models.BooleanField(_("édité"), default=False)
    is_supprime = models.BooleanField(_("supprimé"), default=False)

    reponse_a = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reponses",
        verbose_name=_("réponse à"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(
        _("date de modification"),
        blank=True,
        null=True,
    )
    lu_at = models.DateTimeField(
        _("date de lecture"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("message privé")
        verbose_name_plural = _("messages privés")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.auteur}] {self.contenu[:50]}..."
