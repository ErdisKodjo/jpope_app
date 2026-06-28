"""
Formulaires Django pour l'app accounts.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models.enums import UserRole, Genre, SerieBac

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Formulaire de connexion (email ou téléphone)."""
    username = forms.CharField(
        label=_("Email ou téléphone"),
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("Votre email ou téléphone"),
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": _("Votre mot de passe"),
        }),
    )


class RegisterForm(UserCreationForm):
    """Formulaire d'inscription utilisateur."""
    email = forms.EmailField(
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        label=_("Nom"),
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    role = forms.ChoiceField(
        label=_("Je suis"),
        choices=[
            (UserRole.STUDENT, _("Étudiant")),
            (UserRole.PARENT, _("Parent/Tuteur")),
            (UserRole.COUNSELOR, _("Conseiller d'orientation")),
            (UserRole.SCHOOL_REP, _("Représentant d'établissement")),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    password1 = forms.CharField(
        label=_("Mot de passe"),
        min_length=10,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        min_length=10,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "password1", "password2"]

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if role == UserRole.ADMIN:
            raise forms.ValidationError(
                _("Vous ne pouvez pas vous inscrire en tant qu'administrateur.")
            )
        return role


class UserProfileForm(forms.ModelForm):
    """Formulaire de mise à jour du profil utilisateur."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "genre",
            "date_naissance",
            "timezone",
            "langue_preferee",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "genre": forms.Select(attrs={"class": "form-control"}),
            "date_naissance": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "timezone": forms.Select(attrs={"class": "form-control"}),
            "langue_preferee": forms.Select(
                choices=[("fr", "Français"), ("en", "English")],
                attrs={"class": "form-control"},
            ),
        }


class StudentProfileForm(forms.Form):
    """Formulaire de mise à jour du profil étudiant."""
    serie_bac = forms.ChoiceField(
        label=_("Série du baccalauréat"),
        choices=[("", _("-- Choisir --"))] + SerieBac.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    annee_bac = forms.IntegerField(
        label=_("Année du bac"),
        required=False,
        min_value=2000,
        max_value=2030,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    moyenne_generale = forms.DecimalField(
        label=_("Moyenne générale"),
        required=False,
        min_value=0,
        max_value=20,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    etablissement_scolaire = forms.CharField(
        label=_("Établissement scolaire"),
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    projet_professionnel = forms.CharField(
        label=_("Projet professionnel"),
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )


class PasswordResetRequestForm(forms.Form):
    """Formulaire de demande de réinitialisation de mot de passe."""
    email = forms.EmailField(
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
