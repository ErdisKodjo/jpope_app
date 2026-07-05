"""
Utilitaire de création de notifications in-app.
"""
import logging

from apps.notifications.models import Notification, TypeNotification

logger = logging.getLogger(__name__)


def notify(user, titre: str, message: str, type_notif: str = TypeNotification.INFO, action_url: str = "") -> None:
    """Crée une notification in-app sans interrompre le flux appelant.

    Les erreurs sont journalisées plutôt que silencieusement ignorées afin
    qu'un échec de création de notification reste visible en supervision.
    """
    try:
        Notification.objects.create(
            user=user,
            titre=titre,
            message=message,
            type_notification=type_notif,
            action_url=action_url,
        )
    except Exception:
        logger.exception(
            "Échec de création de la notification in-app pour l'utilisateur %s",
            getattr(user, "pk", user),
        )
