"""
Modèles Marketing & CRM pour les Établissements.

Conformément au cahier des charges (section 2.2 — Établissement) :
- Outils marketing : Interface de création de campagnes ciblées permettant de mettre
  en avant l'établissement auprès de profils de candidats spécifiques
  (selon la région, les notes ou les résultats des tests d'orientation)
- Gestion des Demandes d'Admission : Système de suivi des dossiers (CRM) pour
  accepter, rejeter ou mettre en attente les candidats
- Modèle au Lead Qualifié : Facturation à la performance lorsque l'établissement
  initie un contact direct avec un candidat dont le profil correspond exactement
  à ses critères de recherche

Modèles :
1. SegmentCandidats — critères de ciblage (région, notes, RIASEC, niveau)
2. CampagneMarketing — campagne d'un établissement
3. LeadQualifie — lead qualifié (candidat correspondant à un segment)
4. CandidatureCRM — candidature gérée par l'établissement (CRM)
5. LogInteractionCRM — historique des interactions établissement ↔ candidat
"""
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class StatutCampagne(models.TextChoices):
    BROUILLON = "BROUILLON", _("Brouillon")
    ACTIVE = "ACTIVE", _("Active")
    PAUSE = "PAUSE", _("En pause")
    TERMINEE = "TERMINEE", _("Terminée")
    ANNULEE = "ANNULEE", _("Annulée")


class StatutLead(models.TextChoices):
    NOUVEAU = "NOUVEAU", _("Nouveau")
    CONTACTE = "CONTACTE", _("Contacté")
    INTERESSE = "INTERESSE", _("Intéressé")
    QUALIFIE = "QUALIFIE", _("Qualifié")
    CONVERTI = "CONVERTI", _("Converti (candidature)")
    REFUSE = "REFUSE", _("Refusé")
    INJOIGNABLE = "INJOIGNABLE", _("Injoignable")


class StatutCandidatureCRM(models.TextChoices):
    """Statut de la candidature dans le CRM de l'établissement."""
    RECUE = "RECUE", _("Reçue")
    EN_REVUE = "EN_REVUE", _("En revue")
    ACCEPTEE = "ACCEPTEE", _("Acceptée")
    REFUSEE = "REFUSEE", _("Refusée")
    EN_ATTENTE = "EN_ATTENTE", _("En attente (liste complémentaire)")
    INSCRIT = "INSCRIT", _("Inscrit administrativement")
    DESISTE = "DESISTE", _("Désisté")


class TypeInteraction(models.TextChoices):
    """Types d'interactions dans le CRM."""
    EMAIL = "EMAIL", _("Email")
    APPEL = "APPEL", _("Appel téléphonique")
    SMS = "SMS", _("SMS")
    MESSAGE_INTERNE = "MESSAGE_INTERNE", _("Message interne")
    VISIO = "VISIO", _("Visioconférence")
    PRESENTIEL = "PRESENTIEL", _("Rencontre présentiel")
    NOTE_INTERNE = "NOTE_INTERNE", _("Note interne")


