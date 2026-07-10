"""
URLs de l'API orientation.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .ikigai_views import (
    IkigaiResultatView,
    RapportCombineView,
    ListeTestsIkigaiView,
)

app_name = "orientation-api"

router = DefaultRouter()
router.register(r"tests", views.TestOrientationViewSet, basename="tests")

urlpatterns = [
    # Passation
    path("test/start/", views.CommencerTestView.as_view(), name="test-start"),
    path("test/save-answer/", views.SauvegarderReponseView.as_view(), name="test-save"),
    path("test/submit/", views.SoumettreTestView.as_view(), name="test-submit"),

    # Résultats
    path("resultats/", views.ResultatTestListView.as_view(), name="resultats-list"),
    path("resultats/<uuid:pk>/", views.ResultatTestDetailView.as_view(), name="resultat-detail"),

    # Ikigai (cahier des charges — Test Ikigai combiné)
    path("ikigai/tests/", ListeTestsIkigaiView.as_view(), name="ikigai-tests"),
    path("ikigai/resultat/", IkigaiResultatView.as_view(), name="ikigai-resultat"),
    path("rapport-combine/", RapportCombineView.as_view(), name="rapport-combine"),

    # Recommandations
    path("recommandations/", views.RecommandationListView.as_view(), name="recommandations"),
    path(
        "recommandations/<uuid:pk>/engagement/",
        views.RecommandationEngagementView.as_view(),
        name="recommandation-engagement",
    ),

    # Historique & Analytics
    path("historique/", views.HistoriqueTestsView.as_view(), name="historique"),
    path("evolution/", views.EvolutionProfilView.as_view(), name="evolution"),
    path("stats/", views.OrientationStatsView.as_view(), name="stats"),

    # Router
    path("", include(router.urls)),
]
