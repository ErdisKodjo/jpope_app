"""
Vues API pour l'authentification sociale Google + Apple.

Fournit les URLs d'autorisation OAuth et le callback qui échange le code
contre un token JWT AvenSU-Orienta.

Endpoints :
- GET  /api/v1/auth/social/<provider>/login/   → retourne l'URL OAuth
- POST /api/v1/auth/social/<provider>/callback/ → échange un code OAuth contre un JWT
- GET  /api/v1/auth/social/providers/          → liste des providers disponibles
"""
import logging
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter

logger = logging.getLogger(__name__)


PROVIDERS_AVAILABLE = ["google", "apple"]


class SocialProvidersView(APIView):
    """Liste les providers d'auth sociale disponibles."""
    permission_classes = [AllowAny]

    def get(self, request):
        providers = []
        for p in PROVIDERS_AVAILABLE:
            try:
                app = SocialApp.objects.get(provider=p)
                configured = bool(app.client_id and app.secret)
            except SocialApp.DoesNotExist:
                configured = False
            providers.append({
                "id": p,
                "name": "Google" if p == "google" else "Apple",
                "configured": configured,
                "login_url": f"/api/v1/auth/social/{p}/login/",
            })
        return Response({"providers": providers})


class SocialLoginURLView(APIView):
    """
    Retourne l'URL OAuth du provider pour redirection depuis l'app mobile.
    L'app mobile ouvre cette URL dans un navigateur in-app, puis reçoit le callback.
    """
    permission_classes = [AllowAny]

    def get(self, request, provider):
        if provider not in PROVIDERS_AVAILABLE:
            return Response(
                {"error": f"Provider '{provider}' non supporté."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            app = SocialApp.objects.get(provider=provider)
            if not app.client_id:
                return Response(
                    {"error": f"Provider '{provider}' non configuré."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        except SocialApp.DoesNotExist:
            return Response(
                {"error": f"Provider '{provider}' non configuré."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Construction de l'URL d'autorisation
        from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
        from django.http import HttpResponseRedirect

        # allauth gère la génération de l'URL via sa vue de login
        # On redirige vers la vue web allauth qui construit l'URL et renvoie 302
        allauth_login_url = f"/accounts/{provider}/login/"
        return Response({
            "provider": provider,
            "auth_url": request.build_absolute_uri(allauth_login_url),
            "callback_url": request.build_absolute_uri(
                reverse("accounts-api:social_callback", kwargs={"provider": provider})
            ),
            "instructions": (
                "Ouvrez auth_url dans un navigateur in-app. Après authentification, "
                "l'utilisateur sera redirigé vers callback_url avec le code d'autorisation."
            ),
        })


class SocialCallbackView(APIView):
    """
    Reçoit le code OAuth du provider après authentification, l'échange contre
    un utilisateur AvenSU-Orienta et délivre un JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request, provider):
        code = request.data.get("code") or request.GET.get("code")
        if not code:
            return Response(
                {"error": "Paramètre 'code' manquant."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if provider == "google":
            adapter = GoogleOAuth2Adapter()
        elif provider == "apple":
            adapter = AppleOAuth2Adapter()
        else:
            return Response(
                {"error": f"Provider '{provider}' non supporté."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            client = OAuth2Client(
                request,
                adapter.client_id,
                adapter.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                adapter.callback_url,
            )
            token = client.get_access_token(code)
            social_token = SocialToken(token=token["access_token"], app=adapter.get_provider().app)
            login = adapter.complete_login(request, social_token)
            login.token = social_token
            login.lookup()
            login.connect(request)

            user = login.account.user
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_new_user": login.account._state.adding,
                },
            })
        except Exception as e:
            logger.exception(f"OAuth callback failed for {provider}")
            return Response(
                {"error": "Échange OAuth échoué.", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ConnectedSocialAccountsView(APIView):
    """Liste les comptes sociaux connectés à l'utilisateur courant."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from allauth.socialaccount.models import SocialAccount
        accounts = SocialAccount.objects.filter(user=request.user)
        return Response({
            "accounts": [
                {
                    "id": str(a.id),
                    "provider": a.provider,
                    "uid": a.uid,
                    "display_name": a.extra_data.get("name", ""),
                    "email": a.extra_data.get("email", ""),
                }
                for a in accounts
            ]
        })

    def delete(self, request, provider):
        from allauth.socialaccount.models import SocialAccount
        deleted, _ = SocialAccount.objects.filter(
            user=request.user, provider=provider
        ).delete()
        if deleted:
            return Response({"message": f"Compte {provider} déconnecté."})
        return Response({"error": "Aucun compte à déconnecter."}, status=status.HTTP_404_NOT_FOUND)
