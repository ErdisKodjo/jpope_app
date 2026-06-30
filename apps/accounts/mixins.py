"""
Mixins de contrôle d'accès pour l'app accounts.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models.enums import StatutCompte, UserRole


class VerifiedAccountMixin(LoginRequiredMixin):
    """
    Bloque l'accès aux utilisateurs dont le compte est EN_ATTENTE_VERIFICATION.
    À utiliser sur les vues qui nécessitent un compte pleinement actif
    (tests d'orientation, posting forum, etc.).
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.statut_compte == StatutCompte.EN_ATTENTE_VERIFICATION:
            return redirect("accounts:verification_pending")
        return super().dispatch(request, *args, **kwargs)


class CounselorRequiredMixin(VerifiedAccountMixin):
    """
    Réserve l'accès aux utilisateurs ayant le rôle COUNSELOR.
    """

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return result
        if request.user.role != UserRole.COUNSELOR:
            raise PermissionDenied
        return result


class AdminRequiredMixin(LoginRequiredMixin):
    """
    Réserve l'accès aux utilisateurs ayant le rôle ADMIN ou superuser.
    Lève une PermissionDenied si l'utilisateur connecté n'est pas admin.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin_role:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
