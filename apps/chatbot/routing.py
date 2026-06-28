"""
WebSocket routing pour le chatbot IA.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/chat/", consumers.ChatConsumer.as_asgi()),
    path("ws/chatbot/", consumers.ChatConsumer.as_asgi()),
    path(
        "ws/chatbot/<uuid:conversation_id>/",
        consumers.ChatConsumer.as_asgi(),
    ),
]
