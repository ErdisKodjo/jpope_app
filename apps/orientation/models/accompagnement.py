"""
Modèles pour le système d'accompagnement conseiller.

Flux : Etudiant demande → Conseiller accepte → Échange messages → Clôture + Note → Ristourne
"""
import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import StatutDemande, StatutQuestionProposee


class DemandeAccompagnement(models.Model):
    """
    Demande d'un étudiant pour être accompagné par un conseiller.
    Peut être liée à un résultat de test pour donner du contexte au conseiller.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="demandes_accompagnement",
        limit_choices_to={"role": "STUDENT"},
        verbose_name=_("étudiant"),
    )
    conseiller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accompagnements_recus",
        limit_choices_to={"role": "COUNSELOR"},
        verbose_name=_("conseiller"),
    )
    resultat_test = models.ForeignKey(
        "orientation.ResultatTest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demandes_accompagnement",
        verbose_name=_("résultat de test associé"),
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutDemande.choices,
        default=StatutDemande.EN_ATTENTE,
        db_index=True,
    )

    # Demande de l'étudiant
    motif = models.TextField(
        _("motif de la demande"),
        help_text=_("Expliquez pourquoi vous avez besoin d'accompagnement"),
    )
    domaines_concernes = models.JSONField(
        _("domaines concernés"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Informatique', 'Gestion']"),
    )

    # Réponse du conseiller
    message_reponse = models.TextField(
        _("message de réponse"),
        blank=True,
        help_text=_("Réponse du conseiller lors de l'acceptation ou du refus"),
    )

    # Évaluation finale (après clôture)
    note_conseiller = models.FloatField(
        _("note du conseiller (0-5)"),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    commentaire_note = models.TextField(
        _("commentaire sur la note"),
        blank=True,
    )

    # Ristourne
    ristourne_generee = models.BooleanField(
        _("ristourne générée"),
        default=False,
    )

    # Timestamps
    date_demande = models.DateTimeField(_("date de la demande"), auto_now_add=True)
    date_reponse = models.DateTimeField(_("date de réponse"), null=True, blank=True)
    date_debut = models.DateTimeField(_("date de début"), null=True, blank=True)
    date_fin = models.DateTimeField(_("date de clôture"), null=True, blank=True)

    class Meta:
        verbose_name = _("demande d'accompagnement")
        verbose_name_plural = _("demandes d'accompagnement")
        ordering = ["-date_demande"]
        indexes = [
            models.Index(fields=["etudiant", "statut"]),
            models.Index(fields=["conseiller", "statut"]),
        ]

    def __str__(self):
        return f"Accompagnement {self.etudiant} → {self.conseiller or 'sans conseiller'} [{self.get_statut_display()}]"

    @property
    def nb_messages(self):
        return self.messages.count()

    @property
    def dernier_message(self):
        return self.messages.order_by("-created_at").first()


class MessageAccompagnement(models.Model):
    """Message dans le cadre d'une session d'accompagnement conseiller-étudiant."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    demande = models.ForeignKey(
        DemandeAccompagnement,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("demande"),
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_accompagnement",
        verbose_name=_("auteur"),
    )
    contenu = models.TextField(_("contenu"))
    est_lu = models.BooleanField(_("lu par le destinataire"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("message d'accompagnement")
        verbose_name_plural = _("messages d'accompagnement")
        ordering = ["created_at"]

    def __str__(self):
        return f"Message de {self.auteur} [{self.created_at:%d/%m %H:%M}]"


class QuestionProposee(models.Model):
    """
    Question proposée par un conseiller pour enrichir un test d'orientation.
    Soumise à approbation de l'admin avant d'être intégrée.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conseiller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions_proposees",
        limit_choices_to={"role": "COUNSELOR"},
        verbose_name=_("conseiller proposant"),
    )
    test_cible = models.ForeignKey(
        "orientation.TestOrientation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions_proposees",
        verbose_name=_("test cible"),
        help_text=_("Test dans lequel intégrer la question (optionnel)"),
    )

    # Contenu de la question
    texte = models.TextField(_("texte de la question"))
    explication = models.TextField(
        _("explication / contexte"),
        blank=True,
        help_text=_("Aide pour l'étudiant ou contexte de la question"),
    )
    type = models.CharField(
        _("type de question"),
        max_length=20,
        choices=[
            ("ECHELLE_LIKERT", _("Échelle de Likert (1-5)")),
            ("CHOIX_UNIQUE", _("Choix unique")),
            ("CHOIX_MULTIPLE", _("Choix multiple")),
            ("SITUATIONNELLE", _("Mise en situation")),
        ],
        default="ECHELLE_LIKERT",
    )
    dimensions = models.JSONField(
        _("dimensions évaluées"),
        default=dict,
        help_text=_("Ex: {'R': 0.8, 'I': 0.5} — dimension RIASEC et son coefficient"),
    )
    poids = models.FloatField(
        _("poids de la question"),
        default=1.0,
        validators=[MinValueValidator(0)],
    )
    contexte_situation = models.TextField(
        _("contexte de la situation"),
        blank=True,
        help_text=_("Pour les questions situationnelles uniquement"),
    )

    # Justification du conseiller
    justification_proposition = models.TextField(
        _("justification de la proposition"),
        blank=True,
        help_text=_("Pourquoi cette question est pertinente pour les étudiants"),
    )

    # Traitement admin
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutQuestionProposee.choices,
        default=StatutQuestionProposee.EN_ATTENTE,
        db_index=True,
    )
    motif_rejet = models.TextField(
        _("motif du rejet"),
        blank=True,
    )
    question_creee = models.OneToOneField(
        "orientation.Question",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="depuis_proposition",
        verbose_name=_("question créée"),
    )
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions_traitees",
        limit_choices_to={"role": "ADMIN"},
        verbose_name=_("traité par"),
    )

    # Timestamps
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("question proposée")
        verbose_name_plural = _("questions proposées")
        ordering = ["-date_soumission"]
        indexes = [
            models.Index(fields=["statut"]),
            models.Index(fields=["conseiller", "statut"]),
        ]

    def __str__(self):
        return f"Question de {self.conseiller} [{self.get_statut_display()}] : {self.texte[:60]}…"
