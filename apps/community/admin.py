"""
Admin Django pour l'app community.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Forum, Thread, MessageForum, AbonnementForum,
    ProfilMentor, RelationMentorat, SeanceMentorat,
    ConversationPrivee, MessagePrive,
    Signalement, BlocageUtilisateur,
)


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = [
        "icone_affiche", "nom", "type", "nombre_threads",
        "nombre_messages", "is_active", "is_featured",
    ]
    list_filter = ["type", "is_active", "is_featured"]
    search_fields = ["nom", "description"]
    prepopulated_fields = {"slug": ("nom",)}

    def icone_affiche(self, obj):
        return format_html('<span style="font-size: 1.5em;">{}</span>', obj.icone)
    icone_affiche.short_description = _("Icône")


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = [
        "titre", "forum", "auteur", "statut",
        "nombre_reponses", "nombre_vues", "est_resolu_affichage",
        "created_at",
    ]
    list_filter = ["statut", "forum", "is_epingle"]
    search_fields = ["titre", "contenu", "auteur__email"]
    readonly_fields = ["nombre_reponses", "nombre_vues", "created_at"]

    def est_resolu_affichage(self, obj):
        if obj.est_resolu:
            return format_html('<span style="color: green;">Résolu</span>')
        return format_html('<span style="color: orange;">Non résolu</span>')
    est_resolu_affichage.short_description = _("Résolution")


@admin.register(MessageForum)
class MessageForumAdmin(admin.ModelAdmin):
    list_display = [
        "thread", "auteur", "type", "nombre_likes",
        "is_solution", "est_valide", "is_supprime", "created_at",
    ]
    list_filter = ["type", "is_solution", "est_valide", "is_supprime"]
    search_fields = ["contenu", "auteur__email", "thread__titre"]


@admin.register(ProfilMentor)
class ProfilMentorAdmin(admin.ModelAdmin):
    list_display = [
        "utilisateur", "type_mentor", "is_disponible",
        "nombre_mentores_actuels", "note_moyenne",
        "is_verifie",
    ]
    list_filter = ["type_mentor", "is_disponible", "is_verifie"]
    search_fields = [
        "utilisateur__email",
        "utilisateur__first_name",
        "bio",
    ]

    actions = ["verifier_profils", "deverifier_profils"]

    @admin.action(description="Vérifier les profils sélectionnés")
    def verifier_profils(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            is_verifie=True,
            date_verification=timezone.now(),
        )
        self.message_user(request, f"{count} profil(s) vérifié(s).")

    @admin.action(description="Dévérifier")
    def deverifier_profils(self, request, queryset):
        count = queryset.update(is_verifie=False)
        self.message_user(request, f"{count} profil(s) dévérifié(s).")


@admin.register(RelationMentorat)
class RelationMentoratAdmin(admin.ModelAdmin):
    list_display = [
        "mentor", "mentoré", "statut",
        "date_demande", "nombre_seances",
    ]
    list_filter = ["statut"]
    search_fields = [
        "mentor__utilisateur__email",
        "mentoré__email",
    ]


@admin.register(ConversationPrivee)
class ConversationPriveeAdmin(admin.ModelAdmin):
    list_display = ["id", "is_groupe", "dernier_message_at", "created_at"]
    list_filter = ["is_groupe"]


@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = [
        "type_contenu", "type", "auteur",
        "statut", "created_at",
    ]
    list_filter = ["statut", "type", "type_contenu"]
    search_fields = ["contenu_resume", "description", "auteur__email"]

    actions = ["traiter_signalements"]

    @admin.action(description="Marquer comme traités")
    def traiter_signalements(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            statut="TRAITE",
            traite_par=request.user,
            date_traitement=timezone.now(),
        )
        self.message_user(request, f"{count} signalement(s) traité(s).")


@admin.register(BlocageUtilisateur)
class BlocageUtilisateurAdmin(admin.ModelAdmin):
    list_display = ["bloqueur", "bloque", "niveau", "created_at"]
    list_filter = ["niveau"]
