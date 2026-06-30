"""
Modèles ReponseUtilisateur et DetailReponse.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import StatutTest

class ReponseUtilisateur(models.Model):
    """
    Session de passation d'un test par un étudiant.
    Regroupe toutes les réponses d'un utilisateur pour un test donné.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Liens
    etudiant = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="reponses_tests",
        verbose_name=_("étudiant"),
        limit_choices_to={"role": "STUDENT"},
    )
    test = models.ForeignKey(
        "orientation.TestOrientation",
        on_delete=models.CASCADE,
        related_name="reponses",
        verbose_name=_("test passé"),
    )

    # État de la passation
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutTest.choices,
        default=StatutTest.EN_COURS,
    )

    # Timing
    date_debut = models.DateTimeField(_("date de début"), auto_now_add=True)
    date_fin = models.DateTimeField(_("date de fin"), blank=True, null=True)
    duree_reelle_secondes = models.PositiveIntegerField(
        _("durée réelle (secondes)"),
        default=0,
    )

    # Métriques de complétion
    nombre_questions_repondues = models.PositiveIntegerField(default=0)
    nombre_questions_total = models.PositiveIntegerField(default=0)
    progression = models.FloatField(
        _("progression (%)"),
        default=0,
    )

    # Résultats agrégés (calculés par ScoringService)
    score_global = models.FloatField(
        _("score global"),
        default=0,
    )
    profil_dominant = models.CharField(
        _("profil dominant"),
        max_length=5,
        blank=True,
        help_text=_("Code RIASEC dominant, ex: 'R', 'I', etc."),
    )
    profil_secondaire = models.CharField(
        _("profil secondaire"),
        max_length=5,
        blank=True,
    )
    code_holland = models.CharField(
        _("code profil (Holland ou multi-domaine)"),
        max_length=15,
        blank=True,
        help_text=_("Ex: 'RIA', 'SEC' ou 'N-ENV-I'"),
    )
    scores_par_dimension = models.JSONField(
        _("scores par dimension"),
        default=dict,
        help_text=_("Ex: {'R': 75, 'I': 82, 'A': 45, 'S': 68, 'E': 55, 'C': 60}"),
    )

    # Métadonnées
    appareil = models.CharField(
        _("appareil utilisé"),
        max_length=50,
        blank=True,
        help_text=_("mobile, desktop, tablette"),
    )

    class Meta:
        verbose_name = _("réponse utilisateur")
        verbose_name_plural = _("réponses utilisateurs")
        ordering = ["-date_debut"]
        indexes = [
            models.Index(fields=["etudiant", "test"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["-date_debut"]),
        ]

    def __str__(self):
        return f"{self.etudiant.get_full_name()} — {self.test.nom} ({self.statut})"

    @property
    def est_termine(self) -> bool:
        return self.statut == StatutTest.TERMINE

    @property
    def progression_formatee(self) -> str:
        return f"{self.progression:.0f}%"

class DetailReponse(models.Model):
    """
    Réponse individuelle à une question dans le cadre d'une passation.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Liens
    reponse_utilisateur = models.ForeignKey(
        ReponseUtilisateur,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name=_("session de test"),
    )
    question = models.ForeignKey(
        "orientation.Question",
        on_delete=models.CASCADE,
        related_name="details_reponses",
        verbose_name=_("question"),
    )

    # Réponse (polymorphe selon le type de question)
    choice_selectionne = models.ForeignKey(
        "orientation.Choice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="selections",
        verbose_name=_("choix sélectionné"),
    )
    choices_selectionnes = models.JSONField(
        _("choix multiples sélectionnés"),
        default=list,
        blank=True,
        help_text=_("Liste des IDs des choix pour les questions à choix multiple"),
    )
    valeur_echelle = models.PositiveIntegerField(
        _("valeur échelle (Likert)"),
        blank=True,
        null=True,
        help_text=_("Valeur de 1 à 5 pour les questions Likert"),
    )
    classement = models.JSONField(
        _("classement"),
        default=list,
        blank=True,
        help_text=_("Ordre des choix pour les questions de classement"),
    )
    reponse_ouverte = models.TextField(
        _("réponse ouverte"),
        blank=True,
    )

    # Timing
    temps_reponse_secondes = models.PositiveIntegerField(
        _("temps de réponse (secondes)"),
        default=0,
    )

    # Score calculé pour cette réponse
    score_calcule = models.JSONField(
        _("score calculé par dimension"),
        default=dict,
        blank=True,
        help_text=_("Ex: {'R': 3, 'I': 1} — Points attribués pour cette réponse"),
    )

    class Meta:
        verbose_name = _("détail de réponse")
        verbose_name_plural = _("détails de réponse")
        ordering = ["reponse_utilisateur", "question__ordre"]
        constraints = [
            models.UniqueConstraint(
                fields=["reponse_utilisateur", "question"],
                name="unique_reponse_par_question",
            )
        ]

    def __str__(self):
        return f"Réponse à '{self.question}' par {self.reponse_utilisateur.etudiant}"
