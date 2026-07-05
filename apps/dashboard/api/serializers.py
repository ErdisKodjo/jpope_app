from rest_framework import serializers
from ..models import Favori, Voeu, DemarcheInscription, EvenementAgenda, ChecklistItem, ChecklistUtilisateur


class FavoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favori
        exclude = ("utilisateur",)
        read_only_fields = ("id", "created_at")


class VoeuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voeu
        fields = [
            "id", "formation", "priorite", "niveau_priorite", "statut",
            "lettre_motivation", "notes_etudiant", "date_soumission",
            "date_reponse", "numero_candidature", "commentaire_etablissement",
            "motif_refus", "est_principal", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "date_soumission", "date_reponse", "numero_candidature",
            "commentaire_etablissement", "motif_refus", "created_at", "updated_at",
        ]


class DemarcheSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemarcheInscription
        fields = "__all__"
        read_only_fields = ("id", "utilisateur", "created_at", "updated_at")


class EvenementAgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvenementAgenda
        fields = "__all__"
        read_only_fields = ("id", "utilisateur", "created_at")


class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = "__all__"


class ChecklistUtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistUtilisateur
        fields = "__all__"
        read_only_fields = ("id", "utilisateur", "created_at", "updated_at")
