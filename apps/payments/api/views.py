"""
Vues API pour l'app payments.
"""
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import logging

logger = logging.getLogger(__name__)

from apps.payments.models import (
    PlanAbonnement, Abonnement, Paiement, Facture,
)
from apps.payments.services import PaymentService

from .serializers import (
    PlanAbonnementSerializer,
    AbonnementSerializer,
    PaiementSerializer,
    FactureSerializer,
    InitierPaiementSerializer,
    VerifierStatutSerializer,
)


class PlanAbonnementViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste des plans d'abonnement disponibles."""
    serializer_class = PlanAbonnementSerializer
    permission_classes = [AllowAny]
    lookup_field = "code"

    def get_queryset(self):
        qs = PlanAbonnement.objects.filter(is_active=True, is_public=True)

        type_abonnement = self.request.query_params.get("type")
        if type_abonnement:
            qs = qs.filter(type_abonnement=type_abonnement)

        return qs.order_by("type_abonnement", "ordre", "prix_fcfa")

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Plans mis en avant."""
        plans = PlanAbonnement.objects.filter(
            is_active=True, is_public=True, is_featured=True
        ).order_by("ordre", "prix_fcfa")
        return Response(PlanAbonnementSerializer(plans, many=True).data)

    @action(detail=False, methods=["get"])
    def par_type(self, request):
        """Plans groupés par type."""
        types = [t[0] for t in PlanAbonnement.TYPE_CHOICES]
        result = {}
        for type_ab in types:
            plans = PlanAbonnement.objects.filter(
                is_active=True, is_public=True, type_abonnement=type_ab
            ).order_by("ordre", "prix_fcfa")
            result[type_ab] = PlanAbonnementSerializer(plans, many=True).data
        return Response(result)


class AbonnementListView(generics.ListAPIView):
    """Abonnements de l'utilisateur connecté."""
    serializer_class = AbonnementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Abonnement.objects.filter(
            utilisateur=self.request.user
        ).select_related("plan")


class AbonnementCourantView(APIView):
    """Abonnement actif courant de l'utilisateur."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        abonnement = Abonnement.objects.filter(
            utilisateur=request.user,
            statut__in=["ACTIF", "ESSAI"],
        ).select_related("plan").first()

        if not abonnement:
            return Response({
                "abonnement": None,
                "plan": "GRATUIT",
                "message": "Aucun abonnement actif. Plan gratuit en cours.",
            })

        return Response({
            "abonnement": AbonnementSerializer(abonnement).data,
            "jours_restants": abonnement.jours_restants,
            "est_actif": abonnement.est_actif,
        })


class InitierPaiementView(APIView):
    """Initie un paiement pour un abonnement."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InitierPaiementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Get real client IP
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        client_ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.META.get("REMOTE_ADDR", "")

        try:
            result = PaymentService.initier_paiement(
                utilisateur=request.user,
                plan_id=str(data["plan_id"]),
                methode_paiement=data["methode_paiement"],
                telephone=data.get("telephone", ""),
                metadata={
                    "ip": client_ip,
                    "user_agent": request.META.get("HTTP_USER_AGENT", "")[:200],
                    "payment_method_id": data.get("payment_method_id", ""),
                },
            )
            return Response(result, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception(f"Erreur initiation paiement: {e}")
            return Response(
                {"error": "Erreur lors de l'initiation du paiement."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifierStatutView(APIView):
    """Vérifie le statut d'une transaction."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifierStatutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reference = serializer.validated_data["reference"]

        try:
            from apps.payments.models import Paiement
            paiement = Paiement.objects.get(reference=reference)
        except Paiement.DoesNotExist:
            return Response(
                {"error": "Transaction introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Vérification de propriété
        if paiement.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "Accès non autorisé."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            result = PaymentService.verifier_statut(reference)
            return Response(result)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )


class PaiementHistoriqueView(generics.ListAPIView):
    """Historique des paiements de l'utilisateur."""
    serializer_class = PaiementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Paiement.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class FactureListView(generics.ListAPIView):
    """Factures de l'utilisateur."""
    serializer_class = FactureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Facture.objects.filter(
            utilisateur=self.request.user
        ).order_by("-date_emission")


class PaymentCallbackView(APIView):
    """Endpoint de callback pour les paiements Mobile Money (Flooz/TMoney).

    Non authentifié (appelé par le provider), mais protégé par une signature
    HMAC-SHA256 du corps brut de la requête. Le secret partagé est configuré via
    ``PAYMENT_WEBHOOK_SECRET``. Sans signature valide, le callback est rejeté :
    cela empêche un attaquant de confirmer arbitrairement des paiements.
    """
    permission_classes = [AllowAny]

    # En-têtes acceptés pour la signature (selon le provider).
    SIGNATURE_HEADERS = (
        "HTTP_X_WEBHOOK_SIGNATURE",
        "HTTP_X_SIGNATURE",
        "HTTP_X_FLOOZ_SIGNATURE",
        "HTTP_X_TMONEY_SIGNATURE",
    )

    def _get_signature(self, request):
        for header in self.SIGNATURE_HEADERS:
            value = request.META.get(header)
            if value:
                return value
        return ""

    def post(self, request):
        import json
        from apps.payments.services.utils import verify_webhook_signature

        raw_body = request.body if isinstance(request.body, bytes) else b""
        signature = self._get_signature(request)

        if not verify_webhook_signature(raw_body, signature):
            logger.warning(
                "Callback paiement rejeté : signature manquante ou invalide "
                "(ip=%s)",
                request.META.get("REMOTE_ADDR", ""),
            )
            return Response(
                {"error": "Signature invalide."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            data = json.loads(raw_body) if raw_body else request.data
        except Exception:
            data = request.data

        reference = data.get("reference") or data.get("order_id")
        transaction_id = data.get("transaction_id", "")
        statut = data.get("status", "")

        if not reference:
            return Response(
                {"error": "Référence manquante."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        statut_mappe = "PENDING"
        if str(statut).upper() in ["SUCCESSFUL", "SUCCESS", "COMPLETED", "CONFIRMED"]:
            statut_mappe = "COMPLETED"
        elif str(statut).upper() in ["FAILED", "TIMEOUT", "EXPIRED", "CANCELLED"]:
            statut_mappe = "FAILED"

        try:
            if statut_mappe == "COMPLETED":
                PaymentService.confirmer_paiement(reference, transaction_id)
                logger.info(f"Callback paiement confirmé : {reference}")
            elif statut_mappe == "FAILED":
                PaymentService.annuler_paiement(reference, f"Callback provider: {statut}")
                logger.info(f"Callback paiement échoué : {reference}")
            else:
                success = True

            return Response({"status": "ok", "reference": reference})
        except Exception as e:
            logger.error(f"Erreur callback paiement {reference}: {e}")
            return Response(
                {"error": "Erreur de traitement."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
