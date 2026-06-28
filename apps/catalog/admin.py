"""
Admin Django sur-mesure pour le catalog.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Domaine, Metier, Etablissement, Formation
from .services import RankingService

# ──────────────────────────────────────────────
# Domaine
# ──────────────────────────────────────────────

@admin.register(Domaine)
class DomaineAdmin(admin.ModelAdmin):
    list_display = ["nom", "icon_affiche", "nombre_formations", "nombre_metiers", "ordre", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["nom", "description"]
    prepopulated_fields = {"slug": ("nom",)}
    list_editable = ["ordre", "is_active"]
    readonly_fields = ["nombre_formations", "nombre_metiers"]

    def icon_affiche(self, obj):
        return format_html('<span style="font-size: 1.5em;">{}</span>', obj.icon or "📚")
    icon_affiche.short_description = _("Icône")


# ──────────────────────────────────────────────
# Métier
# ──────────────────────────────────────────────

@admin.register(Metier)
class MetierAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "domaine",
        "revenu_moyen_formate",
        "taux_emploi",
        "demande_marche",
        "score_attractivite",
        "is_active",
    ]
    list_filter = ["domaine", "demande_marche", "niveau_etude_requis", "is_active"]
    search_fields = ["nom", "description", "domaine__nom"]
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ["score_attractivite", "revenu_moyen_formate", "fourchette_revenu"]

    fieldsets = (
        (None, {
            "fields": ("nom", "slug", "domaine", "description", "description_courte"),
        }),
        (_("Données économiques (FCFA)"), {
            "fields": (
                "revenu_min",
                "revenu_max",
                "revenu_moyen",
                "revenu_moyen_formate",
                "fourchette_revenu",
            ),
        }),
        (_("Marché du travail"), {
            "fields": ("taux_emploi", "demande_marche", "score_attractivite"),
        }),
        (_("Formation requise"), {
            "fields": ("niveau_etude_requis", "duree_formation_typique_annees"),
        }),
        (_("Compétences et perspectives"), {
            "fields": (
                "competences_cles",
                "taches_principales",
                "perspectives_evolution",
            ),
        }),
        (_("Contexte géographique"), {
            "fields": ("pays_concernes", "villes_principales"),
        }),
        (_("Métadonnées"), {
            "fields": ("source_donnees", "date_mise_a_jour", "is_active"),
        }),
    )


# ──────────────────────────────────────────────
# Établissement
# ──────────────────────────────────────────────

@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "sigle",
        "ville",
        "type",
        "note_globale",
        "classement_national",
        "score_qualite_global",
        "is_verified",
        "is_active",
    ]
    list_filter = ["type", "statut", "ville", "pays", "is_verified", "is_active", "propose_bourses"]
    search_fields = ["nom", "sigle", "ville", "description"]
    prepopulated_fields = {"slug": ("nom",)}
    filter_horizontal = ["domaines_enseignes"]
    readonly_fields = [
        "score_qualite_global",
        "note_globale",
        "classement_national",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (None, {
            "fields": (
                "nom",
                "sigle",
                "slug",
                "description",
                "description_courte",
                "logo",
                "banniere",
            ),
        }),
        (_("Type et statut"), {
            "fields": ("type", "statut", "date_creation"),
        }),
        (_("Localisation"), {
            "fields": ("adresse", "ville", "pays", "code_postal", "latitude", "longitude"),
        }),
        (_("Contact"), {
            "fields": (
                "site_web",
                "email",
                "telephone",
                "facebook",
                "linkedin",
            ),
        }),
        (_("Coûts (FCFA)"), {
            "fields": (
                "frais_inscription_min",
                "frais_inscription_max",
                "frais_scolarite_annuel_min",
                "frais_scolarite_annuel_max",
            ),
        }),
        (_("Indicateurs de performance"), {
            "fields": (
                "nombre_etudiants",
                "nombre_enseignants",
                "taux_encadrement",
                "taux_reussite",
                "taux_insertion_professionnelle",
            ),
        }),
        (_("Classement et notes"), {
            "fields": (
                "note_globale",
                "nombre_avis",
                "classement_national",
                "classement_regional",
                "score_qualite_global",
            ),
        }),
        (_("Équipements et labels"), {
            "fields": (
                "equipements",
                "labels_qualite",
                "domaines_enseignes",
            ),
        }),
        (_("Bourses"), {
            "fields": (
                "propose_bourses",
                "montant_bourse_max",
                "criteres_bourses",
            ),
        }),
        (_("Vie étudiante"), {
            "fields": (
                "residences_universitaires",
                "clubs_et_associations",
                "sports_proposes",
            ),
        }),
        (_("Statut"), {
            "fields": (
                "is_active",
                "is_verified",
                "is_featured",
                "date_verification",
                "created_at",
                "updated_at",
            ),
        }),
    )

    actions = ["recalculer_classement", "marquer_verifies", "marquer_featured"]

    @admin.action(description="Recalculer le classement de tous les établissements")
    def recalculer_classement(self, request, queryset):
        result = RankingService.recalculer_classement_etablissements()
        self.message_user(
            request,
            f"Classement recalculé : {result['count']} établissements. "
            f"Top 3 : {', '.join([t['nom'] for t in result.get('top_3', [])])}"
        )

    @admin.action(description="Marquer comme vérifiés")
    def marquer_verifies(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f"{count} établissement(s) marqué(s) vérifié(s).")

    @admin.action(description="Marquer comme mis en avant")
    def marquer_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} établissement(s) mis en avant.")


# ──────────────────────────────────────────────
# Formation
# ──────────────────────────────────────────────

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "etablissement",
        "domaine",
        "niveau",
        "cout_annuel_formate",
        "score_qualite",
        "importance_strategique",
        "is_active",
    ]
    list_filter = [
        "niveau",
        "domaine",
        "modalite",
        "importance_strategique",
        "bourses_disponibles",
        "is_active",
        "etablissement__ville",
    ]
    search_fields = ["nom", "description", "etablissement__nom", "domaine__nom"]
    prepopulated_fields = {"slug": ("nom",)}
    filter_horizontal = ["debouches"]
    readonly_fields = ["score_qualite", "cout_total", "created_at", "updated_at"]
    autocomplete_fields = ["etablissement", "domaine"]

    fieldsets = (
        (None, {
            "fields": (
                "nom",
                "slug",
                "etablissement",
                "domaine",
                "description",
                "description_courte",
            ),
        }),
        (_("Caractéristiques"), {
            "fields": ("niveau", "duree_annees", "modalite"),
        }),
        (_("Coûts (FCFA)"), {
            "fields": (
                "cout_annuel",
                "frais_inscription",
                "frais_dossier",
                "cout_total",
            ),
        }),
        (_("Aides financières"), {
            "fields": (
                "bourses_disponibles",
                "montant_bourse_max",
                "facilites_paiement",
            ),
        }),
        (_("Importance stratégique"), {
            "fields": ("importance_strategique",),
        }),
        (_("Indicateurs de performance"), {
            "fields": (
                "taux_reussite",
                "taux_insertion_6mois",
                "taux_insertion_12mois",
                "salaire_sortie_moyen",
                "score_qualite",
            ),
        }),
        (_("Prérequis et programme"), {
            "fields": (
                "prerequis",
                "serie_bac_admises",
                "programmes",
                "debouches",
            ),
        }),
        (_("Dates et capacité"), {
            "fields": (
                "dates_rentree",
                "date_limite_inscription",
                "places_disponibles",
                "nombre_inscrits_annee",
            ),
        }),
        (_("Statut"), {
            "fields": (
                "is_active",
                "is_featured",
                "is_sur_liste_guide",
                "created_at",
                "updated_at",
            ),
        }),
    )

    def cout_annuel_formate(self, obj):
        return f"{int(obj.cout_annuel):,} FCFA".replace(",", " ")
    cout_annuel_formate.short_description = _("Coût annuel")
