"""
Vues API pour le consentement parental (rattachement parent/tuteur des mineurs).

Endpoints :
- POST /api/v1/auth/parental-consent/request/    → étudiant mineur demande le consentement
- GET  /api/v1/auth/parental-consent/<token>/    → parent consulte la demande
- POST /api/v1/auth/parental-consent/<token>/validate/  → parent valide + crée son compte
- POST /api/v1/auth/parental-consent/<token>/refuse/    → parent refuse
- GET  /api/v1/auth/parental-consent/my-children/       → parent liste ses enfants
- GET  /api/v1/auth/parental-consent/my-requests/       → étudiant liste ses demandes
"""
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.accounts.models import ConsentementParental
from apps.accounts.services.parental_consent_service import ParentalConsentService


class DemanderConsentementView(APIView):
    """Étudiant mineur demande le consentement parental."""
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        email_parent = serializers.EmailField()
        nom_parent = serializers.CharField(required=False, allow_blank=True, max_length=255)
        relation = serializers.ChoiceField(
            choices=["PERE", "MERE", "TUTEUR_LEGAL", "AUTRE"],
            default="PERE",
        )

    def post(self, request):
        ser = self.InputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        demande = ParentalConsentService.demander_consentement(
            etudiant=request.user,
            email_parent=ser.validated_data["email_parent"],
            nom_parent=ser.validated_data.get("nom_parent", ""),
            relation=ser.validated_data.get("relation", "PERE"),
        )
        return Response({
            "id": str(demande.id),
            "statut": demande.statut,
            "date_expiration": demande.date_expiration.isoformat(),
            "message": "Email envoyé au parent. Il dispose de 14 jours pour valider.",
        }, status=status.HTTP_201_CREATED)


class DetailConsentementView(APIView):
    """Parent consulte les détails d'une demande via le token."""
    permission_classes = [AllowAny]  # Pas d'auth — le token fait foi

    def get(self, request, token):
        demande = get_object_or_404(ConsentementParental, token=token)
        return Response({
            "etudiant_nom": demande.etudiant.get_full_name(),
            "etudiant_email": demande.etudiant.email,
            "parent_email_attendu": demande.email_parent,
            "relation": demande.relation,
            "statut": demande.statut,
            "date_creation": demande.date_creation.isoformat(),
            "date_expiration": demande.date_expiration.isoformat(),
            "is_expired": demande.is_expired,
        })


class ValiderConsentementView(APIView):
    """Parent valide le consentement et crée son compte."""
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        parent_email = serializers.EmailField()
        parent_first_name = serializers.CharField(max_length=150)
        parent_last_name = serializers.CharField(max_length=150)
        parent_password = serializers.CharField(min_length=10)

    def post(self, request, token):
        ser = self.InputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        demande = ParentalConsentService.valider_consentement(
            token=token,
            parent_email=ser.validated_data["parent_email"],
            parent_first_name=ser.validated_data["parent_first_name"],
            parent_last_name=ser.validated_data["parent_last_name"],
            parent_password=ser.validated_data["parent_password"],
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response({
            "message": "Consentement validé. Votre compte parent est créé.",
            "parent_email": demande.parent.email,
            "etudiant_nom": demande.etudiant.get_full_name(),
        }, status=status.HTTP_201_CREATED)


class RefuserConsentementView(APIView):
    """Parent refuse explicitement le consentement."""
    permission_classes = [AllowAny]

    def post(self, request, token):
        demande = ParentalConsentService.refuser_consentement(token)
        return Response({
            "message": "Consentement refusé. L'étudiant sera notifié.",
            "etudiant_nom": demande.etudiant.get_full_name(),
        })


class MesEnfantsView(APIView):
    """Parent liste ses enfants suivis."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "PARENT":
            return Response(
                {"error": "Réservé aux parents."},
                status=status.HTTP_403_FORBIDDEN,
            )
        demandes = ParentalConsentService.lister_enfants_suivis(request.user)
        return Response({
            "enfants": [
                {
                    "etudiant_id": str(d.etudiant.id),
                    "etudiant_nom": d.etudiant.get_full_name(),
                    "etudiant_email": d.etudiant.email,
                    "relation": d.relation,
                    "date_validation": d.date_validation.isoformat(),
                }
                for d in demandes
            ]
        })


class MesDemandesConsentementView(APIView):
    """Étudiant liste ses demandes de consentement."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        demandes = ConsentementParental.objects.filter(
            etudiant=request.user
        ).order_by("-date_creation")
        return Response({
            "demandes": [
                {
                    "id": str(d.id),
                    "email_parent": d.email_parent,
                    "statut": d.statut,
                    "date_creation": d.date_creation.isoformat(),
                    "date_validation": d.date_validation.isoformat() if d.date_validation else None,
                }
                for d in demandes
            ]
        })
