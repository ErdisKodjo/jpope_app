"""
WebSocket Consumer pour le chatbot temps réel.
Uses AsyncJsonWebsocketConsumer from channels.generic.websocket.
"""
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer pour le chatbot IA.
    Permet une communication temps réel entre le frontend et le chatbot.

    Protocol:
    - Client sends: {"type": "message", "content": "..."}
    - Server sends: {"type": "message", "role": "assistant", "content": "...", ...}
    - Client sends: {"type": "ping"}
    - Server sends: {"type": "pong"}
    - Client sends: {"type": "feedback", "message_id": "...", "feedback": "positive|negative"}
    """

    async def connect(self):
        """Connexion WebSocket."""
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.conversation_id = self.scope["url_route"]["kwargs"].get("conversation_id")
        self.room_group_name = f"chatbot_{self.user.id}"

        # Rejoindre le groupe de canaux
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

        # Envoyer un message de bienvenue
        await self.send_json({
            "type": "connection",
            "status": "connected",
            "conversation_id": self.conversation_id,
            "message": "Connecté à AvenBot !",
        })

    async def disconnect(self, close_code):
        """Déconnexion WebSocket."""
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive_json(self, content, **kwargs):
        """Réception d'un message JSON du client."""
        try:
            message_type = content.get("type", "message")

            if message_type == "message":
                await self.handle_user_message(content.get("content", ""))
            elif message_type == "ping":
                await self.send_json({"type": "pong"})
            elif message_type == "feedback":
                await self.handle_feedback(content)
            elif message_type == "new_conversation":
                await self.handle_new_conversation()
            else:
                await self.send_json({
                    "type": "error",
                    "message": f"Type de message inconnu: {message_type}",
                })

        except Exception as e:
            logger.error(f"Erreur WebSocket: {e}", exc_info=True)
            await self.send_json({
                "type": "error",
                "message": "Erreur interne du serveur",
            })

    async def handle_user_message(self, content: str):
        """Traite un message utilisateur et envoie la réponse."""
        if not content or not content.strip():
            return

        # Indiquer que le bot est en train d'écrire
        await self.send_json({
            "type": "typing",
            "status": "start",
        })

        try:
            # Traiter le message de manière synchrone dans un thread
            response_message = await database_sync_to_async(self._process_message)(content)

            # Envoyer la réponse au client
            await self.send_json({
                "type": "message",
                "role": "assistant",
                "content": response_message.contenu,
                "message_id": str(response_message.id),
                "conversation_id": self.conversation_id,
                "intent": response_message.intent_detecte,
                "sources": response_message.sources_citees,
                "metadata": {
                    "latence_ms": response_message.latence_ms,
                    "source": response_message.source_reponse,
                    "tokens": response_message.tokens_total,
                },
            })

        except Exception as e:
            logger.error(f"Erreur traitement message: {e}", exc_info=True)
            await self.send_json({
                "type": "message",
                "role": "assistant",
                "content": (
                    "Désolé, je rencontre un problème technique. "
                    "Veuillez réessayer dans quelques instants."
                ),
            })

        finally:
            await self.send_json({
                "type": "typing",
                "status": "stop",
            })

    def _process_message(self, content: str):
        """Traite le message de manière synchrone (appelé via database_sync_to_async)."""
        from apps.chatbot.services.chatbot_service import ChatbotService
        from apps.chatbot.models import Conversation

        chatbot = ChatbotService()

        # Récupérer ou créer la conversation
        if self.conversation_id:
            try:
                conversation = Conversation.objects.get(
                    id=self.conversation_id,
                    utilisateur=self.user,
                )
            except Conversation.DoesNotExist:
                conversation = chatbot.creer_conversation(self.user, canal="WEB")
                self.conversation_id = str(conversation.id)
        else:
            conversation = chatbot.creer_conversation(self.user, canal="WEB")
            self.conversation_id = str(conversation.id)

        return chatbot.traiter_message(conversation, content)

    async def handle_feedback(self, data: dict):
        """Gère le feedback utilisateur sur une réponse."""
        message_id = data.get("message_id")
        feedback = data.get("feedback")  # "positive" ou "negative"

        if message_id and feedback:
            await database_sync_to_async(self._save_feedback)(message_id, feedback)

            await self.send_json({
                "type": "feedback_received",
                "message_id": message_id,
            })

    def _save_feedback(self, message_id: str, feedback: str):
        """Sauvegarde le feedback en base de données."""
        from apps.chatbot.models import Message
        try:
            message = Message.objects.get(id=message_id)
            message.feedbackpositif = (feedback == "positive")
            message.save(update_fields=["feedbackpositif"])
        except Message.DoesNotExist:
            pass

    async def handle_new_conversation(self):
        """Crée une nouvelle conversation."""
        self.conversation_id = None
        await self.send_json({
            "type": "new_conversation",
            "status": "ok",
            "message": "Nouvelle conversation démarrée.",
        })

    # Handlers pour les messages de groupe (channel layer)
    async def chat_message(self, event):
        """Envoie un message reçu du groupe."""
        await self.send_json(event["message"])


# Alias requis par le routing
ChatbotConsumer = ChatConsumer
