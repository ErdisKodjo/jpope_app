"""Admin de la bibliothèque."""
from django.contrib import admin
from apps.library.models import (
    RessourcePedagogique, CategorieBibliotheque,
    TelechargementRessource, FavoriBibliotheque, VoteRessource,
)


class CategorieBibliothequeAdmin(admin.ModelAdmin):
    list_display = ("nom", "parent", "ordre", "is_active")
    list_filter = ("is_active", "parent")
    search_fields = ("nom",)
    ordering = ("ordre", "nom")


@admin.register(RessourcePedagogique)
class RessourcePedagogiqueAdmin(admin.ModelAdmin):
    list_display = ("titre", "type", "matiere", "niveaux", "is_premium",
                    "is_free", "is_verified", "nombre_telechargements", "note_moyenne")
    list_filter = ("type", "is_premium", "is_free", "is_verified", "is_active")
    search_fields = ("titre", "auteur", "editeur", "matiere")
    readonly_fields = ("slug", "fichier_taille_mo", "nombre_telechargements",
                       "nombre_vues", "note_moyenne", "nombre_votes")


admin.site.register(CategorieBibliotheque, CategorieBibliothequeAdmin)
admin.site.register(TelechargementRessource)
admin.site.register(FavoriBibliotheque)
admin.site.register(VoteRessource)
