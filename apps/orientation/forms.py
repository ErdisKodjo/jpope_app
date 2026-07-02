"""
Formulaires pour l'app orientation.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models.accompagnement import DemandeAccompagnement, QuestionProposee


class DemandeAccompagnementForm(forms.ModelForm):
    """Formulaire de demande d'accompagnement par un conseiller."""

    class Meta:
        model = DemandeAccompagnement
        fields = ["motif", "domaines_concernes"]
        widgets = {
            "motif": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 5,
                "placeholder": _(
                    "Décrivez votre situation : quelles recommandations vous posent question, "
                    "quels sont vos doutes, ce que vous espérez de cet accompagnement…"
                ),
            }),
        }

    domaines_concernes = forms.MultipleChoiceField(
        label=_("Domaines concernés"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ("Informatique & Numérique", "Informatique & Numérique"),
            ("Ingenierie & Industrie", "Ingénierie & Industrie"),
            ("Santé & Médecine", "Santé & Médecine"),
            ("Gestion & Commerce", "Gestion & Commerce"),
            ("Droit & Sciences Politiques", "Droit & Sciences Politiques"),
            ("Lettres & Sciences Humaines", "Lettres & Sciences Humaines"),
            ("Agriculture & Environnement", "Agriculture & Environnement"),
            ("Éducation & Formation", "Éducation & Formation"),
        ],
    )

    def clean_domaines_concernes(self):
        return list(self.cleaned_data.get("domaines_concernes", []))


class MessageAccompagnementForm(forms.Form):
    """Formulaire d'envoi d'un message dans une session d'accompagnement."""
    contenu = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 3,
            "placeholder": _("Votre message…"),
        }),
        min_length=1,
        max_length=5000,
    )


class AccepterDemandeForm(forms.Form):
    """Formulaire d'acceptation d'une demande par un conseiller."""
    message_reponse = forms.CharField(
        label=_("Message de bienvenue"),
        required=False,
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 3,
            "placeholder": _("Mot d'accueil pour l'étudiant (optionnel)…"),
        }),
        max_length=2000,
    )


class RefuserDemandeForm(forms.Form):
    """Formulaire de refus d'une demande."""
    message_reponse = forms.CharField(
        label=_("Motif du refus"),
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 3,
            "placeholder": _("Expliquez pourquoi vous ne pouvez pas accepter cette demande…"),
        }),
        min_length=10,
        max_length=2000,
    )


class EvaluerConseillerForm(forms.Form):
    """Formulaire de notation d'un conseiller par l'étudiant."""
    note = forms.FloatField(
        label=_("Note (0 à 5)"),
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            "class": "input_field",
            "step": "0.5",
            "min": "0",
            "max": "5",
        }),
    )
    commentaire = forms.CharField(
        label=_("Commentaire (optionnel)"),
        required=False,
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 4,
            "placeholder": _("Partagez votre expérience avec ce conseiller…"),
        }),
        max_length=2000,
    )


class QuestionProposeeForm(forms.ModelForm):
    """Formulaire de proposition d'une question par un conseiller."""

    class Meta:
        model = QuestionProposee
        fields = [
            "texte", "explication", "type", "dimensions",
            "poids", "contexte_situation", "justification_proposition", "test_cible",
        ]
        widgets = {
            "texte": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 3,
                "placeholder": _("Texte complet de la question…"),
            }),
            "explication": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 2,
                "placeholder": _("Aide ou contexte affiché à l'étudiant…"),
            }),
            "type": forms.Select(attrs={"class": "input_field"}),
            "dimensions": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 2,
                "placeholder": _('Ex: {"R": 0.8, "I": 0.5}'),
            }),
            "poids": forms.NumberInput(attrs={"class": "input_field", "step": "0.1", "min": "0"}),
            "contexte_situation": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 2,
                "placeholder": _("Décrivez la situation mise en scène…"),
            }),
            "justification_proposition": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 3,
                "placeholder": _("Pourquoi proposez-vous cette question ?"),
            }),
            "test_cible": forms.Select(attrs={"class": "input_field"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import TestOrientation
        self.fields["test_cible"].queryset = TestOrientation.objects.filter(is_active=True).order_by("nom")
        self.fields["test_cible"].required = False
        self.fields["test_cible"].empty_label = _("— Laisser l'admin décider —")

    def clean_dimensions(self):
        import json
        val = self.cleaned_data.get("dimensions")
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if not isinstance(parsed, dict):
                    raise forms.ValidationError(_("Les dimensions doivent être un objet JSON."))
                return parsed
            except json.JSONDecodeError:
                raise forms.ValidationError(_("Format JSON invalide. Ex: {\"R\": 0.8, \"I\": 0.5}"))
        return val


class RendezVousForm(forms.ModelForm):
    """Proposition d'un rendez-vous dans une session d'accompagnement."""

    DUREES = [(15, "15 min"), (30, "30 min"), (45, "45 min"), (60, "1 h"), (90, "1 h 30")]

    class Meta:
        from .models.rdv import RendezVous
        model = RendezVous
        fields = ["date_rdv", "duree_minutes", "format", "lien_visio", "adresse", "notes"]
        widgets = {
            "date_rdv": forms.DateTimeInput(
                attrs={"class": "input_field", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "format": forms.Select(attrs={"class": "input_field"}),
            "lien_visio": forms.URLInput(attrs={"class": "input_field", "placeholder": "https://meet.google.com/…"}),
            "adresse": forms.TextInput(attrs={"class": "input_field", "placeholder": "Adresse du lieu de rencontre"}),
            "notes": forms.Textarea(attrs={"class": "input_field", "rows": 3, "placeholder": "Points à aborder, documents à préparer…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["duree_minutes"].widget = forms.Select(
            attrs={"class": "input_field"},
            choices=self.DUREES,
        )
        self.fields["lien_visio"].required = False
        self.fields["adresse"].required = False
        self.fields["notes"].required = False
        # Format datetime-local
        self.fields["date_rdv"].input_formats = ["%Y-%m-%dT%H:%M"]


class AnnulerRdvForm(forms.Form):
    """Formulaire optionnel pour le motif d'annulation d'un RDV."""
    motif_annulation = forms.CharField(
        label=_("Motif (optionnel)"),
        required=False,
        widget=forms.Textarea(attrs={"class": "input_field", "rows": 2, "placeholder": "Raison de l'annulation…"}),
        max_length=500,
    )


class RejeterQuestionForm(forms.Form):
    """Formulaire de rejet d'une question proposée (admin)."""
    motif_rejet = forms.CharField(
        label=_("Motif du rejet"),
        min_length=10,
        widget=forms.Textarea(attrs={
            "class": "input_field",
            "rows": 3,
            "placeholder": _("Expliquez pourquoi cette question ne peut pas être intégrée…"),
        }),
    )
