"""
Admin Django sur-mesure pour l'app accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, StudentProfile, CounselorProfile, SchoolRepProfile, ParentProfile


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name = _("Profil étudiant")
    verbose_name_plural = _("Profil étudiant")
    fk_name = "user"
    extra = 0


class CounselorProfileInline(admin.StackedInline):
    model = CounselorProfile
    can_delete = False
    verbose_name = _("Profil conseiller")
    fk_name = "user"
    extra = 0


class SchoolRepProfileInline(admin.StackedInline):
    model = SchoolRepProfile
    can_delete = False
    verbose_name = _("Profil représentant")
    fk_name = "user"
    extra = 0


class ParentProfileInline(admin.StackedInline):
    model = ParentProfile
    can_delete = False
    verbose_name = _("Profil parent")
    fk_name = "user"
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personnalisé pour User."""

    list_display = [
        "email",
        "get_full_name",
        "role",
        "statut_compte",
        "is_email_verified",
        "is_active",
        "created_at",
    ]
    list_filter = ["role", "statut_compte", "is_active", "is_email_verified", "is_staff"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Informations personnelles"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "avatar",
                    "genre",
                    "date_naissance",
                )
            },
        ),
        (
            _("Rôle et statut"),
            {"fields": ("role", "statut_compte", "profile_complete")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Vérifications"),
            {"fields": ("is_email_verified", "is_phone_verified")},
        ),
        (
            _("Préférences"),
            {"fields": ("timezone", "langue_preferee")},
        ),
        (
            _("Métadonnées"),
            {"fields": ("last_login_ip", "last_activity_at")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "role",
                ),
            },
        ),
    )

    readonly_fields = ["last_login_ip", "last_activity_at"]

    def get_inlines(self, request, obj):
        """Retourne les inlines selon le rôle de l'utilisateur."""
        if obj is None:
            return []

        from .models.enums import UserRole

        inlines_map = {
            UserRole.STUDENT: [StudentProfileInline],
            UserRole.COUNSELOR: [CounselorProfileInline],
            UserRole.SCHOOL_REP: [SchoolRepProfileInline],
            UserRole.PARENT: [ParentProfileInline],
        }

        return inlines_map.get(obj.role, [])


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "serie_bac", "annee_bac", "moyenne_generale", "is_complete"]
    list_filter = ["serie_bac", "annee_bac"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(CounselorProfile)
class CounselorProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "annees_experience", "is_available", "nombre_eleves_suivis"]
    list_filter = ["is_available"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]


@admin.register(SchoolRepProfile)
class SchoolRepProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "etablissement", "poste"]
    search_fields = ["user__email", "etablissement__nom"]


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "profession"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
