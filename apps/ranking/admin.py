"""
Admin Django pour l'app ranking.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Classement


@admin.register(Classement)
class ClassementAdmin(admin.ModelAdmin):
    list_display = [
        "etablissement",
        "annee",
        "rang_national",
        "rang_regional",
        "score_formate_display",
        "is_published",
        "updated_at",
    ]
    list_filter = ["annee", "is_published"]
    search_fields = ["etablissement__nom", "etablissement__ville"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["annee", "rang_national"]

    fieldsets = (
        (None, {
            "fields": ("etablissement", "annee", "is_published"),
        }),
        (_("Rangs"), {
            "fields": ("rang_national", "rang_regional"),
        }),
        (_("Scores"), {
            "fields": ("score_final", "details_scores"),
        }),
        (_("Méthodologie"), {
            "fields": ("methodology",),
            "classes": ("collapse",),
        }),
        (_("Horodatage"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    actions = ["publier", "depublier"]

    @admin.action(description=_("Publier les classements sélectionnés"))
    def publier(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count} classement(s) publié(s).")

    @admin.action(description=_("Dépublier les classements sélectionnés"))
    def depublier(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count} classement(s) dépublié(s).")

    def score_formate_display(self, obj):
        score = obj.score_final
        if score >= 75:
            color = "green"
        elif score >= 50:
            color = "orange"
        else:
            color = "red"
        return format_html(
            '<span style="color: {};">{:.1f}/100</span>',
            color,
            score,
        )
    score_formate_display.short_description = _("Score")
