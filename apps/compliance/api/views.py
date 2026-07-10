"""
Vues API pour la conformité RGPD.

Endpoints :
- GET  /api/v1/rgpd/consentements/                  → liste mes consentements
- POST /api/v1/rgpd/consentements/                  → donner un consentement
- DELETE /api/v1/rgpd/consentements/<type>/         → retirer un consentement
- GET  /api/v1/rgpd/demandes/                       → mes demandes RGPD
- POST /api/v1/rgpd/demandes/                       → créer une demande
- GET  /api/v1/rgpd/export/                         → export complet (art. 15 + 20)
- POST /api/v1/rgpd/droit-oubli/                    → déclenche l'anonymisation (art. 17)
- GET  /api/v1/rgpd/journal/                        → journal des accès à mes données
- GET  /api/v1/rgpd/politiques/                     → politiques de conservation
"""
import io
import zipfile
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.compliance.models import (
    ConsentementRGPD, DemandeRGPD, JournalTraitement, PolitiqueConservation,
    TypeConsentement, TypeDemandeRGPD, StatutDemandeRGPD,
)
from apps.compliance.services import RGPDService


# ─── Serializers inline (légers) ───

from rest_framework import serializers


class ConsentementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentementRGPD
        fields = ["id", "type", "statut", "texte_consentement", "version_politique",
                  "date_consentement", "date_retrait"]
        read_only_fields = ["id", "statut", "date_consentement", "date_retrait"]


class CreerConsentementSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=TypeConsentement.choices)
    texte_consentement = serializers.CharField()
    version_politique = serializers.CharField(required=False, default="1.0")


class DemandeRGPDSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeRGPD
        fields = ["id", "reference", "type", "statut", "motif", "motif_refus",
                  "date_creation", "date_traitement", "date_limite"]
        read_only_fields = ["id", "reference", "statut", "motif_refus",
                            "date_creation", "date_traitement", "date_limite"]


class JournalTraitementSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalTraitement
        fields = ["id", "timestamp", "acteur", "action", "categorie_donnee",
                  "details", "ip_address"]


class PolitiqueConservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolitiqueConservation
        fields = ["id", "categorie", "duree_conservation_jours", "description", "is_active"]


# ─── Vues ───

class MesConsentementsView(generics.ListCreateAPIView):
    """Liste et crée des consentements RGPD pour l'utilisateur courant."""
    permission_classes = [IsAuthenticated]
    serializer_class = ConsentementSerializer

    def get_queryset(self):
        return ConsentementRGPD.objects.filter(utilisateur=self.request.user)

    def create(self, request, *args, **kwargs):
        ser = CreerConsentementSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        consentement = RGPDService.donner_consentement(
            utilisateur=request.user,
            type_consentement=ser.validated_data["type"],
            texte=ser.validated_data["texte_consentement"],
            version_politique=ser.validated_data.get("version_politique", "1.0"),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
        )
        return Response(ConsentementSerializer(consentement).data, status=status.HTTP_201_CREATED)


class RetirerConsentementView(APIView):
    """Retire un consentement actif par type."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, type_consentement):
        if type_consentement not in [c[0] for c in TypeConsentement.choices]:
            return Response({"error": "Type de consentement invalide."},
                            status=status.HTTP_400_BAD_REQUEST)
        count = RGPDService.retirer_consentement(request.user, type_consentement)
        return Response({"retires": count}, status=status.HTTP_200_OK)


class MesDemandesRGPDView(generics.ListCreateAPIView):
    """Liste et crée des demandes RGPD pour l'utilisateur courant."""
    permission_classes = [IsAuthenticated]
    serializer_class = DemandeRGPDSerializer

    def get_queryset(self):
        return DemandeRGPD.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)


class ExportDonneesView(APIView):
    """
    Déclenche un export complet des données personnelles (art. 15 + 20 RGPD).
    Retourne un fichier ZIP téléchargeable.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        zip_bytes = RGPDService.exporter_donnees_utilisateur(request.user, demandeur=request.user)
        response = HttpResponse(zip_bytes, content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="export-rgpd-{request.user.id}.zip"'
        )
        return response


class DroitOubliView(APIView):
    """
    Déclenche le droit à l'oubli (art. 17 RGPD).
    Anonymise toutes les données de l'utilisateur — IRRÉVERSIBLE.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Vérifie une confirmation explicite
        if request.data.get("confirm") != "JE_CONFIRME_EFFACEMENT_IRREVERSIBLE":
            return Response(
                {
                    "error": "Confirmation requise",
                    "hint": "Ajoutez {\"confirm\": \"JE_CONFIRME_EFFACEMENT_IRREVERSIBLE\"} dans le corps.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crée d'abord la demande pour traçabilité
        demande = RGPDService.creer_demande(
            utilisateur=request.user,
            type_demande=TypeDemandeRGPD.EFFACEMENT,
            motif="Demande utilisateur via API",
        )
        # Traite immédiatement (en prod : Celery async)
        RGPDService.traiter_demande(demande, traite_par=request.user)

        return Response(
            {
                "message": "Votre compte a été anonymisé. Toutes vos données personnelles ont été effacées.",
                "reference": demande.reference,
            },
            status=status.HTTP_200_OK,
        )


class JournalAccesView(generics.ListAPIView):
    """Journal des accès aux données de l'utilisateur courant."""
    permission_classes = [IsAuthenticated]
    serializer_class = JournalTraitementSerializer

    def get_queryset(self):
        return JournalTraitement.objects.filter(cible=self.request.user)[:200]


class PolitiquesConservationView(generics.ListAPIView):
    """Liste publique des politiques de conservation."""
    permission_classes = [IsAuthenticated]
    serializer_class = PolitiqueConservationSerializer
    queryset = PolitiqueConservation.objects.filter(is_active=True)