class SegmentCandidats(models.Model):
    """
    Définition d'un segment de candidats pour ciblage marketing.
    Conformément au cahier des charges : "selon la région, les notes ou les résultats
    des tests d'orientation".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(_("nom du segment"), max_length=200)
    description = models.TextField(blank=True)

    # Critères démographiques
    regions = models.JSONField(
        _("régions ciblées"),
        default=list,
        blank=True,
        help_text=_("Liste de régions/villes. Ex: ['Lomé', 'Kara', 'Sokodé']"),
    )
    pays = models.JSONField(
        _("pays ciblés"),
        default=list,
        blank=True,
    )

    # Critères académiques
    moyenne_min = models.FloatField(
        _("moyenne minimale"),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    moyenne_max = models.FloatField(
        _("moyenne maximale"),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    niveau_actuel = models.JSONField(
        _("niveaux scolaires ciblés"),
        default=list,
        blank=True,
        help_text=_("Ex: ['TERMINALE', 'POST_BAC']"),
    )
    series_bac = models.JSONField(
        _("séries de bac ciblées"),
        default=list,
        blank=True,
        help_text=_("Ex: ['C', 'D', 'G2']"),
    )

    # Critères d'orientation
    code_riasec_cible = models.JSONField(
        _("codes RIASEC ciblés"),
        default=list,
        blank=True,
        help_text=_("Ex: ['RIA', 'SAE'] — candidats dont le profil contient ces codes"),
    )
    domaines_interet = models.JSONField(
        _("domaines d'intérêt"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Informatique', 'Santé']"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("segment de candidats")
        verbose_name_plural = _("segments de candidats")
        ordering = ["-created_at"]

    def __str__(self):
        return self.nom


class CampagneMarketing(models.Model):
    """
    Campagne marketing d'un établissement ciblant un segment de candidats.
    Conformément au cahier des charges : "mettre en avant l'établissement auprès de
    profils de candidats spécifiques".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.CASCADE,
        related_name="campagnes_marketing",
        verbose_name=_("établissement"),
    )
    nom = models.CharField(_("nom de la campagne"), max_length=200)
    description = models.TextField(blank=True)

    # Ciblage
    segment = models.ForeignKey(
        SegmentCandidats,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campagnes",
        verbose_name=_("segment ciblé"),
    )

    # Contenu
    message_principal = models.TextField(
        _("message principal"),
        help_text=_("Message affiché aux candidats ciblés"),
    )
    appel_action = models.CharField(
        _("appel à l'action"),
        max_length=255,
        help_text=_("Ex: 'Postulez avant le 30 juin'"),
    )
    url_destination = models.URLField(
        _("URL de destination"),
        blank=True,
        help_text=_("Page vers laquelle le candidat est redirigé"),
    )
    visuel = models.ImageField(
        _("visuel"),
        upload_to="marketing/visuels/%Y/%m/",
        blank=True,
        null=True,
    )

    # Période
    date_debut = models.DateTimeField(_("date de début"))
    date_fin = models.DateTimeField(_("date de fin"))
    statut = models.CharField(
        _("statut"),
        max_length=15,
        choices=StatutCampagne.choices,
        default=StatutCampagne.BROUILLON,
    )

    # Budget & tarification (Modèle au Lead Qualifié)
    budget_fcfa = models.DecimalField(
        _("budget (FCFA)"),
        max_digits=12,
        decimal_places=0,
        default=0,
    )
    cout_par_lead_qualifie = models.DecimalField(
        _("coût par lead qualifié (FCFA)"),
        max_digits=10,
        decimal_places=0,
        default=500,
        help_text=_("Montant facturé pour chaque lead qualifié (contact initié)"),
    )

    # Stats calculées
    vues = models.PositiveIntegerField(default=0)
    clics = models.PositiveIntegerField(default=0)
    leads_generes = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("campagne marketing")
        verbose_name_plural = _("campagnes marketing")
        ordering = ["-date_debut"]
        indexes = [
            models.Index(fields=["etablissement", "statut"]),
            models.Index(fields=["date_debut", "date_fin"]),
        ]

    def __str__(self):
        return f"{self.etablissement} — {self.nom} ({self.statut})"

    @property
    def is_active_now(self):
        now = timezone.now()
        return self.statut == StatutCampagne.ACTIVE and self.date_debut <= now <= self.date_fin

    @property
    def taux_conversion(self):
        if self.leads_generes == 0:
            return 0
        return round((self.conversions / self.leads_generes) * 100, 1)


