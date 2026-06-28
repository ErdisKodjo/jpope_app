from django.contrib import admin
from .models import Favori, Voeu, DemarcheInscription, EvenementAgenda, ChecklistItem, ChecklistUtilisateur


@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display = ["utilisateur", "type_entite", "created_at"]
    list_filter = ["type_entite"]
    search_fields = ["utilisateur__email"]


@admin.register(Voeu)
class VoeuAdmin(admin.ModelAdmin):
    list_display = ["etudiant", "formation", "statut", "priorite", "created_at"]
    list_filter = ["statut", "niveau_priorite"]
    search_fields = ["etudiant__email"]


@admin.register(DemarcheInscription)
class DemarcheAdmin(admin.ModelAdmin):
    list_display = ["etudiant", "titre", "type", "statut", "created_at"]
    list_filter = ["type", "statut"]
    search_fields = ["etudiant__email", "titre"]


@admin.register(EvenementAgenda)
class EvenementAgendaAdmin(admin.ModelAdmin):
    list_display = ["utilisateur", "titre", "date_debut"]
    search_fields = ["utilisateur__email", "titre"]


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ["titre", "ordre", "is_active"]
    list_filter = ["is_active"]


@admin.register(ChecklistUtilisateur)
class ChecklistUtilisateurAdmin(admin.ModelAdmin):
    list_display = ["utilisateur", "item", "est_fait"]
    list_filter = ["est_fait"]
