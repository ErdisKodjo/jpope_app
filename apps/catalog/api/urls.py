"""
URLs de l'API catalog.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .simulateur_views import (
    SimulateurAdmissionView,
    SimulateurHistoriqueView,
    VisiteVirtuelle3DView,
)

app_name = "catalog-api"

router = DefaultRouter()
router.register(r"domaines", views.DomaineViewSet, basename="domaines")
router.register(r"metiers", views.MetierViewSet, basename="metiers")
router.register(r"etablissements", views.EtablissementViewSet, basename="etablissements")
router.register(r"formations", views.FormationViewSet, basename="formations")

urlpatterns = [
    # Classements
    path(
        "rankings/etablissements/",
        views.ClassementEtablissementView.as_view(),
        name="ranking-etablissements",
    ),
    path(
        "rankings/formations/",
        views.ClassementFormationView.as_view(),
        name="ranking-formations",
    ),
    path(
        "rankings/methodologie/",
        views.MethodologieClassementView.as_view(),
        name="ranking-methodologie",
    ),

    # Comparateur
    path(
        "compare/<str:type_comparaison>/",
        views.ComparateurView.as_view(),
        name="comparateur",
    ),

    # Simulateur de coût (existant)
    path(
        "simulator/cout/",
        views.SimulateurCoutView.as_view(),
        name="simulator-cout",
    ),

    # Simulateur d'admission prédictif (cahier des charges)
    path(
        "simulateur/admission/",
        SimulateurAdmissionView.as_view(),
        name="simulator-admission",
    ),
    path(
        "simulateur/historique/",
        SimulateurHistoriqueView.as_view(),
        name="simulator-historique",
    ),

    # Visite virtuelle 3D (cahier des charges)
    path(
        "etablissements/<uuid:pk>/visite-3d/",
        VisiteVirtuelle3DView.as_view(),
        name="etablissement-visite-3d",
    ),

    # Stats
    path(
        "stats/",
        views.CatalogStatsView.as_view(),
        name="catalog-stats",
    ),

    # Router
    path("", include(router.urls)),
]
