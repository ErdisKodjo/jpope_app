"""
URLs de l'app analytics.
"""
from django.urls import path, include

app_name = "analytics"

urlpatterns = [
    path("api/", include("apps.analytics.api.urls", namespace="analytics-api")),
]
