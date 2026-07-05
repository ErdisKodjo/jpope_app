"""
Mixins de contrôle d'accès pour l'app accounts.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

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
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != UserRole.COUNSELOR:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CounselorOrAdminMixin(VerifiedAccountMixin):
    """
    Réserve l'accès aux utilisateurs COUNSELOR et ADMIN.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in (UserRole.COUNSELOR, UserRole.ADMIN):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


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


class StudentRequiredMixin(LoginRequiredMixin):
    """
    Réserve l'accès aux étudiants.

    Replaces the duplicated ``dispatch`` guard that checked
    ``request.user.is_student`` in ``StudentProfileEditView``,
    ``NotesEtudiantView``, and ``DemandeAccompagnementCreateView``.

    Subclasses may override ``student_denied_url`` and
    ``student_denied_message`` to customise redirect behaviour.
    """
    student_denied_url = "accounts:profile"
    student_denied_message = _("Accès réservé aux étudiants.")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_student:
            messages.error(request, self.student_denied_message)
            return redirect(self.student_denied_url)
        return super().dispatch(request, *args, **kwargs)
