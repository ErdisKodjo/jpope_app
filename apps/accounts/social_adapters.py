"""
Configuration django-allauth pour auth sociale Google + Apple.

Cahier des charges (section 2.1 — Candidat) :
"Inscription via email ou authentification sociale (Google, Apple)."

Wire django-allauth to the existing User model (email-based, no username).
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.translation import gettext_lazy as _
from apps.accounts.models.enums import UserRole, StatutCompte


class AvenSUAccountAdapter(DefaultAccountAdapter):
    """Adapter allauth — utilise le modèle User personnalisé (email-based)."""

    def is_open_for_signup(self, request):
        return True

    def save_user(self, request, user, form, commit=True):
        # Force le rôle STUDENT par défaut pour les inscriptions sociales
        if not user.role:
            user.role = UserRole.STUDENT
        if not user.statut_compte:
            user.statut_compte = StatutCompte.ACTIF
        user.is_email_verified = True  # Email vérifié via le provider social
        return super().save_user(request, user, form, commit)

    def populate_username(self, request, user):
        # User model has no username field — no-op
        pass


class AvenSUSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adapter social — connecte les comptes sociaux au User personnalisé."""

    def pre_social_login(self, request, sociallogin):
        """
        Si un utilisateur avec le même email existe déjà, on connecte le compte
        social à ce compte (pas de création de doublon).
        """
        if sociallogin.is_existing:
            return
        if sociallogin.account and sociallogin.account.email:
            from apps.accounts.models import User
            try:
                user = User.objects.get(email__iexact=sociallogin.account.email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Force le rôle STUDENT si pas défini
        if not user.role:
            user.role = UserRole.STUDENT
        if not user.statut_compte:
            user.statut_compte = StatutCompte.ACTIF
        user.is_email_verified = True
        user.save()
        return user

    def is_open_for_signup(self, request, sociallogin):
        # Autorise l'inscription via providers sociaux
        return True
