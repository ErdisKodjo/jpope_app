"""Vues API de la roadmap évolutive."""
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.roadmap.models import (
    EtapeRoadmap, EtapePersonnelleEtudiant, JalonRoadmap,
    PhaseRoadmap, StatutEtape, CategorieEtape,
)
from apps.roadmap.services import RoadmapService


class EtapePersonnelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtapePersonnelleEtudiant
        fields = [
            "id", "phase", "categorie", "titre", "description", "ordre",
            "statut", "date_debut", "date_objectif", "date_completion",
            "notes_personnelles", "conseiller", "etape_generique",
        ]
        read_only_fields = ["id", "date_creation", "date_debut", "date_completion", "conseiller"]


class JalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = JalonRoadmap
        fields = [
            "id", "nom", "description", "phase", "date_evenement",
            "is_national", "pays", "ville", "url_inscription",
        ]


class RoadmapProgressionView(APIView):
    """Progression de l'étudiant par phase."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        progression = RoadmapService.progression_etudiant(request.user)
        return Response({
            "progression": progression,
            "phase_actuelle": RoadmapService.determiner_phase_etudiant(request.user),
        })


class RoadmapInitView(APIView):
    """Initialise la roadmap de l'étudiant (génère les étapes par défaut)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phase = request.data.get("phase")
        if phase and phase not in PhaseRoadmap.values:
            return Response({"error": "Phase invalide."}, status=status.HTTP_400_BAD_REQUEST)
        creees = RoadmapService.initialiser_roadmap_etudiant(request.user, phase=phase)
        return Response({
            "message": f"{len(creees)} nouvelles étapes créées.",
            "etape_ids": [str(e.id) for e in creees],
        }, status=status.HTTP_201_CREATED)


class MesEtapesListView(generics.ListCreateAPIView):
    """Liste et crée des étapes personnelles."""
    serializer_class = EtapePersonnelleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = EtapePersonnelleEtudiant.objects.filter(etudiant=self.request.user)
        phase = self.request.query_params.get("phase")
        statut = self.request.query_params.get("statut")
        if phase:
            qs = qs.filter(phase=phase)
        if statut:
            qs = qs.filter(statut=statut)
        return qs.order_by("phase", "ordre", "date_objectif")

    def perform_create(self, serializer):
        serializer.save(etudiant=self.request.user)


class EtapeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail / update / delete d'une étape personnelle."""
    serializer_class = EtapePersonnelleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EtapePersonnelleEtudiant.objects.filter(etudiant=self.request.user)


class EtapeActionView(APIView):
    """Actions rapides sur une étape : complete / start / block."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        from django.shortcuts import get_object_or_404
        etape = get_object_or_404(
            EtapePersonnelleEtudiant, pk=pk, etudiant=request.user
        )
        if action == "complete":
            etape.marquer_complete()
        elif action == "start":
            etape.marquer_en_cours()
        elif action == "block":
            etape.statut = StatutEtape.BLOQUE
            etape.save(update_fields=["statut"])
        elif action == "reset":
            etape.statut = StatutEtape.NON_COMMENCE
            etape.date_debut = None
            etape.date_completion = None
            etape.save(update_fields=["statut", "date_debut", "date_completion"])
        else:
            return Response({"error": "Action invalide."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EtapePersonnelleSerializer(etape).data)


class JalonsAvenirView(generics.ListAPIView):
    """Jalons à venir (nationaux + personnels)."""
    serializer_class = JalonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        days = int(self.request.query_params.get("days", 90))
        return RoadmapService.jalons_a_venir(self.request.user, days_ahead=days)


class EtapesAvenirView(APIView):
    """Étapes non complétées triées par date objectif."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        etapes = RoadmapService.etapes_a_venir(request.user, limit=limit)
        return Response({
            "etapes": EtapePersonnelleSerializer(etapes, many=True).data,
        })
