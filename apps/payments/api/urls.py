"""
URLs de l'API payments.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "payments-api"

router = DefaultRouter()
router.register(
    r"plans",
    views.PlanAbonnementViewSet,
    basename="plans",
)

urlpatterns = [
    # Plans
    path("", include(router.urls)),

    # Abonnements
    path(
        "abonnements/",
        views.AbonnementListView.as_view(),
        name="abonnements-list",
    ),
    path(
        "abonnements/courant/",
        views.AbonnementCourantView.as_view(),
        name="abonnement-courant",
    ),

    # Paiements
    path(
        "paiements/initier/",
        views.InitierPaiementView.as_view(),
        name="initier-paiement",
    ),
    path(
        "paiements/verifier/",
        views.VerifierStatutView.as_view(),
        name="verifier-statut",
    ),
    path(
        "paiements/historique/",
        views.PaiementHistoriqueView.as_view(),
        name="paiements-historique",
    ),

    # Factures
    path(
        "factures/",
        views.FactureListView.as_view(),
        name="factures-list",
    ),
]
