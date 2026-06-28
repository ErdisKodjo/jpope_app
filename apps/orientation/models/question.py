"""
Modèles Question et Choice (choix de réponse).
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from .enums import TypeQuestion, TypeDimension

class Question(models.Model):
    """
    Question d'un test d'orientation.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    test = models.ForeignKey(
        "orientation.TestOrientation",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("test associé"),
    )

    # Contenu
    texte = models.TextField(_("texte de la question"))
    texte_court = models.CharField(
        _("texte court (pour mobile)"),
        max_length=100,
        blank=True,
    )
    explication = models.TextField(
        _("explication / aide"),
        blank=True,
        help_text=_("Affichée si l'utilisateur demande de l'aide"),
    )
    image = models.ImageField(
        _("image illustrative"),
        upload_to="orientation/questions/%Y/",
        blank=True,
        null=True,
    )

    # Configuration
    type = models.CharField(
        _("type de question"),
        max_length=20,
        choices=TypeQuestion.choices,
        default=TypeQuestion.ECHELLE_LIKERT,
    )
    ordre = models.PositiveIntegerField(
        _("ordre dans le test"),
        default=0,
    )
    poids = models.FloatField(
        _("poids de la question"),
        default=1.0,
        validators=[MinValueValidator(0)],
        help_text=_("Multiplicateur pour le scoring"),
    )
    obligatoire = models.BooleanField(
        _("obligatoire"),
        default=True,
    )

    # Dimensions évaluées
    dimensions = models.JSONField(
        _("dimensions évaluées"),
        default=dict,
        help_text=_(
            "Mapping dimension → coefficient. "
            "Ex: {'R': 1.0, 'I': 0.5} signifie que cette question "
            "évalue la dimension Réaliste (coef 1) et Investigateur (coef 0.5)"
        ),
    )

    # Pour les questions échelle de Likert
    echelle_min = models.PositiveIntegerField(
        _("valeur min échelle"),
        default=1,
    )
    echelle_max = models.PositiveIntegerField(
        _("valeur max échelle"),
        default=5,
    )
    label_min = models.CharField(
        _("label min"),
        max_length=50,
        default="Pas du tout d'accord",
    )
    label_max = models.CharField(
        _("label max"),
        max_length=50,
        default="Tout à fait d'accord",
    )

    # Pour les questions situationnelles
    contexte = models.TextField(
        _("contexte de la situation"),
        blank=True,
    )

    # Statut
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ["test", "ordre"]
        indexes = [
            models.Index(fields=["test", "ordre"]),
        ]

    def __str__(self):
        return f"Q{self.ordre}: {self.texte[:60]}..."

    @property
    def nombre_choices(self) -> int:
        return self.choices.count()

    @property
    def dimension_principale(self) -> str | None:
        """Retourne la dimension avec le coefficient le plus élevé."""
        if not self.dimensions:
            return None
        return max(self.dimensions, key=self.dimensions.get)

class Choice(models.Model):
    """
    Choix de réponse pour une question (choix unique/multiple).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name=_("question"),
    )

    # Contenu
    texte = models.TextField(_("texte du choix"))
    ordre = models.PositiveIntegerField(_("ordre"), default=0)

    # Scoring : points attribués par dimension si ce choix est sélectionné
    scores = models.JSONField(
        _("scores par dimension"),
        default=dict,
        help_text=_(
            "Ex: {'R': 3, 'I': 1, 'S': 0} — "
            "Points ajoutés à chaque dimension si ce choix est sélectionné"
        ),
    )

    # Statut
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("choix de réponse")
        verbose_name_plural = _("choix de réponse")
        ordering = ["question", "ordre"]

    def __str__(self):
        return f"Choix: {self.texte[:50]}"
