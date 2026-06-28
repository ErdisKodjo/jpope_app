"""
Serializers DRF pour l'API chatbot.
"""
from rest_framework import serializers

from apps.chatbot.models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "role",
            "role_display",
            "contenu",
            "intent_detecte",
            "confiance_intent",
            "source_reponse",
            "sources_citees",
            "latence_ms",
            "tokens_total",
            "feedbackpositif",
            "created_at",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    dernier_message = serializers.SerializerMethodField()
    nombre_messages = serializers.IntegerField(read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "titre",
            "canal",
            "statut",
            "is_active",
            "nombre_messages",
            "tokens_utilises",
            "dernier_message",
            "created_at",
            "updated_at",
        ]

    def get_dernier_message(self, obj):
        dernier = obj.dernier_message
        if dernier:
            return MessageSerializer(dernier).data
        return None


class ConversationCreateSerializer(serializers.Serializer):
    canal = serializers.ChoiceField(
        choices=["WEB", "MOBILE", "API"],
        default="WEB",
    )


class MessageSendSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=False)
    content = serializers.CharField(max_length=5000)


class FeedbackSerializer(serializers.Serializer):
    message_id = serializers.UUIDField()
    feedback = serializers.ChoiceField(choices=["positive", "negative"])


class ConversationRatingSerializer(serializers.Serializer):
    note = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_blank=True)
