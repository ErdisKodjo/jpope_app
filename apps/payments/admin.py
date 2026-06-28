"""
Admin Django pour l'app payments.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Paiement, PlanAbonnement, Abonnement, Transaction, Facture


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = [
        "reference", "user", "montant_formate", "statut_badge",
        "provider", "created_at",
    ]
    list_filter = ["statut", "provider", "created_at"]
    search_fields = [
        "reference", "transaction_id",
        "user__email", "user__first_name",
    ]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    def montant_formate(self, obj):
        return obj.montant_formate
    montant_formate.short_description = _("Montant")

    def statut_badge(self, obj):
        colors = {
            "PENDING": "gray",
            "COMPLETED": "green",
            "FAILED": "red",
            "REFUNDED": "orange",
        }
        color = colors.get(obj.statut, "gray")
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_statut_display(),
        )
    statut_badge.short_description = _("Statut")


@admin.register(PlanAbonnement)
class PlanAbonnementAdmin(admin.ModelAdmin):
    list_display = [
        "code", "nom", "type_abonnement", "niveau", "frequence",
        "prix_fcfa", "is_active", "is_public", "is_featured",
    ]
    list_filter = ["type_abonnement", "niveau", "frequence", "is_active", "is_public"]
    search_fields = ["code", "nom", "description"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {
            "fields": ("code", "nom", "description", "description_courte"),
        }),
        (_("Classification"), {
            "fields": ("type_abonnement", "niveau", "frequence"),
        }),
        (_("Prix"), {
            "fields": ("prix_fcfa", "prix_promo_fcfa", "devise"),
        }),
        (_("Durée"), {
            "fields": ("duree_mois", "periode_essai_jours"),
        }),
        (_("Contenu"), {
            "fields": ("fonctionnalites", "limites", "avantages"),
        }),
        (_("Affichage"), {
            "fields": ("icone", "couleur", "is_active", "is_public", "is_featured", "ordre"),
        }),
        (_("Stripe"), {
            "fields": ("stripe_price_id",),
            "classes": ("collapse",),
        }),
    )


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = [
        "utilisateur", "plan", "statut", "date_debut", "date_fin",
        "jours_restants_affiche", "renouvellement_auto",
    ]
    list_filter = ["statut", "renouvellement_auto", "plan__type_abonnement"]
    search_fields = ["utilisateur__email", "utilisateur__first_name", "plan__nom"]
    readonly_fields = ["created_at", "updated_at", "nombre_renouvellements"]
    date_hierarchy = "date_debut"

    def jours_restants_affiche(self, obj):
        return f"{obj.jours_restants} j."
    jours_restants_affiche.short_description = _("Jours restants")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "reference", "utilisateur", "montant_formate_display",
        "type", "methode_paiement", "statut_badge",
        "date_initiation",
    ]
    list_filter = ["type", "methode_paiement", "statut", "date_initiation"]
    search_fields = [
        "reference", "reference_externe",
        "utilisateur__email", "utilisateur__first_name",
    ]
    readonly_fields = ["date_initiation", "created_at", "updated_at"]
    date_hierarchy = "date_initiation"

    def montant_formate_display(self, obj):
        return obj.montant_formate
    montant_formate_display.short_description = _("Montant")

    def statut_badge(self, obj):
        colors = {
            "EN_ATTENTE": "gray",
            "INITIEE": "blue",
            "CONFIRMEE": "green",
            "ECHEC": "red",
            "ANNULEE": "orange",
            "REMBOURSEE": "purple",
        }
        color = colors.get(obj.statut, "gray")
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_statut_display(),
        )
    statut_badge.short_description = _("Statut")


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = [
        "numero", "utilisateur", "montant_ttc_formate_display",
        "statut", "date_emission", "date_echeance",
    ]
    list_filter = ["statut", "date_emission"]
    search_fields = ["numero", "utilisateur__email"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "date_emission"

    def montant_ttc_formate_display(self, obj):
        return obj.montant_ttc_formate
    montant_ttc_formate_display.short_description = _("Montant TTC")
