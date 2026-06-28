"""
URLs web pour l'application catalog.
"""
from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    # Domaines
    path("domaines/", views.DomaineListView.as_view(), name="domaine-list"),
    path("domaines/<slug:slug>/", views.DomaineDetailView.as_view(), name="domaine-detail"),

    # Établissements
    path("etablissements/", views.EtablissementListView.as_view(), name="etablissement-list"),
    path("etablissements/<slug:slug>/", views.EtablissementDetailView.as_view(), name="etablissement-detail"),

    # Formations
    path("formations/", views.FormationListView.as_view(), name="formation-list"),
    path("formations/<slug:slug>/", views.FormationDetailView.as_view(), name="formation-detail"),

    # Métiers
    path("metiers/", views.MetierListView.as_view(), name="metier-list"),
    path("metiers/<slug:slug>/", views.MetierDetailView.as_view(), name="metier-detail"),

    # Classements
    path("classements/", views.ClassementView.as_view(), name="classements"),

    # Comparateur
    path("comparateur/", views.ComparateurView.as_view(), name="comparateur"),

    # Simulateur de coût
    path("simulateur/", views.SimulateurView.as_view(), name="simulateur"),
]
