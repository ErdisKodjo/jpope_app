"""
Formulaires Django pour l'app accounts.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models.enums import UserRole, Genre, SerieBac
from .models.verification import TypeDocument
from .models.notes import NotesEtudiant

User = get_user_model()

# Rôles qui nécessitent une vérification de document
ROLES_NECESSITE_VERIFICATION = {
    UserRole.PARENT,
    UserRole.COUNSELOR,
    UserRole.SCHOOL_REP,
}


class LoginForm(AuthenticationForm):
    """Formulaire de connexion (email ou téléphone)."""
    username = forms.CharField(
        label=_("Email ou téléphone"),
        widget=forms.TextInput(attrs={
            "class": "input_field",
            "placeholder": _("Votre email ou téléphone"),
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={
            "class": "input_field",
            "placeholder": _("Votre mot de passe"),
        }),
    )


class RegisterForm(UserCreationForm):
    """Formulaire d'inscription utilisateur."""
    email = forms.EmailField(
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(attrs={
            "class": "input_field",
            "placeholder": "exemple@email.com",
        }),
    )
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "input_field",
            "placeholder": _("Votre prénom"),
        }),
    )
    last_name = forms.CharField(
        label=_("Nom"),
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "input_field",
            "placeholder": _("Votre nom de famille"),
        }),
    )
    role = forms.ChoiceField(
        label=_("Je suis"),
        choices=[
            (UserRole.STUDENT, _("Étudiant(e)")),
            (UserRole.PARENT, _("Parent / Tuteur")),
            (UserRole.COUNSELOR, _("Conseiller d'orientation")),
            (UserRole.SCHOOL_REP, _("Représentant d'établissement")),
        ],
        widget=forms.Select(attrs={"class": "input_field"}),
    )
    password1 = forms.CharField(
        label=_("Mot de passe"),
        min_length=10,
        widget=forms.PasswordInput(attrs={
            "class": "input_field",
            "placeholder": _("10 caractères minimum"),
        }),
    )
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        min_length=10,
        widget=forms.PasswordInput(attrs={
            "class": "input_field",
            "placeholder": _("Répétez le mot de passe"),
        }),
    )

    # Champs de vérification (requis seulement pour les non-étudiants)
    document = forms.FileField(
        label=_("Document justificatif"),
        required=False,
        help_text=_("PDF, JPG ou PNG — 5 Mo maximum."),
        widget=forms.FileInput(attrs={"class": "input_field", "accept": ".pdf,.jpg,.jpeg,.png"}),
    )
    type_document = forms.ChoiceField(
        label=_("Type de document"),
        required=False,
        choices=[("", _("-- Choisir le type --"))] + TypeDocument.choices,
        widget=forms.Select(attrs={"class": "input_field"}),
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

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        document = cleaned_data.get("document")
        type_document = cleaned_data.get("type_document")

        if role in ROLES_NECESSITE_VERIFICATION:
            if not document:
                self.add_error(
                    "document",
                    _("Un document justificatif est obligatoire pour ce type de compte."),
                )
            if not type_document:
                self.add_error(
                    "type_document",
                    _("Veuillez sélectionner le type de document."),
                )
            # Validation taille fichier (5 Mo)
            if document and document.size > 5 * 1024 * 1024:
                self.add_error(
                    "document",
                    _("Le fichier ne doit pas dépasser 5 Mo."),
                )

        return cleaned_data

    def requires_verification(self):
        """Indique si le rôle sélectionné nécessite une vérification."""
        return self.cleaned_data.get("role") in ROLES_NECESSITE_VERIFICATION


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
            "first_name": forms.TextInput(attrs={"class": "input_field"}),
            "last_name": forms.TextInput(attrs={"class": "input_field"}),
            "phone": forms.TextInput(attrs={"class": "input_field"}),
            "avatar": forms.FileInput(attrs={"class": "input_field"}),
            "genre": forms.Select(attrs={"class": "input_field"}),
            "date_naissance": forms.DateInput(
                attrs={"class": "input_field", "type": "date"}
            ),
            "timezone": forms.Select(attrs={"class": "input_field"}),
            "langue_preferee": forms.Select(
                choices=[("fr", "Français"), ("en", "English")],
                attrs={"class": "input_field"},
            ),
        }


class StudentProfileForm(forms.Form):
    """Formulaire de mise à jour du profil étudiant."""
    serie_bac = forms.ChoiceField(
        label=_("Série du baccalauréat"),
        choices=[("", _("-- Choisir --"))] + SerieBac.choices,
        required=False,
        widget=forms.Select(attrs={"class": "input_field"}),
    )
    annee_bac = forms.IntegerField(
        label=_("Année du bac"),
        required=False,
        min_value=2000,
        max_value=2030,
        widget=forms.NumberInput(attrs={"class": "input_field"}),
    )
    moyenne_generale = forms.DecimalField(
        label=_("Moyenne générale"),
        required=False,
        min_value=0,
        max_value=20,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "input_field", "step": "0.01"}),
    )
    etablissement_scolaire = forms.CharField(
        label=_("Établissement scolaire"),
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={"class": "input_field"}),
    )
    projet_professionnel = forms.CharField(
        label=_("Projet professionnel"),
        required=False,
        widget=forms.Textarea(attrs={"class": "input_field", "rows": 4}),
    )


class PasswordResetRequestForm(forms.Form):
    """Formulaire de demande de réinitialisation de mot de passe."""
    email = forms.EmailField(
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(attrs={
            "class": "input_field",
            "placeholder": "votre@email.com",
        }),
    )


class RejectVerificationForm(forms.Form):
    """Formulaire de rejet d'une vérification (admin)."""
    motif = forms.CharField(
        label=_("Motif du rejet"),
        required=True,
        min_length=10,
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 3,
            "placeholder": _("Expliquez clairement pourquoi le document est refusé…"),
        }),
    )


class NotesEtudiantForm(forms.ModelForm):
    """Formulaire de saisie des notes académiques d'un étudiant."""

    class Meta:
        model = NotesEtudiant
        fields = [
            "annee_scolaire", "classe",
            "note_maths", "note_physique", "note_svt", "note_info",
            "note_francais", "note_anglais", "note_philosophie", "note_histoire_geo",
            "note_economie", "note_comptabilite", "note_gestion",
        ]
        widgets = {
            "annee_scolaire": forms.TextInput(attrs={"class": "input_field", "placeholder": "2024-2025"}),
            "classe": forms.TextInput(attrs={"class": "input_field", "placeholder": _("Ex : Terminale C")}),
            "note_maths": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_physique": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_svt": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_info": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_francais": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_anglais": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_philosophie": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_histoire_geo": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_economie": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_comptabilite": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
            "note_gestion": forms.NumberInput(attrs={"class": "input_field", "step": "0.25", "min": "0", "max": "20", "placeholder": "/20"}),
        }
