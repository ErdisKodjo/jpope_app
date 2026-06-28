"""
Admin Django pour l'app analytics.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    PageView, SearchQuery, FormationView, ActionLog,
    DailyStats, KPIDefinition, KPISnapshot, ReportTemplate, Report,
)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ["path", "utilisateur", "ip_address", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["path", "utilisateur__email", "ip_address"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["query", "utilisateur", "result_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["query", "utilisateur__email"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(FormationView)
class FormationViewAdmin(admin.ModelAdmin):
    list_display = ["formation", "utilisateur", "duration_seconds", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["formation__nom", "utilisateur__email"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ["type_action", "utilisateur", "entite_type", "created_at"]
    list_filter = ["type_action", "created_at"]
    search_fields = ["utilisateur__email"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = [
        "date", "nouveaux_utilisateurs", "utilisateurs_actifs",
        "pages_vues", "paiements_reussis", "revenus_fcfa",
    ]
    list_filter = ["date"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "date"


@admin.register(KPIDefinition)
class KPIDefinitionAdmin(admin.ModelAdmin):
    list_display = ["icone", "nom", "categorie", "periode", "cible", "is_active"]
    list_filter = ["categorie", "periode", "is_active"]
    search_fields = ["code", "nom", "description"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(KPISnapshot)
class KPISnapshotAdmin(admin.ModelAdmin):
    list_display = ["kpi", "date", "periode", "valeur", "variation"]
    list_filter = ["periode", "date"]
    search_fields = ["kpi__nom", "kpi__code"]
    readonly_fields = ["created_at"]
    date_hierarchy = "date"


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ["code", "nom", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["code", "nom"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "titre", "template", "genere_par", "format_export",
        "statut", "nombre_telechargements", "created_at",
    ]
    list_filter = ["format_export", "statut", "created_at"]
    search_fields = ["titre", "genere_par__email"]
    readonly_fields = ["created_at", "updated_at", "nombre_telechargements"]
    date_hierarchy = "created_at"
