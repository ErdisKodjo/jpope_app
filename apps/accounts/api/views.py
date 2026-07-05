"""
Vues API pour l'app accounts.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from core.utils import get_client_ip

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    StudentProfileSerializer,
    StudentProfileUpdateSerializer,
    CounselorProfileSerializer,
    SchoolRepProfileSerializer,
    ParentProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
)
from .permissions import (
    IsOwner,
    IsStudent,
    IsCounselor,
    IsSchoolRep,
    IsParent,
    IsAdminRole,
)
from apps.accounts.models import (
    StudentProfile,
    CounselorProfile,
    SchoolRepProfile,
    ParentProfile,
)
from apps.accounts.models.enums import UserRole
from apps.accounts.services.auth_service import AuthService

User = get_user_model()

# ──────────────────────────────────────────────
# Authentification
# ──────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """Inscription d'un nouvel utilisateur."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)

        # Envoyer email de vérification (asynchrone)
        AuthService.send_verification_email.delay(user.id)

        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "message": "Inscription réussie. Un email de vérification vous a été envoyé.",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Connexion d'un utilisateur."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Mettre à jour la dernière connexion
        user.last_login = timezone.now()
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=["last_login", "last_login_ip"])
        user.update_last_activity()

        # Générer les tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Déconnexion (blacklist du refresh token)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Token de rafraîchissement requis."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Déconnexion réussie."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "Token invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenRefreshView(TokenRefreshView):
    """Refresh token personnalisé."""
    permission_classes = [AllowAny]


# ──────────────────────────────────────────────
# Utilisateur courant (me)
# ──────────────────────────────────────────────

class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Récupère ou met à jour le profil de l'utilisateur connecté."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Changement de mot de passe."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        return Response(
            {"message": "Mot de passe modifié avec succès."},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    """Demande de réinitialisation de mot de passe."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Toujours retourner 200 pour ne pas révéler si l'email existe
        AuthService.send_password_reset_email.delay(email)

        return Response(
            {"message": "Si cet email existe, un lien de réinitialisation a été envoyé."},
            status=status.HTTP_200_OK,
        )


class EmailVerificationView(APIView):
    """Vérification de l'email via token."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = AuthService.verify_email_token(
            serializer.validated_data["token"]
        )

        if success:
            return Response(
                {"message": "Email vérifié avec succès."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Token invalide ou expiré."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetConfirmView(APIView):
    """Confirmation de réinitialisation de mot de passe."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = AuthService.reset_password_with_token(
            serializer.validated_data["token"],
            serializer.validated_data["new_password"],
        )

        if success:
            return Response(
                {"message": "Mot de passe réinitialisé avec succès."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Token invalide ou expiré."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ──────────────────────────────────────────────
# Profils
# ──────────────────────────────────────────────

class StudentProfileView(generics.RetrieveUpdateAPIView):
    """Récupère ou met à jour le profil étudiant."""
    permission_classes = [IsAuthenticated, IsStudent]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return StudentProfileUpdateSerializer
        return StudentProfileSerializer

    def get_object(self):
        # Retourne le profil de l'utilisateur connecté
        return self.request.user.student_profile

    def perform_update(self, serializer):
        instance = serializer.save()
        # Vérifier si le profil est maintenant complet
        if instance.is_complete:
            self.request.user.profile_complete = True
            self.request.user.save(update_fields=["profile_complete"])


class CounselorProfileView(generics.RetrieveUpdateAPIView):
    """Récupère ou met à jour le profil conseiller."""
    serializer_class = CounselorProfileSerializer
    permission_classes = [IsAuthenticated, IsCounselor | IsAdminRole]

    def get_object(self):
        return self.request.user.counselor_profile


class SchoolRepProfileView(generics.RetrieveUpdateAPIView):
    """Récupère ou met à jour le profil représentant d'établissement."""
    serializer_class = SchoolRepProfileSerializer
    permission_classes = [IsAuthenticated, IsSchoolRep | IsAdminRole]

    def get_object(self):
        return self.request.user.school_rep_profile


class ParentProfileView(generics.RetrieveUpdateAPIView):
    """Récupère ou met à jour le profil parent."""
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAuthenticated, IsParent | IsAdminRole]

    def get_object(self):
        return self.request.user.parent_profile


# ──────────────────────────────────────────────
# Admin : Liste des utilisateurs
# ──────────────────────────────────────────────

class UserAdminViewSet(viewsets.ModelViewSet):
    """ViewSet admin pour gérer les utilisateurs."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = User.objects.all()
    http_method_names = ["get", "patch", "delete"]

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """Active/désactive un utilisateur."""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return Response(
            {"message": f"Utilisateur {'activé' if user.is_active else 'désactivé'}."}
        )

    @action(detail=True, methods=["post"])
    def change_role(self, request, pk=None):
        """Change le rôle d'un utilisateur."""
        user = self.get_object()
        new_role = request.data.get("role")

        if new_role not in UserRole.values:
            return Response(
                {"error": "Rôle invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.role = new_role
        user.save(update_fields=["role"])

        # Créer le profil pour le nouveau rôle si nécessaire
        from apps.accounts.models import (
            StudentProfile, CounselorProfile,
            SchoolRepProfile, ParentProfile,
        )
        profile_map = {
            UserRole.STUDENT: StudentProfile,
            UserRole.COUNSELOR: CounselorProfile,
            UserRole.SCHOOL_REP: SchoolRepProfile,
            UserRole.PARENT: ParentProfile,
        }
        profile_cls = profile_map.get(new_role)
        if profile_cls:
            try:
                profile_cls.objects.get_or_create(user=user)
            except Exception:
                pass

        return Response(UserSerializer(user).data)
