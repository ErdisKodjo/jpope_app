"""
Permissions personnalisées pour l'API accounts.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models.enums import UserRole


class IsOwner(BasePermission):
    """L'utilisateur ne peut modifier que son propre profil."""

    def has_object_permission(self, request, view, obj):
        # obj peut être User ou un Profile
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user


class IsStudent(BasePermission):
    """Réservé aux étudiants."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.STUDENT
        )


class IsCounselor(BasePermission):
    """Réservé aux conseillers."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.COUNSELOR
        )


class IsSchoolRep(BasePermission):
    """Réservé aux représentants d'établissement."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.SCHOOL_REP
        )


class IsAdminRole(BasePermission):
    """Réservé aux administrateurs."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


class IsAdminOrReadOnly(BasePermission):
    """Admin pour les modifications, lecture publique."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


class IsAuthenticatedOrReadOnly(BasePermission):
    """Lecture publique, écriture authentifiée."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated


class CanViewStudentProfile(BasePermission):
    """
    Qui peut voir un profil étudiant ?
    - L'étudiant lui-même
    - Un conseiller qui le suit
    - Un parent qui l'a en suivi
    - Un admin
    """

    def has_object_permission(self, request, view, obj):
        from apps.accounts.models import StudentProfile

        if not isinstance(obj, StudentProfile):
            return False

        # L'étudiant lui-même
        if obj.user == request.user:
            return True

        # Admin
        if request.user.role == UserRole.ADMIN or request.user.is_superuser:
            return True

        # Conseiller — vérifier s'il suit cet étudiant via un accompagnement
        if request.user.role == UserRole.COUNSELOR:
            from apps.orientation.models import DemandeAccompagnement
            return DemandeAccompagnement.objects.filter(
                conseiller=request.user,
                etudiant=obj.user,
                statut__in=["ACCEPTÉE", "EN_COURS"],
            ).exists()

        # Parent
        if request.user.role == UserRole.PARENT:
            parent_profile = getattr(request.user, "parent_profile", None)
            if parent_profile:
                return parent_profile.enfants_suivis.filter(pk=obj.user.pk).exists()

        return False
