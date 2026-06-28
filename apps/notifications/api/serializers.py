"""
Serializers DRF pour l'API notifications.
"""
from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source="get_type_notification_display", read_only=True
    )
    est_lue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "type_notification",
            "type_display",
            "titre",
            "message",
            "action_url",
            "is_read",
            "est_lue",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields


class NotificationMarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )
    mark_all = serializers.BooleanField(default=False)


class SendBulkNotificationSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.UUIDField())
    titre = serializers.CharField(max_length=255)
    message = serializers.CharField()
    type_notification = serializers.CharField(default="INFO")
    action_url = serializers.URLField(required=False, allow_blank=True)
