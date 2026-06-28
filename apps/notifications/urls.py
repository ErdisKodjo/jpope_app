"""
URLs de l'app notifications.
"""
from django.urls import path, include

app_name = "notifications"

urlpatterns = [
    path("api/", include("apps.notifications.api.urls", namespace="notifications-api")),
]
