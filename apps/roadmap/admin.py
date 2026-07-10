"""Admin roadmap."""
from django.contrib import admin
from apps.roadmap.models import EtapeRoadmap, EtapePersonnelleEtudiant, JalonRoadmap


@admin.register(EtapeRoadmap)
class EtapeRoadmapAdmin(admin.ModelAdmin):
    list_display = ("phase", "categorie", "titre", "ordre", "is_active", "is_obligatoire")
    list_filter = ("phase", "categorie", "is_active", "is_obligatoire")
    search_fields = ("titre", "description")
    ordering = ("phase", "ordre")


@admin.register(EtapePersonnelleEtudiant)
class EtapePersonnelleEtudiantAdmin(admin.ModelAdmin):
    list_display = ("etudiant", "phase", "titre", "statut", "date_objectif", "date_completion")
    list_filter = ("phase", "statut")
    search_fields = ("etudiant__email", "titre")
    date_hierarchy = "date_creation"


@admin.register(JalonRoadmap)
class JalonRoadmapAdmin(admin.ModelAdmin):
    list_display = ("nom", "phase", "date_evenement", "is_national", "is_annuel")
    list_filter = ("phase", "is_national", "is_annuel")
    search_fields = ("nom", "ville", "pays")
    date_hierarchy = "date_evenement"
