"""
URLs web pour l'application orientation.
"""
from django.urls import path

from . import views

app_name = "orientation"

urlpatterns = [
    path("", views.OrientationHomeView.as_view(), name="home"),
    path("tests/", views.TestListView.as_view(), name="test-list"),
    path("tests/<slug:slug>/", views.TestDetailView.as_view(), name="test-detail"),
    path("resultats/", views.ResultatListView.as_view(), name="resultats"),
    path("resultats/<uuid:pk>/", views.ResultatDetailView.as_view(), name="resultat-detail"),
    path("recommandations/", views.RecommandationListView.as_view(), name="recommandations"),
]
