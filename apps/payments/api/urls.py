"""
URLs de l'API payments.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .stripe_views import (
    StripePaymentIntentView,
    StripeSubscribeView,
    StripeCancelView,
    StripeSubscriptionDetailView,
    StripePortalView,
    StripePlansView,
    StripeWebhookView,
)

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

    # Paiements Mobile Money (Flooz/TMoney)
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

    # Callback Mobile Money (Flooz/TMoney)
    path(
        "callback/mobile-money/",
        views.PaymentCallbackView.as_view(),
        name="payment-callback",
    ),

    # Stripe (carte bancaire — cahier des charges business plan P-5)
    path(
        "stripe/payment-intent/",
        StripePaymentIntentView.as_view(),
        name="stripe-payment-intent",
    ),
    path(
        "stripe/subscribe/",
        StripeSubscribeView.as_view(),
        name="stripe-subscribe",
    ),
    path(
        "stripe/cancel/",
        StripeCancelView.as_view(),
        name="stripe-cancel",
    ),
    path(
        "stripe/subscription/<str:subscription_id>/",
        StripeSubscriptionDetailView.as_view(),
        name="stripe-subscription-detail",
    ),
    path(
        "stripe/portal/",
        StripePortalView.as_view(),
        name="stripe-portal",
    ),
    path(
        "stripe/plans/",
        StripePlansView.as_view(),
        name="stripe-plans",
    ),
    path(
        "stripe/webhook/",
        StripeWebhookView.as_view(),
        name="stripe-webhook",
    ),
]
