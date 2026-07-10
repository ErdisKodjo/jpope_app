"""Admin compliance."""
from django.contrib import admin

from apps.compliance.models import (
    ConsentementRGPD, DemandeRGPD, JournalTraitement, PolitiqueConservation,
)


@admin.register(ConsentementRGPD)
class ConsentementRGPDAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "type", "statut", "date_consentement", "date_retrait", "version_politique")
    list_filter = ("type", "statut", "version_politique")
    search_fields = ("utilisateur__email",)
    date_hierarchy = "date_consentement"
    readonly_fields = ("date_consentement", "date_retrait")


@admin.register(DemandeRGPD)
class DemandeRGPDAdmin(admin.ModelAdmin):
    list_display = ("reference", "utilisateur", "type", "statut", "date_creation", "date_limite", "date_traitement")
    list_filter = ("type", "statut")
    search_fields = ("reference", "utilisateur__email")
    date_hierarchy = "date_creation"
    readonly_fields = ("reference", "date_creation", "date_limite", "date_traitement")


@admin.register(JournalTraitement)
class JournalTraitementAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "acteur", "cible", "action", "categorie_donnee")
    list_filter = ("action", "categorie_donnee")
    search_fields = ("acteur__email", "cible__email")
    date_hierarchy = "timestamp"
    readonly_fields = ("timestamp",)


@admin.register(PolitiqueConservation)
class PolitiqueConservationAdmin(admin.ModelAdmin):
    list_display = ("categorie", "duree_conservation_jours", "is_active")
    list_filter = ("is_active",)
