"""
Vues API pour le chatbot.
"""
import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

from apps.chatbot.models import Conversation, Message
from apps.chatbot.services import ChatbotService

from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSendSerializer,
    MessageSerializer,
    FeedbackSerializer,
    ConversationRatingSerializer,
)


class ConversationListView(generics.ListAPIView):
    """Liste des conversations de l'utilisateur."""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            utilisateur=self.request.user,
        ).order_by("-updated_at")


class ConversationDetailView(generics.RetrieveAPIView):
    """Détail d'une conversation."""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(utilisateur=self.request.user)


class ConversationCreateView(APIView):
    """Créer une nouvelle conversation."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chatbot = ChatbotService()
        conversation = chatbot.creer_conversation(
            request.user,
            canal=serializer.validated_data["canal"],
        )

        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
        )


class MessageSendView(APIView):
    """Envoyer un message et recevoir une réponse (REST, non-WebSocket)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MessageSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        chatbot = ChatbotService()

        # Récupérer ou créer la conversation
        conversation_id = data.get("conversation_id")
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    utilisateur=request.user,
                )
            except Conversation.DoesNotExist:
                return Response(
                    {"error": "Conversation introuvable."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            conversation = chatbot.creer_conversation(request.user, canal="API")

        # Traiter le message
        try:
            response_message = chatbot.traiter_message(
                conversation, data["content"]
            )

            return Response({
                "conversation_id": str(conversation.id),
                "user_message": data["content"],
                "assistant_message": MessageSerializer(response_message).data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erreur traitement message: {e}", exc_info=True)
            return Response(
                {"error": "Erreur de traitement. Veuillez réessayer."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConversationMessagesView(generics.ListAPIView):
    """Historique des messages d'une conversation."""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_id")
        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__utilisateur=self.request.user,
        ).order_by("created_at")


class MessageFeedbackView(APIView):
    """Donner un feedback sur une réponse."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            message = Message.objects.get(
                id=data["message_id"],
                conversation__utilisateur=request.user,
            )
            message.feedbackpositif = (data["feedback"] == "positive")
            message.save(update_fields=["feedbackpositif"])

            return Response({"message": "Feedback enregistré."})

        except Message.DoesNotExist:
            return Response(
                {"error": "Message introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ConversationRateView(APIView):
    """Noter une conversation."""
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        serializer = ConversationRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                utilisateur=request.user,
            )
            conversation.note_satisfaction = serializer.validated_data["note"]
            conversation.feedback_utilisateur = serializer.validated_data.get(
                "feedback", ""
            )
            conversation.save(update_fields=[
                "note_satisfaction", "feedback_utilisateur"
            ])

            return Response({"message": "Note enregistrée. Merci !"})

        except Conversation.DoesNotExist:
            return Response(
                {"error": "Conversation introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
