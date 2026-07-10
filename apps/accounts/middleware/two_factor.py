"""
Middleware pour exiger le 2FA sur les comptes Établissement et Conseiller.

Conformément au cahier des charges (section 3 — Sécurité) :
"Double authentification (2FA) obligatoire pour les comptes Établissements et Conseillers."

Le middleware bloque l'accès aux endpoints protégés tant que le 2FA n'est pas activé,
sauf sur les routes d'activation du 2FA et de logout.
"""
import re
from django.conf import settings
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models.two_factor import is_2fa_required, has_active_2fa


# Routes exemptées du blocage 2FA — permettent à l'utilisateur d'activer son 2FA
TWO_FA_EXEMPT_PATTERNS = [
    r"^/api/v1/auth/2fa/",        # tous les endpoints 2FA (setup, confirm, status, etc.)
    r"^/api/v1/auth/login/?$",    # login (le challenge 2FA est lancé après)
    r"^/api/v1/auth/logout/?$",
    r"^/api/v1/auth/refresh/?$",
    r"^/api/v1/auth/password/reset",
    r"^/api/v1/auth/email/verify",
    r"^/admin/",                  # admin Django — gestion à part
    r"^/static/",
    r"^/media/",
    r"^/__debug__/",
    r"^/__reload__/",
    r"^/silk/",
    r"^/i18n/",
    r"^/$",                        # page d'accueil publique
    r"^/login/?$",
    r"^/register/?$",
    r"^/logout/?$",
    r"^/profile/2fa",              # page web de configuration du 2FA
    r"^/verification-pending",
]


class TwoFactorEnforcementMiddleware(MiddlewareMixin):
    """
    Bloque l'accès aux endpoints protégés pour les comptes SCHOOL_REP et COUNSELOR
    qui n'ont pas encore activé le 2FA. Les renvoie vers la page d'activation.
    """

    def process_request(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None

        # Superusers sont exemptés (accès admin)
        if user.is_superuser:
            return None

        # Si le 2FA n'est pas requis pour ce rôle → on laisse passer
        if not is_2fa_required(user):
            return None

        # Si le 2FA est requis ET activé → on laisse passer
        if has_active_2fa(user):
            return None

        # 2FA requis mais non activé : on bloque sauf les routes exemptées
        path = request.path
        for pattern in TWO_FA_EXEMPT_PATTERNS:
            if re.match(pattern, path):
                return None

        # Pour les requêtes API → JSON 403
        if path.startswith("/api/"):
            from rest_framework.response import Response
            from rest_framework import status as drf_status
            from django.http import JsonResponse
            return JsonResponse(
                {
                    "error": "TWO_FACTOR_REQUIRED",
                    "message": str(_("Vous devez activer le 2FA pour accéder à cette ressource.")),
                    "setup_url": "/api/v1/auth/2fa/setup/",
                },
                status=drf_status.HTTP_403_FORBIDDEN,
            )

        # Pour les requêtes web → redirect vers la page de setup
        # (on évite redirect cycles en vérifiant qu'on n'y est pas déjà)
        try:
            from django.shortcuts import redirect
            return redirect("accounts:two_fa_setup")
        except Exception:
            return None
