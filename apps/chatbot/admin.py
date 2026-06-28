"""
Admin Django pour l'app chatbot.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ["role", "contenu_court", "intent_detecte", "source_reponse", "created_at"]
    readonly_fields = ["role", "contenu_court", "intent_detecte", "source_reponse", "created_at"]
    show_change_link = True
    max_num = 20

    def contenu_court(self, obj):
        return obj.contenu[:100] + "..." if len(obj.contenu) > 100 else obj.contenu
    contenu_court.short_description = _("Contenu")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        "titre_court",
        "utilisateur",
        "canal",
        "statut",
        "nombre_messages",
        "tokens_utilises",
        "note_satisfaction",
        "updated_at",
    ]
    list_filter = ["statut", "canal", "signale"]
    search_fields = ["titre", "utilisateur__email", "utilisateur__first_name"]
    readonly_fields = [
        "nombre_messages", "nombre_messages_utilisateur",
        "nombre_messages_assistant", "tokens_utilises",
        "cout_estime_usd", "created_at", "updated_at",
    ]
    inlines = [MessageInline]

    actions = ["archiver_conversations", "exporter_conversations"]

    def titre_court(self, obj):
        return obj.titre[:50] + "..." if len(obj.titre) > 50 else obj.titre
    titre_court.short_description = _("Titre")

    @admin.action(description="Archiver les conversations sélectionnées")
    def archiver_conversations(self, request, queryset):
        count = queryset.update(statut="ARCHIVEE")
        self.message_user(request, f"{count} conversation(s) archivée(s).")

    @admin.action(description="Exporter les conversations")
    def exporter_conversations(self, request, queryset):
        self.message_user(
            request,
            f"Export de {queryset.count()} conversation(s) (à implémenter)."
        )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "conversation",
        "role",
        "contenu_court",
        "intent_detecte",
        "source_reponse",
        "tokens_total",
        "latence_ms",
        "feedbackpositif_icon",
        "created_at",
    ]
    list_filter = ["role", "intent_detecte", "source_reponse", "feedbackpositif"]
    search_fields = ["contenu", "conversation__titre"]
    readonly_fields = ["created_at"]

    def contenu_court(self, obj):
        return obj.contenu[:80] + "..." if len(obj.contenu) > 80 else obj.contenu
    contenu_court.short_description = _("Contenu")

    def feedbackpositif_icon(self, obj):
        if obj.feedbackpositif is True:
            return format_html('<span style="color: green;">+1</span>')
        elif obj.feedbackpositif is False:
            return format_html('<span style="color: red;">-1</span>')
        return format_html('<span style="color: gray;">—</span>')
    feedbackpositif_icon.short_description = _("Feedback")
