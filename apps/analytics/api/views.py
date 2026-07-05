"""
Vues API pour l'app analytics.
"""
from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.analytics.models import (
    PageView, DailyStats, KPIDefinition, KPISnapshot,
)

from .serializers import (
    DailyStatsSerializer,
    KPIDefinitionSerializer,
    KPISnapshotSerializer,
    TrackPageViewSerializer,
)


class TrackPageViewAPIView(APIView):
    """Endpoint de tracking côté client (page views)."""
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = TrackPageViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        PageView.objects.create(
            utilisateur=request.user if request.user.is_authenticated else None,
            path=data["path"],
            referrer=data.get("referrer", ""),
            ip_address=self._get_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            session_key=data.get("session_key", ""),
        )
        return Response({"tracked": True}, status=status.HTTP_201_CREATED)

    def _get_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class DailyStatsListView(generics.ListAPIView):
    """Liste des statistiques quotidiennes."""
    serializer_class = DailyStatsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        jours = int(self.request.query_params.get("jours", 30))
        seuil = timezone.now().date() - timedelta(days=jours)
        return DailyStats.objects.filter(date__gte=seuil).order_by("-date")


class KPIListView(generics.ListAPIView):
    """Liste des KPIs disponibles."""
    serializer_class = KPIDefinitionSerializer
    permission_classes = [IsAuthenticated]
    queryset = KPIDefinition.objects.filter(is_active=True)


class KPIEvolutionView(APIView):
    """Évolution d'un KPI sur une période."""
    permission_classes = [IsAuthenticated]

    def get(self, request, kpi_code):
        jours = int(request.query_params.get("jours", 30))
        date_fin = timezone.now().date()
        date_debut = date_fin - timedelta(days=jours)

        try:
            kpi = KPIDefinition.objects.get(code=kpi_code, is_active=True)
        except KPIDefinition.DoesNotExist:
            return Response(
                {"error": f"KPI '{kpi_code}' introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        snapshots = KPISnapshot.objects.filter(
            kpi=kpi,
            date__gte=date_debut,
            date__lte=date_fin,
        ).order_by("date")

        return Response({
            "kpi": KPIDefinitionSerializer(kpi).data,
            "evolution": KPISnapshotSerializer(snapshots, many=True).data,
        })


class DashboardSummaryView(APIView):
    """Résumé du dashboard (stats 30 derniers jours)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jours = int(request.query_params.get("jours", 30))
        date_fin = timezone.now().date()
        date_debut = date_fin - timedelta(days=jours)

        stats = DailyStats.objects.filter(
            date__gte=date_debut,
            date__lte=date_fin,
        )

        totaux = {
            "pages_vues": sum(s.pages_vues for s in stats),
            "nouveaux_utilisateurs": sum(s.nouveaux_utilisateurs for s in stats),
            "tests_completes": sum(s.tests_completes for s in stats),
            "revenus_fcfa": float(sum(s.revenus_fcfa for s in stats)),
            "paiements_reussis": sum(s.paiements_reussis for s in stats),
            "periode_jours": jours,
            "date_debut": str(date_debut),
            "date_fin": str(date_fin),
        }

        return Response(totaux)
