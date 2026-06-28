"""
Modèles ProfilMentor, RelationMentorat, SeanceMentorat — système de mentorat.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import StatutMentorat, TypeMentor


class ProfilMentor(models.Model):
    """
    Profil de mentor — utilisateur proposant ses services de mentorat.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    utilisateur = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="profil_mentor",
        verbose_name=_("utilisateur"),
    )

    type_mentor = models.CharField(
        _("type de mentor"),
        max_length=20,
        choices=TypeMentor.choices,
        default=TypeMentor.PAIR,
    )

    bio = models.TextField(
        _("biographie"),
        blank=True,
        help_text=_("Présentation du mentor et de son parcours"),
    )
    domaines_expertise = models.JSONField(
        _("domaines d'expertise"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Informatique', 'Gestion', 'Médecine']"),
    )
    competences = models.JSONField(
        _("compétences"),
        default=list,
        blank=True,
    )
    annees_experience = models.PositiveIntegerField(
        _("années d'expérience"),
        default=0,
    )
    diplomes = models.JSONField(
        _("diplômes"),
        default=list,
        blank=True,
    )

    is_disponible = models.BooleanField(
        _("disponible pour du mentorat"),
        default=True,
    )
    nombre_mentores_max = models.PositiveIntegerField(
        _("nombre maximum de mentorés simultanés"),
        default=3,
    )
    nombre_mentores_actuels = models.PositiveIntegerField(
        _("nombre de mentorés actuels"),
        default=0,
    )
    nombre_mentores_total = models.PositiveIntegerField(
        _("nombre total de mentorés (historique)"),
        default=0,
    )

    creneaux_disponibles = models.JSONField(
        _("créneaux de disponibilité"),
        default=dict,
        blank=True,
        help_text=_("Ex: {'lundi': ['18:00-20:00'], 'samedi': ['09:00-12:00']}"),
    )
    formats_proposes = models.JSONField(
        _("formats proposés"),
        default=list,
        blank=True,
        help_text=_("Ex: ['visio', 'chat', 'présentiel']"),
    )
    langues_parlees = models.JSONField(
        _("langues parlées"),
        default=list,
        blank=True,
    )

    note_moyenne = models.FloatField(
        _("note moyenne (0-5)"),
        default=0,
    )
    nombre_evaluations = models.PositiveIntegerField(
        _("nombre d'évaluations"),
        default=0,
    )

    is_verifie = models.BooleanField(
        _("profil vérifié par l'équipe"),
        default=False,
    )
    date_verification = models.DateTimeField(
        _("date de vérification"),
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil mentor")
        verbose_name_plural = _("profils mentors")
        ordering = ["-note_moyenne", "-nombre_evaluations"]

    def __str__(self):
        return f"Mentor: {self.utilisateur.get_full_name()} ({self.get_type_mentor_display()})"

    @property
    def places_disponibles(self) -> int:
        return max(0, self.nombre_mentores_max - self.nombre_mentores_actuels)

    @property
    def peut_accepter_mentore(self) -> bool:
        return self.is_disponible and self.places_disponibles > 0


class RelationMentorat(models.Model):
    """
    Relation de mentorat entre un mentor et un mentoré.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    mentor = models.ForeignKey(
        ProfilMentor,
        on_delete=models.CASCADE,
        related_name="relations_mentorat",
        verbose_name=_("mentor"),
    )
    mentoré = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="relations_mentorat_mentore",
        verbose_name=_("mentoré"),
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutMentorat.choices,
        default=StatutMentorat.EN_ATTENTE,
    )

    motif_demande = models.TextField(
        _("motif de la demande"),
        blank=True,
    )
    objectifs = models.JSONField(
        _("objectifs du mentorat"),
        default=list,
        blank=True,
    )

    date_demande = models.DateTimeField(auto_now_add=True)
    date_reponse = models.DateTimeField(
        _("date de réponse du mentor"),
        blank=True,
        null=True,
    )
    date_debut = models.DateTimeField(
        _("date de début du mentorat"),
        blank=True,
        null=True,
    )
    date_fin = models.DateTimeField(
        _("date de fin du mentorat"),
        blank=True,
        null=True,
    )

    nombre_seances = models.PositiveIntegerField(
        _("nombre de séances effectuées"),
        default=0,
    )
    derniere_seance = models.DateTimeField(
        _("date de la dernière séance"),
        blank=True,
        null=True,
    )

    evaluation_mentore = models.FloatField(
        _("évaluation du mentor par le mentoré (0-5)"),
        blank=True,
        null=True,
    )
    evaluation_mentor = models.FloatField(
        _("évaluation du mentoré par le mentor (0-5)"),
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("relation de mentorat")
        verbose_name_plural = _("relations de mentorat")
        ordering = ["-date_demande"]
        indexes = [
            models.Index(fields=["mentor", "statut"]),
            models.Index(fields=["mentoré", "statut"]),
        ]

    def __str__(self):
        return f"{self.mentor} → {self.mentoré} ({self.get_statut_display()})"

    @property
    def duree_jours(self) -> int | None:
        if self.date_debut and self.date_fin:
            return (self.date_fin - self.date_debut).days
        return None


class SeanceMentorat(models.Model):
    """
    Séance individuelle dans le cadre d'une relation de mentorat.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    relation = models.ForeignKey(
        RelationMentorat,
        on_delete=models.CASCADE,
        related_name="seances",
        verbose_name=_("relation de mentorat"),
    )

    titre = models.CharField(_("titre"), max_length=255, blank=True)
    description = models.TextField(_("description / ordre du jour"), blank=True)

    date_prevue = models.DateTimeField(_("date prévue"))
    duree_minutes = models.PositiveIntegerField(
        _("durée (minutes)"),
        default=60,
    )
    format = models.CharField(
        _("format"),
        max_length=20,
        choices=[
            ("VISIO", "Visioconférence"),
            ("CHAT", "Chat/Messages"),
            ("PRESENTIEL", "Présentiel"),
            ("TELEPHONE", "Téléphone"),
        ],
        default="VISIO",
    )
    lien_visio = models.URLField(
        _("lien visio"),
        blank=True,
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=[
            ("PLANIFIEE", "Planifiée"),
            ("EFFECTUEE", "Effectuée"),
            ("ANNULEE", "Annulée"),
            ("REPORTEE", "Reportée"),
        ],
        default="PLANIFIEE",
    )

    compte_rendu = models.TextField(_("compte rendu"), blank=True)
    prochaines_etapes = models.JSONField(
        _("prochaines étapes"),
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("séance de mentorat")
        verbose_name_plural = _("séances de mentorat")
        ordering = ["-date_prevue"]

    def __str__(self):
        return f"Séance {self.date_prevue.strftime('%d/%m/%Y')} — {self.relation}"
