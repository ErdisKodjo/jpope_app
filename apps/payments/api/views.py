"""
Vues API pour l'app payments.
"""
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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
        )
        return Response(PlanAbonnementSerializer(plans, many=True).data)

    @action(detail=False, methods=["get"])
    def par_type(self, request):
        """Plans groupés par type."""
        types = ["ETUDIANT", "CONSEILLER", "ETABLISSEMENT"]
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

        try:
            result = PaymentService.initier_paiement(
                utilisateur=request.user,
                plan_id=str(data["plan_id"]),
                methode_paiement=data["methode_paiement"],
                telephone=data.get("telephone", ""),
                metadata={
                    "ip": request.META.get("REMOTE_ADDR", ""),
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
