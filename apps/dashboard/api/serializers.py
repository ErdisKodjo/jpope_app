from rest_framework import serializers
from ..models import Favori, Voeu, DemarcheInscription, EvenementAgenda, ChecklistItem, ChecklistUtilisateur


class FavoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favori
        fields = "__all__"
        read_only_fields = ("id", "utilisateur", "created_at")


class VoeuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voeu
        fields = "__all__"
        read_only_fields = ("id", "utilisateur", "created_at", "updated_at")


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
