"""
Admin Django pour l'app events.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Evenement, InscriptionEvenement


class InscriptionInline(admin.TabularInline):
    model = InscriptionEvenement
    extra = 0
    fields = ["utilisateur", "statut", "date_inscription", "a_participe"]
    readonly_fields = ["date_inscription"]
    show_change_link = True
    max_num = 20


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = [
        "titre",
        "type",
        "date_debut",
        "ville",
        "organisateur_nom",
        "nombre_inscrits_affiche",
        "statut",
        "is_featured",
    ]
    list_filter = [
        "type", "format", "statut", "ville", "pays",
        "est_gratuit", "inscriptions_ouvertes", "is_featured",
    ]
    search_fields = ["titre", "description", "ville", "tags"]
    prepopulated_fields = {"slug": ("titre",)}
    filter_horizontal = ["domaines_concernes"]
    inlines = [InscriptionInline]
    readonly_fields = [
        "nombre_inscrits", "nombre_presents", "nombre_vues",
        "nombre_partages", "created_at", "updated_at",
    ]
    date_hierarchy = "date_debut"

    fieldsets = (
        (None, {
            "fields": (
                "titre", "slug", "description", "description_courte",
                "image_principale", "image_couverture",
            ),
        }),
        (_("Classification"), {
            "fields": (
                "type", "format", "statut", "cible", "priorite",
            ),
        }),
        (_("Temporalité"), {
            "fields": (
                "date_debut", "date_fin", "date_limite_inscription",
            ),
        }),
        (_("Localisation"), {
            "fields": (
                "lieu_nom", "adresse", "ville", "pays",
                "latitude", "longitude",
            ),
        }),
        (_("En ligne"), {
            "fields": (
                "lien_visio", "plateforme_visio", "code_acces",
            ),
            "classes": ("collapse",),
        }),
        (_("Inscriptions"), {
            "fields": (
                "capacite_max", "nombre_inscrits", "nombre_presents",
                "inscriptions_ouvertes", "inscription_obligatoire",
                "est_gratuit", "cout_participation", "informations_tarifs",
            ),
        }),
        (_("Organisateurs"), {
            "fields": (
                "etablissement", "organisateur_externe", "createur",
            ),
        }),
        (_("Contenu"), {
            "fields": (
                "programme", "intervenants", "tags", "domaines_concernes",
            ),
            "classes": ("collapse",),
        }),
        (_("Contact"), {
            "fields": (
                "email_contact", "telephone_contact", "site_web",
                "reseaux_sociaux",
            ),
            "classes": ("collapse",),
        }),
        (_("Rappels automatiques"), {
            "fields": (
                "envoi_rappel_j7", "envoi_rappel_j1", "envoi_rappel_j0",
            ),
        }),
        (_("Statistiques"), {
            "fields": (
                "nombre_vues", "nombre_partages", "is_featured",
                "published_at", "created_at", "updated_at",
            ),
        }),
    )

    actions = [
        "publier_evenements",
        "annuler_evenements",
        "marquer_featured",
    ]

    def nombre_inscrits_affiche(self, obj):
        if obj.capacite_max > 0:
            return f"{obj.nombre_inscrits}/{obj.capacite_max}"
        return str(obj.nombre_inscrits)
    nombre_inscrits_affiche.short_description = _("Inscrits")

    @admin.action(description="Publier les événements sélectionnés")
    def publier_evenements(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            statut="PUBLIE",
            published_at=timezone.now(),
        )
        self.message_user(request, f"{count} événement(s) publié(s).")

    @admin.action(description="Annuler les événements sélectionnés")
    def annuler_evenements(self, request, queryset):
        count = queryset.update(statut="ANNULE")
        self.message_user(request, f"{count} événement(s) annulé(s).")

    @admin.action(description="Mettre en avant")
    def marquer_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} événement(s) mis en avant.")


@admin.register(InscriptionEvenement)
class InscriptionEvenementAdmin(admin.ModelAdmin):
    list_display = [
        "utilisateur",
        "evenement",
        "statut",
        "date_inscription",
        "a_participe",
        "note_satisfaction",
    ]
    list_filter = ["statut", "a_participe", "source_inscription"]
    search_fields = [
        "utilisateur__email",
        "utilisateur__first_name",
        "evenement__titre",
    ]
    readonly_fields = [
        "date_inscription", "date_confirmation",
        "date_annulation", "date_checkin",
    ]

    actions = ["marquer_presents", "exporter_liste"]

    @admin.action(description="Marquer comme présents")
    def marquer_presents(self, request, queryset):
        count = 0
        for inscription in queryset:
            if not inscription.a_participe:
                inscription.marquer_present()
                count += 1
        self.message_user(request, f"{count} participant(s) marqué(s) présent(s).")

    @admin.action(description="Exporter la liste des inscrits")
    def exporter_liste(self, request, queryset):
        # TODO: Implémenter export CSV/Excel
        self.message_user(
            request,
            f"Export de {queryset.count()} inscription(s) (à implémenter)."
        )
