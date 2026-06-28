"""
Serializers DRF pour l'API ranking.
"""
from rest_framework import serializers

from apps.ranking.models import Classement


class ClassementListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes de classements."""
    etablissement_nom = serializers.CharField(
        source="etablissement.nom",
        read_only=True,
    )
    etablissement_ville = serializers.CharField(
        source="etablissement.ville",
        read_only=True,
    )

    class Meta:
        model = Classement
        fields = [
            "id",
            "etablissement",
            "etablissement_nom",
            "etablissement_ville",
            "annee",
            "rang_national",
            "rang_regional",
            "score_final",
            "is_published",
        ]


class ClassementDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour le détail d'un classement."""
    etablissement_nom = serializers.CharField(
        source="etablissement.nom",
        read_only=True,
    )
    etablissement_slug = serializers.SlugField(
        source="etablissement.slug",
        read_only=True,
    )
    score_formate = serializers.CharField(read_only=True)
    criteres_principaux = serializers.ListField(read_only=True)

    class Meta:
        model = Classement
        fields = [
            "id",
            "etablissement",
            "etablissement_nom",
            "etablissement_slug",
            "annee",
            "rang_national",
            "rang_regional",
            "score_final",
            "score_formate",
            "details_scores",
            "criteres_principaux",
            "methodology",
            "is_published",
            "created_at",
            "updated_at",
        ]


class ClassementCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer / mettre à jour un classement (admin/staff)."""

    class Meta:
        model = Classement
        fields = [
            "etablissement",
            "annee",
            "rang_national",
            "rang_regional",
            "score_final",
            "details_scores",
            "methodology",
            "is_published",
        ]

    def validate_score_final(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Le score final doit être compris entre 0 et 100."
            )
        return value
