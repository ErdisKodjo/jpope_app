"""
Serializers DRF pour l'API analytics.
"""
from rest_framework import serializers

from apps.analytics.models import (
    PageView, SearchQuery, FormationView,
    DailyStats, KPIDefinition, KPISnapshot, Report,
)


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = [
            "id", "path", "referrer", "ip_address",
            "user_agent", "session_key", "created_at",
        ]
        read_only_fields = fields


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ["id", "query", "result_count", "created_at"]
        read_only_fields = fields


class FormationViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormationView
        fields = ["id", "formation", "duration_seconds", "created_at"]
        read_only_fields = fields


class DailyStatsSerializer(serializers.ModelSerializer):
    taux_completion_tests = serializers.FloatField(read_only=True)

    class Meta:
        model = DailyStats
        fields = "__all__"


class KPIDefinitionSerializer(serializers.ModelSerializer):
    categorie_display = serializers.CharField(
        source="get_categorie_display", read_only=True
    )

    class Meta:
        model = KPIDefinition
        fields = [
            "id", "code", "nom", "description", "formule",
            "categorie", "categorie_display", "periode",
            "unite", "icone", "couleur",
            "cible", "seuil_alerte_bas", "seuil_alerte_haut",
        ]


class KPISnapshotSerializer(serializers.ModelSerializer):
    kpi_detail = KPIDefinitionSerializer(source="kpi", read_only=True)
    atteint_cible = serializers.BooleanField(read_only=True)
    statut_alerte = serializers.CharField(read_only=True)

    class Meta:
        model = KPISnapshot
        fields = [
            "id", "kpi", "kpi_detail", "date", "periode",
            "valeur", "valeur_precedente", "variation",
            "atteint_cible", "statut_alerte",
        ]


class ReportSerializer(serializers.ModelSerializer):
    format_display = serializers.CharField(
        source="get_format_export_display", read_only=True
    )

    class Meta:
        model = Report
        fields = [
            "id", "template",
            "genere_par",
            "titre", "date_debut", "date_fin",
            "format_export", "format_display",
            "fichier", "statut",
            "nombre_telechargements",
            "created_at",
        ]
        read_only_fields = ["fichier", "statut", "nombre_telechargements"]


class TrackPageViewSerializer(serializers.Serializer):
    """Pour l'endpoint de tracking côté client."""
    path = serializers.CharField(max_length=500)
    referrer = serializers.URLField(required=False, allow_blank=True)
    session_key = serializers.CharField(max_length=100, required=False, allow_blank=True)
