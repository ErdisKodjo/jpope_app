"""
Vues API pour le simulateur d'admissions prédictif.

Endpoints :
- POST /api/v1/catalog/simulateur/admission/    → lance une simulation
- GET  /api/v1/catalog/simulateur/historique/   → historique des simulations de l'utilisateur
- GET  /api/v1/catalog/etablissements/<id>/visite-3d/  → données de visite virtuelle
"""
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Formation, Etablissement, ResultatSimulateur
from apps.catalog.services.admission_simulator_service import SimulateurAdmissionService


class SimulateurAdmissionSerializer(serializers.Serializer):
    formation_id = serializers.UUIDField()
    moyenne = serializers.FloatField(min_value=0, max_value=20)
    serie_bac = serializers.CharField(required=False, allow_blank=True, max_length=10)


class SimulateurAdmissionView(APIView):
    """Lance une simulation d'admission prédictive."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = SimulateurAdmissionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            formation = Formation.objects.get(pk=ser.validated_data["formation_id"])
        except Formation.DoesNotExist:
            return Response(
                {"error": "Formation introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        resultat = SimulateurAdmissionService.simuler(
            etudiant=request.user,
            formation=formation,
            moyenne_saisie=ser.validated_data["moyenne"],
            serie_bac_saisie=ser.validated_data.get("serie_bac", ""),
        )

        return Response({
            "id": str(resultat.id),
            "formation": {
                "id": str(formation.id),
                "nom": formation.nom,
                "etablissement": str(formation.etablissement),
            },
            "moyenne_saisie": resultat.moyenne_saisie,
            "serie_bac_saisie": resultat.serie_bac_saisie,
            "pourcentage_chances": resultat.pourcentage_chances,
            "niveau_confiance": resultat.niveau_confiance,
            "explication": resultat.explication,
            "recommandations": resultat.recommandations,
            "date_simulation": resultat.date_simulation.isoformat(),
        }, status=status.HTTP_201_CREATED)


class SimulateurHistoriqueView(generics.ListAPIView):
    """Historique des simulations de l'utilisateur courant."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        simulations = ResultatSimulateur.objects.filter(etudiant=request.user).order_by("-date_simulation")[:50]
        return Response({
            "simulations": [
                {
                    "id": str(s.id),
                    "formation": s.formation.nom,
                    "etablissement": str(s.formation.etablissement),
                    "moyenne_saisie": s.moyenne_saisie,
                    "pourcentage_chances": s.pourcentage_chances,
                    "niveau_confiance": s.niveau_confiance,
                    "date_simulation": s.date_simulation.isoformat(),
                }
                for s in simulations
            ]
        })


class VisiteVirtuelle3DView(APIView):
    """
    Récupère les données de visite virtuelle 3D d'un établissement.
    Permet au frontend d'afficher le lecteur immersif (Matterport, Sketchfab, 360°).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        etablissement = get_object_or_404(Etablissement, pk=pk, is_active=True)
        return Response({
            "etablissement": {
                "id": str(etablissement.id),
                "nom": etablissement.nom,
            },
            "visite_virtuelle_url": etablissement.visite_virtuelle_url,
            "galerie_3d": etablissement.galerie_3d or [],
            "video_presentation_url": etablissement.video_presentation_url,
            "ateliers_virtuels_disponibles": etablissement.ateliers_virtuels_disponibles,
            "banniere": etablissement.banniere.url if etablissement.banniere else None,
            "logo": etablissement.logo.url if etablissement.logo else None,
        })
