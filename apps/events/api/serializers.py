"""
Serializers DRF pour l'API events.
"""
from rest_framework import serializers

from apps.events.models import Evenement, InscriptionEvenement


class EvenementListSerializer(serializers.ModelSerializer):
    """Serializer pour les listes d'événements."""
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    format_display = serializers.CharField(source="get_format_display", read_only=True)
    organisateur_nom = serializers.CharField(read_only=True)
    jours_avant = serializers.IntegerField(read_only=True)
    places_restantes = serializers.IntegerField(read_only=True)
    est_complet = serializers.BooleanField(read_only=True)
    inscriptions_encore_ouvertes = serializers.BooleanField(read_only=True)

    class Meta:
        model = Evenement
        fields = [
            "id",
            "titre",
            "slug",
            "description_courte",
            "image_principale",
            "type",
            "type_display",
            "format",
            "format_display",
            "statut",
            "date_debut",
            "date_fin",
            "lieu_nom",
            "ville",
            "pays",
            "organisateur_nom",
            "est_gratuit",
            "cout_participation",
            "capacite_max",
            "nombre_inscrits",
            "places_restantes",
            "est_complet",
            "inscriptions_ouvertes",
            "inscriptions_encore_ouvertes",
            "is_featured",
            "jours_avant",
            "nombre_vues",
        ]


class EvenementDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé d'un événement."""
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    format_display = serializers.CharField(source="get_format_display", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    cible_display = serializers.CharField(source="get_cible_display", read_only=True)
    organisateur_nom = serializers.CharField(read_only=True)
    jours_avant = serializers.IntegerField(read_only=True)
    places_restantes = serializers.IntegerField(read_only=True)
    est_complet = serializers.BooleanField(read_only=True)
    est_a_venir = serializers.BooleanField(read_only=True)
    est_en_cours = serializers.BooleanField(read_only=True)
    est_passe = serializers.BooleanField(read_only=True)
    inscriptions_encore_ouvertes = serializers.BooleanField(read_only=True)
    taux_remplissage = serializers.FloatField(read_only=True)
    duree_formatee = serializers.CharField(read_only=True)
    domaines_concernes = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "titre",
            "slug",
            "description",
            "description_courte",
            "image_principale",
            "image_couverture",
            "galerie_images",
            "type",
            "type_display",
            "format",
            "format_display",
            "statut",
            "statut_display",
            "cible",
            "cible_display",
            "priorite",
            "date_debut",
            "date_fin",
            "date_limite_inscription",
            "duree_formatee",
            "lieu_nom",
            "adresse",
            "ville",
            "pays",
            "latitude",
            "longitude",
            "lien_visio",
            "plateforme_visio",
            "est_gratuit",
            "cout_participation",
            "informations_tarifs",
            "capacite_max",
            "nombre_inscrits",
            "places_restantes",
            "est_complet",
            "taux_remplissage",
            "inscriptions_ouvertes",
            "inscriptions_encore_ouvertes",
            "programme",
            "intervenants",
            "tags",
            "domaines_concernes",
            "email_contact",
            "telephone_contact",
            "site_web",
            "reseaux_sociaux",
            "etablissement",
            "organisateur_nom",
            "is_featured",
            "nombre_vues",
            "nombre_partages",
            "jours_avant",
            "est_a_venir",
            "est_en_cours",
            "est_passe",
            "created_at",
        ]

    def get_domaines_concernes(self, obj):
        return [
            {"id": str(d.id), "nom": d.nom}
            for d in obj.domaines_concernes.all()
        ]


class InscriptionEvenementSerializer(serializers.ModelSerializer):
    """Serializer d'inscription à un événement."""
    utilisateur_nom = serializers.CharField(
        source="utilisateur.get_full_name", read_only=True
    )
    evenement_titre = serializers.CharField(
        source="evenement.titre", read_only=True
    )
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)

    class Meta:
        model = InscriptionEvenement
        fields = [
            "id",
            "utilisateur",
            "utilisateur_nom",
            "evenement",
            "evenement_titre",
            "statut",
            "statut_display",
            "date_inscription",
            "date_confirmation",
            "nombre_accompagnants",
            "besoins_speciaux",
            "source_inscription",
            "a_participe",
            "date_checkin",
            "feedback",
            "note_satisfaction",
        ]
        read_only_fields = [
            "id", "utilisateur", "date_inscription",
            "date_confirmation", "a_participe", "date_checkin",
        ]


class InscriptionCreateSerializer(serializers.Serializer):
    """Serializer pour créer une inscription."""
    evenement_id = serializers.UUIDField()
    nombre_accompagnants = serializers.IntegerField(default=0, min_value=0)
    besoins_speciaux = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, default="site_web")


class FeedbackSerializer(serializers.Serializer):
    """Serializer pour le feedback post-événement."""
    feedback = serializers.CharField()
    note_satisfaction = serializers.IntegerField(min_value=1, max_value=5)
