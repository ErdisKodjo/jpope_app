from django import forms
from .models import Thread, MessageForum


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ["titre", "contenu"]
        widgets = {
            "titre": forms.TextInput(attrs={
                "class": "input_field",
                "placeholder": "Titre de votre discussion...",
            }),
            "contenu": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 6,
                "placeholder": "Décrivez votre sujet en détail...",
            }),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = MessageForum
        fields = ["contenu"]
        widgets = {
            "contenu": forms.Textarea(attrs={
                "class": "input_field",
                "rows": 4,
                "placeholder": "Votre réponse...",
            }),
        }
