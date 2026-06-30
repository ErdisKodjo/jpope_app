"""
URLs pour l'app chatbot.
"""
from django.urls import path, include

from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.ChatbotPageView.as_view(), name="home"),
    path("api/", include("apps.chatbot.api.urls", namespace="chatbot-api")),
]
