"""
URLs de l'API notifications.
"""
from django.urls import path

from . import views

app_name = "notifications-api"

urlpatterns = [
    path(
        "",
        views.NotificationListView.as_view(),
        name="notifications-list",
    ),
    path(
        "<uuid:pk>/",
        views.NotificationDetailView.as_view(),
        name="notification-detail",
    ),
    path(
        "mark-read/",
        views.NotificationMarkReadView.as_view(),
        name="notifications-mark-read",
    ),
    path(
        "count/",
        views.NotificationCountView.as_view(),
        name="notifications-count",
    ),
]
