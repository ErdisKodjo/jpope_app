"""
Vues API Stripe — paiements carte bancaire + abonnements + webhook.

Endpoints :
- POST /api/v1/payments/stripe/payment-intent/    → créer un PaymentIntent
- POST /api/v1/payments/stripe/subscribe/         → créer un abonnement
- POST /api/v1/payments/stripe/cancel/            → annuler un abonnement
- GET  /api/v1/payments/stripe/subscription/<id>/ → récupérer un abonnement
- POST /api/v1/payments/stripe/portal/            → session portail client
- GET  /api/v1/payments/stripe/plans/             → liste des plans
- POST /api/v1/payments/stripe/webhook/           → webhook Stripe (signature)
"""
import json
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.services.stripe_service import StripeService


class StripePaymentIntentView(APIView):
    """Crée un PaymentIntent pour un paiement ponctuel."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        description = request.data.get("description", "")
        if not amount or int(amount) <= 0:
            return Response(
                {"error": "Montant invalide (FCFA, entier positif requis)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = StripeService()
        try:
            result = service.create_payment_intent(
                amount=int(amount),
                user=request.user,
                description=description,
                metadata=request.data.get("metadata", {}),
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeSubscribeView(APIView):
    """Crée un abonnement Stripe."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        price_id = request.data.get("price_id")
        if not price_id:
            return Response(
                {"error": "price_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = StripeService()
        try:
            result = service.create_subscription(
                user=request.user,
                price_id=price_id,
                metadata=request.data.get("metadata", {}),
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeCancelView(APIView):
    """Annule un abonnement en fin de période."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription_id = request.data.get("subscription_id")
        if not subscription_id:
            return Response(
                {"error": "subscription_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = StripeService()
        try:
            result = service.cancel_subscription(subscription_id)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeSubscriptionDetailView(APIView):
    """Récupère le statut d'un abonnement."""
    permission_classes = [IsAuthenticated]

    def get(self, request, subscription_id):
        service = StripeService()
        try:
            return Response(service.retrieve_subscription(subscription_id))
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripePortalView(APIView):
    """Crée une session Stripe Customer Portal."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return_url = request.data.get("return_url", "https://avensu.tg/profile/")
        service = StripeService()
        try:
            result = service.create_portal_session(request.user, return_url)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripePlansView(APIView):
    """Liste les plans Stripe disponibles."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = StripeService()
        try:
            return Response(service.list_plans())
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeWebhookView(APIView):
    """
    Webhook Stripe — reçoit les notifications d'événements.
    ⚠️ Pas d'auth (Stripe signe les payloads).
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # désactive JWT

    def post(self, request):
        payload = request.body
        signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        service = StripeService()
        try:
            event = service.construct_webhook_event(payload, signature)
        except Exception as e:
            return Response(
                {"error": f"Signature invalide: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = service.handle_webhook_event(event)
        return Response(result, status=status.HTTP_200_OK)
