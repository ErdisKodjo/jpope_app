"""
Admin Django pour l'app orientation.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    TestOrientation, Question, Choice,
    ReponseUtilisateur, DetailReponse,
    ResultatTest, Recommandation,
)

# ──────────────────────────────────────────────
# Question & Choice (inlines)
# ──────────────────────────────────────────────

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ["texte", "ordre", "scores", "is_active"]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["ordre", "texte_court", "test", "type", "poids", "is_active"]
    list_filter = ["test", "type", "is_active"]
    search_fields = ["texte"]
    inlines = [ChoiceInline]

# ──────────────────────────────────────────────
# Test d'orientation
# ──────────────────────────────────────────────

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ["texte", "type", "ordre", "poids", "dimensions", "is_active"]
    show_change_link = True

@admin.register(TestOrientation)
class TestOrientationAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "type",
        "nombre_questions",
        "duree_estimee_minutes",
        "nombre_passations",
        "taux_completion",
        "is_active",
        "is_featured",
    ]
    list_filter = ["type", "is_active", "is_featured"]
    search_fields = ["nom", "description"]
    prepopulated_fields = {"slug": ("nom",)}
    inlines = [QuestionInline]
    readonly_fields = ["nombre_questions", "nombre_passations", "taux_completion"]

    fieldsets = (
        (None, {
            "fields": ("nom", "slug", "description", "description_courte", "type"),
        }),
        (_("Configuration"), {
            "fields": (
                "duree_estimee_minutes",
                "dimensions_evaluees",
                "methode_scoring",
                "niveau_minimum",
                "age_minimum",
            ),
        }),
        (_("Statistiques"), {
            "fields": ("nombre_questions", "nombre_passations", "taux_completion", "score_moyen"),
        }),
        (_("Métadonnées"), {
            "fields": (
                "auteur", "version", "date_publication", "source_scientifique",
                "is_active", "is_public", "is_featured", "ordre",
            ),
        }),
    )

# ──────────────────────────────────────────────
# Réponses et résultats
# ──────────────────────────────────────────────

@admin.register(ReponseUtilisateur)
class ReponseUtilisateurAdmin(admin.ModelAdmin):
    list_display = [
        "etudiant",
        "test",
        "statut",
        "progression",
        "code_holland",
        "score_global",
        "date_debut",
    ]
    list_filter = ["statut", "test"]
    search_fields = ["etudiant__email", "etudiant__first_name"]
    readonly_fields = [
        "score_global", "code_holland", "scores_par_dimension",
        "progression", "date_debut",
    ]

@admin.register(ResultatTest)
class ResultatTestAdmin(admin.ModelAdmin):
    list_display = [
        "reponse_utilisateur",
        "code_holland",
        "score_global",
        "profil_dominant",
        "date_calcul",
    ]
    list_filter = ["code_holland", "profil_dominant"]
    search_fields = ["reponse_utilisateur__etudiant__email"]
    readonly_fields = [
        "score_global", "scores_par_dimension", "code_holland",
        "interpretation", "forces", "axes_amelioration",
    ]

@admin.register(Recommandation)
class RecommandationAdmin(admin.ModelAdmin):
    list_display = [
        "etudiant",
        "type_entite",
        "entite_nom",
        "taux_compatibilite",
        "plan",
        "niveau_confiance",
        "a_ete_vue",
    ]
    list_filter = ["plan", "type_entite", "niveau_confiance", "a_ete_vue"]
    search_fields = ["etudiant__email"]
    readonly_fields = ["taux_compatibilite", "niveau_confiance"]
