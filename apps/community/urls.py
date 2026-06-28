from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path("", views.ForumListView.as_view(), name="forum-list"),
    path("forum/<int:pk>/", views.ForumDetailView.as_view(), name="forum-detail"),
    path("thread/<int:pk>/", views.ThreadDetailView.as_view(), name="thread-detail"),
]
