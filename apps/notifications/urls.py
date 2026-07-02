"""
URLs de l'app notifications.
"""
from django.urls import path, include
from . import views

app_name = "notifications"

urlpatterns = [
    path("api/", include("apps.notifications.api.urls", namespace="notifications-api")),
    path("", views.NotificationListView.as_view(), name="list"),
    path("<uuid:pk>/lire/", views.MarkNotificationReadView.as_view(), name="mark-read"),
    path("tout-lire/", views.MarkAllNotificationsReadView.as_view(), name="mark-all-read"),
]
