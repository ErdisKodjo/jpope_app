"""
Vues API pour l'app ranking.
"""
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.ranking.models import Classement
from .serializers import (
    ClassementListSerializer,
    ClassementDetailSerializer,
    ClassementCreateUpdateSerializer,
)


class ClassementViewSet(viewsets.ModelViewSet):
    """
    CRUD des classements.
    Lecture publique — écriture réservée aux admins.
    """
    queryset = Classement.objects.select_related("etablissement")

    def get_queryset(self):
        qs = super().get_queryset()
        # Les non-admins ne voient que les classements publiés
        if not self.request.user.is_staff:
            qs = qs.filter(is_published=True)

        # Filtre par année
        annee = self.request.query_params.get("annee")
        if annee:
            qs = qs.filter(annee=annee)

        # Filtre par établissement
        etablissement_id = self.request.query_params.get("etablissement")
        if etablissement_id:
            qs = qs.filter(etablissement_id=etablissement_id)

        return qs.order_by("rang_national", "-score_final")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ClassementCreateUpdateSerializer
        if self.action == "retrieve":
            return ClassementDetailSerializer
        return ClassementListSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=["get"])
    def top_national(self, request):
        """Top 20 des établissements au classement national pour l'année la plus récente."""
        annee = request.query_params.get("annee")

        qs = Classement.objects.filter(is_published=True, rang_national__isnull=False)

        if annee:
            qs = qs.filter(annee=annee)
        else:
            # Prendre l'année la plus récente disponible
            derniere_annee = (
                qs.order_by("-annee").values_list("annee", flat=True).first()
            )
            if derniere_annee:
                qs = qs.filter(annee=derniere_annee)

        qs = qs.select_related("etablissement").order_by("rang_national")[:20]
        serializer = ClassementListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def annees_disponibles(self, request):
        """Retourne la liste des années disponibles dans les classements publiés."""
        annees = (
            Classement.objects.filter(is_published=True)
            .values_list("annee", flat=True)
            .distinct()
            .order_by("-annee")
        )
        return Response(list(annees))
