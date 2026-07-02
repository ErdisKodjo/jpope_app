from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path("", views.ForumListView.as_view(), name="forum-list"),
    path("forum/<slug:slug>/", views.ForumDetailView.as_view(), name="forum-detail"),
    path("forum/<slug:forum_slug>/nouveau/", views.ThreadCreateView.as_view(), name="thread-create"),
    path("discussion/<uuid:pk>/", views.ThreadDetailView.as_view(), name="thread-detail"),
    path("discussion/<uuid:thread_pk>/repondre/", views.MessageCreateView.as_view(), name="message-create"),
    path("message/<uuid:pk>/like/", views.LikeMessageView.as_view(), name="message-like"),
]