class LeadQualifie(models.Model):
    """
    Lead qualifié : candidat dont le profil correspond à un segment ciblé par une campagne.
    Conformément au cahier des charges : "Facturation à la performance lorsque
    l'établissement initie un contact direct avec un candidat dont le profil correspond
    exactement à ses critères de recherche".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campagne = models.ForeignKey(
        CampagneMarketing,
        on_delete=models.CASCADE,
        related_name="leads",
    )
    candidat = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leads_recus",
        verbose_name=_("candidat"),
    )

    # Score de matching (qualité du lead)
    score_matching = models.FloatField(
        _("score de matching"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Pourcentage de correspondance avec le segment ciblé"),
    )
    critères_matches = models.JSONField(
        _("critères matchés"),
        default=dict,
        help_text=_("Détail des critères qui matchent : {'region': True, 'moyenne': 14.5, ...}"),
    )

    # Statut du lead
    statut = models.CharField(
        _("statut"),
        max_length=15,
        choices=StatutLead.choices,
        default=StatutLead.NOUVEAU,
    )

    # Facturation
    is_facture = models.BooleanField(
        _("facturé"),
        default=False,
        help_text=_("True si l'établissement a initié un contact (facturation au lead)"),
    )
    date_facturation = models.DateTimeField(blank=True, null=True)
    montant_facture = models.DecimalField(
        _("montant facturé"),
        max_digits=10,
        decimal_places=0,
        default=0,
    )

    # Dates
    date_generation = models.DateTimeField(auto_now_add=True)
    date_premier_contact = models.DateTimeField(blank=True, null=True)
    date_conversion = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("lead qualifié")
        verbose_name_plural = _("leads qualifiés")
        ordering = ["-date_generation"]
        unique_together = ("campagne", "candidat")
        indexes = [
            models.Index(fields=["campagne", "statut"]),
            models.Index(fields=["candidat", "-date_generation"]),
        ]

    def __str__(self):
        return f"Lead {self.candidat.email} → {self.campagne.etablissement} ({self.statut})"


class CandidatureCRM(models.Model):
    """
    Candidature gérée dans le CRM de l'établissement.
    Conformément au cahier des charges : "Système de suivi des dossiers (CRM) pour
    accepter, rejeter ou mettre en attente les candidats".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.CASCADE,
        related_name="candidatures_crm",
        verbose_name=_("établissement"),
    )
    candidat = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidatures_crm",
        verbose_name=_("candidat"),
    )
    formation = models.ForeignKey(
        "catalog.Formation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="candidatures_crm",
        verbose_name=_("formation visée"),
    )

    # Statut
    statut = models.CharField(
        _("statut"),
        max_length=15,
        choices=StatutCandidatureCRM.choices,
        default=StatutCandidatureCRM.RECUE,
    )

    # Évaluation
    note_interne = models.TextField(
        _("note interne"),
        blank=True,
        help_text=_("Évaluation interne de l'établissement (non visible par le candidat)"),
    )
    score_evaluation = models.FloatField(
        _("score d'évaluation"),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Score attribué par l'établissement au dossier"),
    )
    commentaire_etablissement = models.TextField(blank=True)
    motif_refus = models.TextField(
        _("motif de refus"),
        blank=True,
    )

    # Synchronisation API externe (cahier des charges : "synchronisation optionnelle via API")
    external_application_id = models.CharField(
        _("ID application externe"),
        max_length=100,
        blank=True,
        help_text=_("ID dans le système de gestion interne de l'établissement"),
    )
    is_synced_external = models.BooleanField(
        _("synchronisé à l'externe"),
        default=False,
    )
    last_sync_at = models.DateTimeField(blank=True, null=True)

    # Dates clés
    date_reception = models.DateTimeField(auto_now_add=True)
    date_decision = models.DateTimeField(blank=True, null=True)
    date_inscription = models.DateTimeField(blank=True, null=True)

    # Lien avec un lead marketing (si applicable)
    lead_source = models.ForeignKey(
        LeadQualifie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="candidatures_generees",
        verbose_name=_("lead source"),
    )

    class Meta:
        verbose_name = _("candidature CRM")
        verbose_name_plural = _("candidatures CRM")
        ordering = ["-date_reception"]
        indexes = [
            models.Index(fields=["etablissement", "statut"]),
            models.Index(fields=["candidat", "-date_reception"]),
        ]

    def __str__(self):
        return f"{self.candidat.email} → {self.etablissement} ({self.statut})"


class LogInteractionCRM(models.Model):
    """
    Historique des interactions entre l'établissement et le candidat dans le CRM.
    Conformément au cahier des charges : audit et traçabilité des actions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidature = models.ForeignKey(
        CandidatureCRM,
        on_delete=models.CASCADE,
        related_name="interactions",
        verbose_name=_("candidature"),
    )
    type = models.CharField(
        _("type d'interaction"),
        max_length=20,
        choices=TypeInteraction.choices,
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interactions_crm_initiees",
        verbose_name=_("auteur"),
    )
    sujet = models.CharField(_("sujet"), max_length=255, blank=True)
    contenu = models.TextField()
    date_interaction = models.DateTimeField(auto_now_add=True)
    is_automatique = models.BooleanField(
        _("automatique"),
        default=False,
        help_text=_("True si l'interaction a été générée automatiquement"),
    )

    class Meta:
        verbose_name = _("log d'interaction CRM")
        verbose_name_plural = _("logs d'interactions CRM")
        ordering = ["-date_interaction"]
