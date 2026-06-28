"""
URLs pour l'app chatbot.
"""
from django.urls import path, include

app_name = "chatbot"

urlpatterns = [
    path("api/", include("apps.chatbot.api.urls", namespace="chatbot-api")),
]
