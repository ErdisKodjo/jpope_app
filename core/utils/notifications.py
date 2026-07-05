"""
Shared notification helper for silent in-app notifications.

Replaces the duplicated ``_notify`` wrappers that existed in
``apps.orientation.views`` and ``apps.community.views``.
"""


def notify_silent(user, titre, message, type_notif="INFO", action_url=""):
    """Create an in-app notification, silently swallowing any errors."""
    try:
        from apps.notifications.utils import notify
        notify(
            user=user,
            titre=titre,
            message=message,
            type_notif=type_notif,
            action_url=action_url,
        )
    except Exception:
        pass
