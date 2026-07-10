"""URLs API de la bibliothèque numérique."""
from django.urls import path
from . import views

app_name = "library-api"

urlpatterns = [
    path("", views.RessourceListView.as_view(), name="list"),
    path("recommandations/", views.RecommandationsView.as_view(), name="recommandations"),
    path("categories/", views.CategoriesListView.as_view(), name="categories"),
    path("stats/", views.StatsBibliothequeView.as_view(), name="stats"),
    path("<slug:slug>/", views.RessourceDetailView.as_view(), name="detail"),
    path("<slug:slug>/download/", views.RessourceDownloadView.as_view(), name="download"),
    path("<slug:slug>/vote/", views.RessourceVoteView.as_view(), name="vote"),
    path("<slug:slug>/favori/", views.FavoriToggleView.as_view(), name="favori"),
]
