"""
Serializers DRF pour l'API accounts.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.models import (
    StudentProfile,
    CounselorProfile,
    SchoolRepProfile,
    ParentProfile,
)
from apps.accounts.models.enums import UserRole

User = get_user_model()

# ──────────────────────────────────────────────
# Serializers de base
# ──────────────────────────────────────────────

class UserMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour afficher un utilisateur."""
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = ["public_id", "first_name", "last_name", "full_name", "avatar", "role"]
        read_only_fields = ["public_id"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer complet pour l'utilisateur."""
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "public_id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "avatar",
            "genre",
            "date_naissance",
            "role",
            "is_email_verified",
            "timezone",
            "langue_preferee",
            "profile_complete",
            "created_at",
        ]
        read_only_fields = [
            "public_id",
            "email",
            "role",
            "is_email_verified",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Serializers d'inscription
# ──────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer d'inscription utilisateur."""
    password = serializers.CharField(write_only=True, min_length=10)
    password_confirm = serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "role",
        ]

    def validate_role(self, value):
        """Empêche l'inscription directe en admin."""
        if value == UserRole.ADMIN:
            raise serializers.ValidationError(
                _("Vous ne pouvez pas vous inscrire en tant qu'administrateur.")
            )
        return value

    def validate(self, attrs):
        """Vérifie la cohérence des mots de passe et leur validité."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": _("Les mots de passe ne correspondent pas.")}
            )

        try:
            validate_password(attrs["password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        """Crée l'utilisateur et son profil associé."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)
        return user


# ──────────────────────────────────────────────
# Serializers d'authentification
# ──────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    """Serializer de connexion."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        from django.contrib.auth import authenticate

        user = authenticate(
            email=attrs["email"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError(
                _("Identifiants invalides.")
            )

        if not user.is_active:
            raise serializers.ValidationError(
                _("Ce compte est désactivé.")
            )

        attrs["user"] = user
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    """Serializer de réponse après authentification."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


# ──────────────────────────────────────────────
# Serializers de profils
# ──────────────────────────────────────────────

class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer du profil étudiant."""
    user = UserSerializer(read_only=True)
    is_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = StudentProfile
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at", "nombre_tests_passes"]


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer de mise à jour du profil étudiant."""

    class Meta:
        model = StudentProfile
        fields = [
            "serie_bac",
            "annee_bac",
            "moyenne_generale",
            "etablissement_scolaire",
            "ville_etablissement",
            "centres_interet",
            "matieres_fortes",
            "matieres_faibles",
            "contraintes_financieres",
            "budget_max_annuel",
            "mobilite_geographique",
            "villes_preferees",
            "projet_professionnel",
            "metiers_envisages",
        ]


class CounselorProfileSerializer(serializers.ModelSerializer):
    """Serializer du profil conseiller."""
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = CounselorProfile
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


class SchoolRepProfileSerializer(serializers.ModelSerializer):
    """Serializer du profil représentant d'établissement."""
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = SchoolRepProfile
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


class ParentProfileSerializer(serializers.ModelSerializer):
    """Serializer du profil parent."""
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = ParentProfile
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


# ──────────────────────────────────────────────
# Serializers utilitaires
# ──────────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer de changement de mot de passe."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=10)
    new_password_confirm = serializers.CharField(write_only=True, min_length=10)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Ancien mot de passe incorrect."))
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": _("Les mots de passe ne correspondent pas.")}
            )
        try:
            validate_password(attrs["new_password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer de demande de réinitialisation de mot de passe."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer de confirmation de réinitialisation."""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=10)
    new_password_confirm = serializers.CharField(write_only=True, min_length=10)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": _("Les mots de passe ne correspondent pas.")}
            )
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer de vérification d'email."""
    token = serializers.CharField()
