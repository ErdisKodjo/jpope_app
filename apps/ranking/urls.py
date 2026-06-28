"""
URLs web pour l'application ranking.
"""
from django.urls import path

from . import views

app_name = "ranking"

urlpatterns = [
    path("", views.ClassementListView.as_view(), name="classement-list"),
    path("<uuid:pk>/", views.ClassementDetailView.as_view(), name="classement-detail"),
    path("top/", views.TopNationalView.as_view(), name="top-national"),
]
