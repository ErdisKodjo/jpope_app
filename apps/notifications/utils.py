"""
Utilitaire de création de notifications in-app.
"""
from apps.notifications.models import Notification, TypeNotification


def notify(user, titre: str, message: str, type_notif: str = TypeNotification.INFO, action_url: str = "") -> None:
    """Crée une notification in-app silencieusement (n'échoue jamais)."""
    try:
        Notification.objects.create(
            user=user,
            titre=titre,
            message=message,
            type_notification=type_notif,
            action_url=action_url,
        )
    except Exception:
        pass
