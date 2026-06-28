"""
Permissions pour l'API catalog.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models.enums import UserRole


class IsAdminOrSchoolRepForWrite(BasePermission):
    """
    Lecture publique.
    Écriture réservée aux admins et représentants d'établissement.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        return request.user.role in [UserRole.ADMIN, UserRole.SCHOOL_REP]

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        # Admin : tout
        if request.user.role == UserRole.ADMIN or request.user.is_superuser:
            return True

        # SchoolRep : seulement son établissement
        if request.user.role == UserRole.SCHOOL_REP:
            school_rep_profile = getattr(request.user, "school_rep_profile", None)
            if school_rep_profile and hasattr(obj, "etablissement"):
                return obj.etablissement == school_rep_profile.etablissement
            if school_rep_profile and obj == school_rep_profile.etablissement:
                return True

        return False
