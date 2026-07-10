"""
Vues API pour l'authentification à deux facteurs (2FA).

Endpoints exposés :
- POST /api/v1/auth/2fa/setup/         → initie le setup (retourne secret + QR)
- POST /api/v1/auth/2fa/confirm/       → confirme le code TOTP et active
- POST /api/v1/auth/2fa/disable/       → désactive après vérification
- POST /api/v1/auth/2fa/backup/regenerate/  → régénère les codes de secours
- POST /api/v1/auth/2fa/challenge/     → crée un défi (étape login 2FA)
- POST /api/v1/auth/2fa/verify/        → vérifie le code TOTP + défi → JWT
- GET  /api/v1/auth/2fa/status/        → statut 2FA de l'utilisateur courant
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.services.two_factor_service import TwoFactorService
from apps.accounts.models.two_factor import is_2fa_required, has_active_2fa


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class TwoFASetupView(APIView):
    """Étape 1 : génère le secret TOTP + QR code (utilisateur authentifié requis)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = TwoFactorService.initiate_setup(request.user)
        # On ne renvoie jamais le secret dans une response GET — seulement ici, à la création
        return Response(result, status=status.HTTP_200_OK)


class TwoFAConfirmView(APIView):
    """Étape 2 : utilisateur saisit un code TOTP → on active le 2FA + on génère les backup codes."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code", "").strip()
        if not code:
            return Response(
                {"error": "Le champ 'code' est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = TwoFactorService.confirm_setup(request.user, code)
        return Response(result, status=status.HTTP_200_OK)


class TwoFADisableView(APIView):
    """Désactive le 2FA après vérification d'un code TOTP ou de secours."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = (request.data.get("code") or "").strip()
        backup_code = (request.data.get("backup_code") or "").strip()
        if not code and not backup_code:
            return Response(
                {"error": "Un code TOTP ou un code de secours est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        TwoFactorService.disable(request.user, code=code or None, backup_code=backup_code or None)
        return Response({"message": "2FA désactivé."}, status=status.HTTP_200_OK)


class TwoFABackupRegenerateView(APIView):
    """Régénère les codes de secours (nécessite un code TOTP valide)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = (request.data.get("code") or "").strip()
        if not code:
            return Response(
                {"error": "Le champ 'code' est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        backup_codes = TwoFactorService.regenerate_backup_codes(request.user, code)
        return Response(
            {"backup_codes": backup_codes, "message": "Nouveaux codes générés. Les anciens sont invalidés."},
            status=status.HTTP_200_OK,
        )


class TwoFAChallengeView(APIView):
    """
    Étape login 2FA : après validation email+password, le client appelle cet endpoint
    avec son refresh token (ou id utilisateur via serializer) pour obtenir un challenge_token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not has_active_2fa(user):
            # Si le 2FA est requis mais pas encore activé, on invite à le configurer
            if is_2fa_required(user):
                return Response(
                    {
                        "error": "2FA_REQUIRED_BUT_NOT_SETUP",
                        "message": "Vous devez activer le 2FA pour finaliser la connexion.",
                        "setup_url": "/api/v1/auth/2fa/setup/",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            # 2FA pas requis → on délivre directement un JWT
            refresh = RefreshToken.for_user(user)
            return Response(
                {"access": str(refresh.access_token), "refresh": str(refresh), "user_id": str(user.id)},
                status=status.HTTP_200_OK,
            )

        challenge = TwoFactorService.create_challenge(user, ip_address=_client_ip(request))
        return Response(
            {
                "challenge_token": challenge.challenge_token,
                "expires_at": challenge.expires_at,
                "message": "Saisissez le code TOTP généré par votre application.",
            },
            status=status.HTTP_200_OK,
        )


class TwoFAVerifyView(APIView):
    """
    Étape finale login 2FA : le client soumet challenge_token + code TOTP.
    Si valide, retourne les tokens JWT d'accès.
    """
    permission_classes = [AllowAny]  # Pas authentifié — le challenge_token fait foi

    def post(self, request):
        challenge_token = (request.data.get("challenge_token") or "").strip()
        code = (request.data.get("code") or "").strip()
        if not challenge_token or not code:
            return Response(
                {"error": "Les champs 'challenge_token' et 'code' sont requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = TwoFactorService.verify_challenge(
            challenge_token=challenge_token,
            code=code,
            ip_address=_client_ip(request),
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": str(user.id),
            },
            status=status.HTTP_200_OK,
        )


class TwoFAStatusView(APIView):
    """Statut 2FA de l'utilisateur courant."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "required": is_2fa_required(user),
                "enabled": has_active_2fa(user),
                "is_superuser": user.is_superuser,
            },
            status=status.HTTP_200_OK,
        )
