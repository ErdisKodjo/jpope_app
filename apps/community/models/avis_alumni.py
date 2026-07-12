"""
Modèle AvisAlumni — avis certifiés d'anciens élèves sur les établissements.

Cahier des charges (section 2.2 — Établissement, Classement et Évaluation) :
"Avis certifiés des anciens élèves (alumni)."

Un avis est "certifié" si :
- L'auteur a un compte avec rôle STUDENT ou PARENT
- L'auteur a effectivement été inscrit dans l'établissement (vérification via document
  ou via vérification manuelle par l'établissement)
- Le statut "is_certified" est validé par l'admin ou par l'établissement lui-même
"""
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class StatutAvis(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente de vérification")
    CERTIFIE = "CERTIFIE", _("Certifié (alumni vérifié)")
    REFUSE = "REFUSE", _("Refusé (non vérifiable)")
    SIGNALE = "SIGNALE", _("Signalé (modération)")


class AvisAlumni(models.Model):
    """
    Avis d'un alumni sur un établissement.
    Seuls les avis "certifiés" sont affichés publiquement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.CASCADE,
        related_name="avis_alumni",
        verbose_name=_("établissement"),
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avis_alumni_donnes",
        verbose_name=_("auteur (alumni)"),
    )

    # Période d'étude dans l'établissement (preuve)
    annee_entree = models.PositiveIntegerField(
        _("année d'entrée"),
        help_text=_("Année d'inscription dans l'établissement"),
    )
    annee_sortie = models.PositiveIntegerField(
        _("année de sortie"),
        help_text=_("Année d'obtention du diplôme ou de départ"),
    )
    formation_suivie = models.CharField(
        _("formation suivie"),
        max_length=255,
        blank=True,
        help_text=_("Nom de la formation/diplôme"),
    )
    diplome_obtenu = models.BooleanField(
        _("diplôme obtenu"),
        default=True,
    )

    # Notes (0-5 étoiles)
    note_globale = models.FloatField(
        _("note globale"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    note_enseignement = models.FloatField(
        _("qualité de l'enseignement"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=3.0,
    )
    note_infrastructures = models.FloatField(
        _("infrastructures"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=3.0,
    )
    note_vie_etudiante = models.FloatField(
        _("vie étudiante"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=3.0,
    )
    note_insertion_pro = models.FloatField(
        _("insertion professionnelle"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=3.0,
    )

    # Témoignage
    titre = models.CharField(_("titre"), max_length=255)
    contenu = models.TextField(
        _("contenu"),
        help_text=_("Témoignage détaillé de l'expérience dans l'établissement"),
    )
    points_forts = models.TextField(
        _("points forts"),
        blank=True,
        help_text=_("Ce que vous avez apprécié"),
    )
    points_faibles = models.TextField(
        _("points faibles"),
        blank=True,
        help_text=_("Ce qui peut être amélioré"),
    )

    # Recommandation
    recommande = models.BooleanField(
        _("recommande cet établissement"),
        default=True,
    )

    # Après l'établissement
    situation_actuelle = models.CharField(
        _("situation actuelle"),
        max_length=255,
        blank=True,
        help_text=_("Ex: 'En poste chez Google', 'En thèse à Paris', etc."),
    )

    # Modération et certification
    statut = models.CharField(
        _("statut"),
        max_length=15,
        choices=StatutAvis.choices,
        default=StatutAvis.EN_ATTENTE,
    )
    is_certified = models.BooleanField(
        _("certifié"),
        default=False,
        help_text=_("True si l'auteur a été vérifié comme alumni de l'établissement"),
    )
    date_certification = models.DateTimeField(blank=True, null=True)
    certifie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="avis_alumni_certifies",
        verbose_name=_("certifié par"),
    )

    # Preuves (justificatif de diplôme, etc.)
    justificatif = models.FileField(
        _("justificatif"),
        upload_to="avis_alumni/justificatifs/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Diplôme, certificat de scolarité, etc."),
    )

    # Signalements
    nombre_signalements = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("avis alumni")
        verbose_name_plural = _("avis alumni")
        ordering = ["-created_at"]
        unique_together = ("etablissement", "auteur")  # 1 avis par alumni par établissement
        indexes = [
            models.Index(fields=["etablissement", "is_certified"]),
            models.Index(fields=["statut"]),
        ]

    def __str__(self):
        return f"{self.auteur.email} → {self.etablissement.nom} ({self.note_globale}/5)"

    def certifier(self, certifie_par):
        from django.utils import timezone
        self.is_certified = True
        self.statut = StatutAvis.CERTIFIE
        self.date_certification = timezone.now()
        self.certifie_par = certifie_par
        self.save(update_fields=["is_certified", "statut", "date_certification", "certifie_par"])
