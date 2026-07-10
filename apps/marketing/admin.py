"""Admin marketing."""
from django.contrib import admin
from apps.marketing.models import (
    SegmentCandidats, CampagneMarketing, LeadQualifie,
    CandidatureCRM, LogInteractionCRM,
)


@admin.register(SegmentCandidats)
class SegmentCandidatsAdmin(admin.ModelAdmin):
    list_display = ("nom", "moyenne_min", "moyenne_max", "created_at")
    list_filter = ("niveau_actuel",)
    search_fields = ("nom", "description")


@admin.register(CampagneMarketing)
class CampagneMarketingAdmin(admin.ModelAdmin):
    list_display = ("nom", "etablissement", "statut", "date_debut", "date_fin",
                    "vues", "clics", "leads_generes", "conversions")
    list_filter = ("statut", "etablissement")
    search_fields = ("nom", "etablissement__nom")
    date_hierarchy = "date_debut"


@admin.register(LeadQualifie)
class LeadQualifieAdmin(admin.ModelAdmin):
    list_display = ("candidat", "campagne", "score_matching", "statut", "is_facture", "date_generation")
    list_filter = ("statut", "is_facture", "campagne")
    search_fields = ("candidat__email", "campagne__nom")


@admin.register(CandidatureCRM)
class CandidatureCRMAdmin(admin.ModelAdmin):
    list_display = ("candidat", "etablissement", "formation", "statut",
                    "date_reception", "date_decision", "is_synced_external")
    list_filter = ("statut", "is_synced_external", "etablissement")
    search_fields = ("candidat__email", "etablissement__nom", "external_application_id")
    date_hierarchy = "date_reception"


@admin.register(LogInteractionCRM)
class LogInteractionCRMAdmin(admin.ModelAdmin):
    list_display = ("candidature", "type", "auteur", "sujet", "date_interaction", "is_automatique")
    list_filter = ("type", "is_automatique")
    search_fields = ("sujet", "contenu")
    date_hierarchy = "date_interaction"
