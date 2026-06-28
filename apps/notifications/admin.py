"""
Admin Django pour l'app notifications.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "titre_court",
        "user",
        "type_notification",
        "statut_badge",
        "read_at",
        "created_at",
    ]
    list_filter = ["type_notification", "is_read", "created_at"]
    search_fields = [
        "titre",
        "message",
        "user__email",
        "user__first_name",
    ]
    readonly_fields = ["created_at", "updated_at", "read_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {
            "fields": ("user", "type_notification"),
        }),
        (_("Contenu"), {
            "fields": ("titre", "message", "action_url"),
        }),
        (_("Statut"), {
            "fields": ("is_read", "read_at"),
        }),
        (_("Horodatage"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    actions = ["marquer_comme_lues", "marquer_comme_non_lues"]

    def titre_court(self, obj):
        return obj.titre[:50] + "..." if len(obj.titre) > 50 else obj.titre
    titre_court.short_description = _("Titre")

    def statut_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="background: darkgreen; color: white; '
                'padding: 3px 8px; border-radius: 3px;">✅ Lu</span>'
            )
        return format_html(
            '<span style="background: #3B82F6; color: white; '
            'padding: 3px 8px; border-radius: 3px;">🔵 Non lu</span>'
        )
    statut_badge.short_description = _("Statut")

    @admin.action(description=_("Marquer comme lues"))
    def marquer_comme_lues(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now(),
        )
        self.message_user(request, f"{count} notification(s) marquée(s) comme lue(s).")

    @admin.action(description=_("Marquer comme non lues"))
    def marquer_comme_non_lues(self, request, queryset):
        count = queryset.filter(is_read=True).update(
            is_read=False,
            read_at=None,
        )
        self.message_user(request, f"{count} notification(s) marquée(s) comme non lue(s).")
