"""
Vues API pour l'app notifications.
"""
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification

from .serializers import (
    NotificationSerializer,
    NotificationMarkReadSerializer,
    SendBulkNotificationSerializer,
)


class NotificationListView(generics.ListAPIView):
    """Liste des notifications de l'utilisateur connecté."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)

        type_notif = self.request.query_params.get("type")
        if type_notif:
            qs = qs.filter(type_notification=type_notif)

        non_lues = self.request.query_params.get("non_lues")
        if non_lues == "true":
            qs = qs.filter(is_read=False)

        return qs.order_by("-created_at")


class NotificationDetailView(generics.RetrieveAPIView):
    """Détail d'une notification (marque comme lue)."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.marquer_comme_lue()
        return super().retrieve(request, *args, **kwargs)


class NotificationMarkReadView(APIView):
    """Marque des notifications comme lues."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.get("mark_all"):
            count = Notification.objects.filter(
                user=request.user, is_read=False
            ).update(is_read=True, read_at=timezone.now())
            return Response({"message": f"{count} notification(s) marquée(s) comme lue(s)."})

        ids = data.get("notification_ids", [])
        if not ids:
            return Response(
                {"error": "notification_ids ou mark_all requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        count = Notification.objects.filter(
            id__in=ids,
            user=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())

        return Response({"message": f"{count} notification(s) marquée(s) comme lue(s)."})


class NotificationCountView(APIView):
    """Compte les notifications non lues."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user)
        return Response({
            "total": qs.count(),
            "non_lues": qs.filter(is_read=False).count(),
            "lues": qs.filter(is_read=True).count(),
        })
