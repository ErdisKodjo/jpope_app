"""
Formulaires dashboard — EvaluationConseiller, Voeu, DemarcheInscription.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import EvaluationConseiller, Voeu, DemarcheInscription, StatutVoeu, StatutDemarche

User = get_user_model()

_LIST_HELP = "Un élément par ligne."


class EvaluationConseillerForm(forms.ModelForm):
    """
    Formulaire de création/édition d'une fiche d'évaluation.
    Les champs JSONField (listes) sont saisis un élément par ligne
    et convertis en list Python dans clean().
    """

    etudiant_email = forms.EmailField(
        label=_("Email de l'étudiant"),
        help_text=_("Adresse e-mail du compte étudiant à évaluer."),
        widget=forms.EmailInput(attrs={
            "class": "input_field",
            "placeholder": "etudiant@exemple.com",
        }),
    )

    points_forts_texte = forms.CharField(
        label=_("Points forts"),
        required=False,
        help_text=_LIST_HELP,
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 4,
            "placeholder": "Bonne capacité analytique\nEsprit de synthèse\n…",
        }),
    )

    points_attention_texte = forms.CharField(
        label=_("Points d'attention"),
        required=False,
        help_text=_LIST_HELP,
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 4,
            "placeholder": "Manque de confiance\nDifficultés en mathématiques\n…",
        }),
    )

    formations_suggerees_texte = forms.CharField(
        label=_("Formations suggérées"),
        required=False,
        help_text=_LIST_HELP,
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 4,
            "placeholder": "Licence Informatique — Université de Lomé\nBTS Gestion\n…",
        }),
    )

    class Meta:
        model = EvaluationConseiller
        fields = ["bilan_scolaire"]
        widgets = {
            "bilan_scolaire": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 6,
                "placeholder": "Résumé du parcours scolaire, résultats, contexte…",
            }),
        }

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        if instance:
            self.fields["etudiant_email"].initial = instance.etudiant.email
            self.fields["points_forts_texte"].initial = "\n".join(instance.points_forts or [])
            self.fields["points_attention_texte"].initial = "\n".join(instance.points_attention or [])
            self.fields["formations_suggerees_texte"].initial = "\n".join(instance.formations_suggerees or [])

    def _split_lines(self, texte: str) -> list:
        return [line.strip() for line in texte.splitlines() if line.strip()]

    def clean_etudiant_email(self):
        email = self.cleaned_data["etudiant_email"].lower().strip()
        try:
            user = User.objects.get(email=email, role="STUDENT", is_active=True)
        except User.DoesNotExist:
            raise forms.ValidationError(
                _("Aucun étudiant actif avec cet e-mail.")
            )
        return user

    def clean(self):
        cd = super().clean()
        cd["points_forts"]         = self._split_lines(cd.get("points_forts_texte", ""))
        cd["points_attention"]     = self._split_lines(cd.get("points_attention_texte", ""))
        cd["formations_suggerees"] = self._split_lines(cd.get("formations_suggerees_texte", ""))
        return cd

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.etudiant           = self.cleaned_data["etudiant_email"]
        instance.points_forts       = self.cleaned_data["points_forts"]
        instance.points_attention   = self.cleaned_data["points_attention"]
        instance.formations_suggerees = self.cleaned_data["formations_suggerees"]
        if commit:
            instance.save()
        return instance


class AdminReviewForm(forms.Form):
    """
    Formulaire utilisé par l'admin pour valider ou demander une révision.
    """
    note_admin = forms.CharField(
        label=_("Commentaire admin"),
        required=False,
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 4,
            "placeholder": "Observations, demandes de précision…",
        }),
    )
    action = forms.ChoiceField(
        choices=[
            ("valider", _("Valider la fiche")),
            ("revision", _("Demander une révision")),
            ("archiver", _("Archiver")),
        ],
        widget=forms.HiddenInput(),
    )


_FIELD_ATTRS = {"class": "input_field"}
_TA_ATTRS = {"class": "input_field", "rows": 4}


class VoeuForm(forms.ModelForm):
    class Meta:
        model = Voeu
        fields = ["priorite", "niveau_priorite", "lettre_motivation", "notes_etudiant"]
        widgets = {
            "priorite": forms.NumberInput(attrs={**_FIELD_ATTRS, "min": 1, "max": 20}),
            "niveau_priorite": forms.Select(attrs=_FIELD_ATTRS),
            "lettre_motivation": forms.Textarea(attrs={**_TA_ATTRS, "rows": 6, "placeholder": "Expliquez votre motivation pour cette formation…"}),
            "notes_etudiant": forms.Textarea(attrs={**_TA_ATTRS, "placeholder": "Notes personnelles, rappels…"}),
        }


class VoeuStatutForm(forms.ModelForm):
    """Formulaire minimal pour changer le statut d'un vœu."""
    class Meta:
        model = Voeu
        fields = ["statut"]
        widgets = {"statut": forms.Select(attrs=_FIELD_ATTRS)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # N'autoriser que les transitions possibles depuis l'étudiant
        choix_autorises = [
            StatutVoeu.BROUILLON,
            StatutVoeu.SOUMIS,
            StatutVoeu.ABANDONNE,
        ]
        self.fields["statut"].choices = [
            (v, l) for v, l in StatutVoeu.choices if v in choix_autorises
        ]


class DemarcheForm(forms.ModelForm):
    class Meta:
        model = DemarcheInscription
        fields = ["titre", "type", "description", "statut", "progression", "date_echeance", "cout_estime", "notes_etudiant"]
        widgets = {
            "titre": forms.TextInput(attrs={**_FIELD_ATTRS, "placeholder": "Ex : Constituer le dossier d'inscription"}),
            "type": forms.Select(attrs=_FIELD_ATTRS),
            "description": forms.Textarea(attrs={**_TA_ATTRS, "placeholder": "Instructions, liens utiles…"}),
            "statut": forms.Select(attrs=_FIELD_ATTRS),
            "progression": forms.NumberInput(attrs={**_FIELD_ATTRS, "min": 0, "max": 100}),
            "date_echeance": forms.DateTimeInput(attrs={**_FIELD_ATTRS, "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "cout_estime": forms.NumberInput(attrs={**_FIELD_ATTRS, "placeholder": "0"}),
            "notes_etudiant": forms.Textarea(attrs={**_TA_ATTRS, "placeholder": "Notes personnelles…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_echeance"].input_formats = ["%Y-%m-%dT%H:%M"]
