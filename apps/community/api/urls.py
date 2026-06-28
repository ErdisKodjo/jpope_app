"""
URLs de l'API community.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "community-api"

router = DefaultRouter()
router.register(r"forums", views.ForumViewSet, basename="forums")
router.register(r"threads", views.ThreadViewSet, basename="threads")
router.register(r"mentors", views.MentorViewSet, basename="mentors")
router.register(r"mentorats", views.MentoratViewSet, basename="mentorats")
router.register(r"conversations", views.ConversationViewSet, basename="conversations")
router.register(r"messages", views.MessagePriveViewSet, basename="messages")
router.register(r"signalements", views.SignalementViewSet, basename="signalements")

urlpatterns = [
    # Messages forum
    path(
        "messages-forum/<uuid:message_id>/like/",
        views.MessageForumLikeView.as_view(),
        name="message-like",
    ),

    # Conversations
    path(
        "conversations/create/",
        views.ConversationCreateView.as_view(),
        name="conversations-create",
    ),

    # Blocages
    path(
        "blocages/",
        views.BlocageView.as_view(),
        name="blocages",
    ),

    # Router
    path("", include(router.urls)),
]
