"""
URLs API pour le chatbot.
"""
from django.urls import path

from . import views

app_name = "chatbot-api"

urlpatterns = [
    # Conversations
    path(
        "conversations/",
        views.ConversationListView.as_view(),
        name="conversation-list",
    ),
    path(
        "conversations/create/",
        views.ConversationCreateView.as_view(),
        name="conversation-create",
    ),
    path(
        "conversations/<uuid:pk>/",
        views.ConversationDetailView.as_view(),
        name="conversation-detail",
    ),
    path(
        "conversations/<uuid:conversation_id>/messages/",
        views.ConversationMessagesView.as_view(),
        name="conversation-messages",
    ),
    path(
        "conversations/<uuid:conversation_id>/rate/",
        views.ConversationRateView.as_view(),
        name="conversation-rate",
    ),

    # Messages
    path(
        "message/",
        views.MessageSendView.as_view(),
        name="message-send",
    ),
    path(
        "message/feedback/",
        views.MessageFeedbackView.as_view(),
        name="message-feedback",
    ),
]
