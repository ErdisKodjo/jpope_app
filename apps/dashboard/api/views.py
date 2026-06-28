from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Favori, Voeu, DemarcheInscription, EvenementAgenda, ChecklistUtilisateur
from .serializers import (
    FavoriSerializer, VoeuSerializer, DemarcheSerializer,
    EvenementAgendaSerializer, ChecklistUtilisateurSerializer,
)


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "favoris_count": Favori.objects.filter(utilisateur=user).count(),
            "voeux_count": Voeu.objects.filter(etudiant=user).count(),
            "demarches_count": DemarcheInscription.objects.filter(etudiant=user).count(),
        })


class FavoriListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favori.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)


class VoeuListCreateView(generics.ListCreateAPIView):
    serializer_class = VoeuSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Voeu.objects.filter(etudiant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(etudiant=self.request.user)


class DemarcheListCreateView(generics.ListCreateAPIView):
    serializer_class = DemarcheSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DemarcheInscription.objects.filter(etudiant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(etudiant=self.request.user)


class AgendaListCreateView(generics.ListCreateAPIView):
    serializer_class = EvenementAgendaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EvenementAgenda.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
