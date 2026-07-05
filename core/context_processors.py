import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def global_context(request):
    """Contexte global disponible dans tous les templates."""
    ctx = {
        "PROJECT_NAME": "AvenSU-Orienta",
        "PROJECT_VERSION": "1.0.0",
        "DEBUG": settings.DEBUG,
        "CHATBOT_ENABLED": bool(getattr(settings, "CHATBOT", {}).get("OPENAI_API_KEY")),
        "unread_notifications_count": 0,
    }
    if request.user.is_authenticated:
        try:
            from apps.notifications.models import Notification
            ctx["unread_notifications_count"] = Notification.objects.filter(
                user=request.user,
                is_read=False,
            ).count()
        except Exception:
            logger.exception(
                "Impossible de récupérer le nombre de notifications non lues "
                "pour l'utilisateur %s",
                request.user.pk,
            )
    return ctx
