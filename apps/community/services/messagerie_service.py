"""
Service de gestion de la messagerie privée.
"""
import logging
from django.db import transaction
from django.db.models import F
from django.utils import timezone

logger = logging.getLogger(__name__)


class MessagerieService:
    """Service pour la gestion des messages privés."""

    @classmethod
    @transaction.atomic
    def envoyer_message(cls, conversation, auteur, contenu: str, type_contenu: str = "TEXTE"):
        """Envoie un message dans une conversation privée."""
        from apps.community.models import MessagePrive, ConversationPrivee, ParticipantConversation

        message = MessagePrive.objects.create(
            conversation=conversation,
            auteur=auteur,
            contenu=contenu,
            type_contenu=type_contenu,
        )

        # Mettre à jour la conversation
        ConversationPrivee.objects.filter(pk=conversation.pk).update(
            dernier_message=message,
            dernier_message_at=message.created_at,
        )

        # Mettre à jour les compteurs non-lus pour les autres participants
        ParticipantConversation.objects.filter(
            conversation=conversation,
        ).exclude(utilisateur=auteur).update(
            nombre_non_lus=F("nombre_non_lus") + 1
        )

        logger.info(
            f"Message envoyé dans conversation {conversation.id} par {auteur.email}"
        )
        return message

    @classmethod
    def marquer_lus(cls, conversation, utilisateur) -> int:
        """Marque tous les messages d'une conversation comme lus pour un utilisateur."""
        from apps.community.models import ParticipantConversation

        count = ParticipantConversation.objects.filter(
            conversation=conversation,
            utilisateur=utilisateur,
        ).update(nombre_non_lus=0)

        return count
