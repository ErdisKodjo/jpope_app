"""
Modèles RGPD pour AvenSU-Orienta.

Conformément au cahier des charges (section 3 — Sécurité et Confidentialité) :
- Conformité stricte RGPD, notamment pour les mineurs
- Chiffrement de bout en bout des données sensibles
- Droit d'accès, rectification, effacement, portabilité

Modèles implémentés :
1. ConsentementRGPD — trace chaque consentement explicite de l'utilisateur
2. DemandeRGPD — demande d'accès / rectification / suppression / portabilité
3. JournalTraitement — journal des traitements de données (audit)
4. PolitiqueConservation — règles de conservation par type de donnée
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TypeConsentement(models.TextChoices):
    """Types de consentement RGPD tracés dans la plateforme."""
    INSCRIPTION = "INSCRIPTION", _("Inscription à la plateforme")
    TEST_ORIENTATION = "TEST_ORIENTATION", _("Passation d'un test d'orientation")
    PARTAGE_CONSEILLER = "PARTAGE_CONSEILLER", _("Partage de données avec un conseiller")
    PARTAGE_ETABLISSEMENT = "PARTAGE_ETABLISSEMENT", _("Partage de données avec un établissement")
    COMMUNICATION_MARKETING = "MARKETING", _("Recevoir des communications marketing")
    PROFILAGE_IA = "PROFILAGE_IA", _("Utilisation de l'IA pour recommandations personnalisées")
    MESSAGERIE = "MESSAGERIE", _("Utilisation de la messagerie interne")
    PARENTAL = "PARENTAL", _("Consentement parental pour mineur")
    COOKIES = "COOKIES", _("Acceptation des cookies non essentiels")
    ANALYTICS = "ANALYTICS", _("Collecte de données d'analytics")


class StatutConsentement(models.TextChoices):
    ACTIVE = "ACTIVE", _("Actif")
    RETIRE = "RETIRE", _("Retiré")
    EXPIRE = "EXPIRE", _("Expiré")


class ConsentementRGPD(models.Model):
    """
    Trace chaque consentement explicite donné par un utilisateur.
    Conformément à l'art. 7 du RGPD : "Preuve du consentement".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consentements",
        verbose_name=_("utilisateur"),
    )
    type = models.CharField(
        _("type de consentement"),
        max_length=30,
        choices=TypeConsentement.choices,
        db_index=True,
    )
    statut = models.CharField(
        _("statut"),
        max_length=10,
        choices=StatutConsentement.choices,
        default=StatutConsentement.ACTIVE,
    )
    # Texte exact présenté à l'utilisateur au moment du consentement
    texte_consentement = models.TextField(
        _("texte du consentement"),
        help_text=_("Version exacte du texte accepté par l'utilisateur"),
    )
    version_politique = models.CharField(
        _("version de la politique de confidentialité"),
        max_length=20,
        default="1.0",
    )
    # Métadonnées de preuve
    date_consentement = models.DateTimeField(_("date du consentement"), auto_now_add=True)
    date_retrait = models.DateTimeField(_("date de retrait"), blank=True, null=True)
    ip_consentement = models.GenericIPAddressField(
        _("IP au moment du consentement"),
        blank=True,
        null=True,
    )
    user_agent = models.CharField(
        _("User-Agent"),
        max_length=512,
        blank=True,
    )
    # Lien parent si consentement parental pour mineur
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consentements_parentaux_donnes",
        verbose_name=_("parent/tuteur"),
    )

    class Meta:
        verbose_name = _("consentement RGPD")
        verbose_name_plural = _("consentements RGPD")
        ordering = ["-date_consentement"]
        indexes = [
            models.Index(fields=["utilisateur", "type", "statut"]),
            models.Index(fields=["date_consentement"]),
        ]

    def __str__(self):
        return f"{self.utilisateur.email} — {self.get_type_display()} ({self.statut})"

    def retirer(self):
        """Marque le consentement comme retiré."""
        self.statut = StatutConsentement.RETIRE
        self.date_retrait = timezone.now()
        self.save(update_fields=["statut", "date_retrait"])


class TypeDemandeRGPD(models.TextChoices):
    ACCES = "ACCES", _("Droit d'accès (art. 15)")
    RECTIFICATION = "RECTIFICATION", _("Droit de rectification (art. 16)")
    EFFACEMENT = "EFFACEMENT", _("Droit à l'oubli (art. 17)")
    LIMITATION = "LIMITATION", _("Limitation du traitement (art. 18)")
    PORTABILITE = "PORTABILITE", _("Portabilité des données (art. 20)")
    OPPOSITION = "OPPOSITION", _("Opposition au traitement (art. 21)")


class StatutDemandeRGPD(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente de traitement")
    EN_COURS = "EN_COURS", _("En cours de traitement")
    TRAITEE = "TRAITEE", _("Traitée")
    REFUSEE = "REFUSEE", _("Refusée (motif légal)")


class DemandeRGPD(models.Model):
    """
    Demande exercée par un utilisateur dans le cadre de ses droits RGPD.
    Conformément au cahier des charges : export/suppression des données.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(
        _("référence"),
        max_length=32,
        unique=True,
        editable=False,
        help_text=_("Référence unique de la demande (ex: RGPD-2026-001234)"),
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="demandes_rgpd",
        verbose_name=_("utilisateur"),
    )
    type = models.CharField(
        _("type de demande"),
        max_length=20,
        choices=TypeDemandeRGPD.choices,
    )
    statut = models.CharField(
        _("statut"),
        max_length=15,
        choices=StatutDemandeRGPD.choices,
        default=StatutDemandeRGPD.EN_ATTENTE,
    )
    # Détails
    motif = models.TextField(
        _("motif / précisions"),
        blank=True,
        help_text=_("Précisions apportées par l'utilisateur (notamment pour rectification/effacement)"),
    )
    motif_refus = models.TextField(
        _("motif de refus"),
        blank=True,
        help_text=_("Rempli par le DPO si la demande est refusée pour motif légal"),
    )
    # Données demandées (pour ACCES / PORTABILITE)
    donnees_exportees = models.JSONField(
        _("données exportées"),
        default=dict,
        blank=True,
        help_text=_("Snapshot JSON des données au moment du traitement"),
    )
    fichier_export_url = models.URLField(
        _("URL du fichier d'export"),
        blank=True,
        help_text=_("Lien signé temporaire vers le fichier ZIP d'export"),
    )
    # Traitement
    traitee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demandes_rgpd_traitees",
        verbose_name=_("traitée par"),
    )
    date_creation = models.DateTimeField(_("date de création"), auto_now_add=True)
    date_traitement = models.DateTimeField(_("date de traitement"), blank=True, null=True)
    # Délai légal RGPD : 1 mois (art. 12.3)
    date_limite = models.DateTimeField(
        _("date limite de réponse"),
        help_text=_("Délai légal d'1 mois à compter de la demande"),
    )

    class Meta:
        verbose_name = _("demande RGPD")
        verbose_name_plural = _("demandes RGPD")
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["utilisateur", "statut"]),
            models.Index(fields=["date_limite"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.utilisateur.email} — {self.get_type_display()}"

    def save(self, *args, **kwargs):
        if not self.reference:
            # Génère une référence unique de type RGPD-YYYY-NNNNNN
            year = timezone.now().year
            count = DemandeRGPD.objects.filter(
                date_creation__year=year
            ).count() + 1
            self.reference = f"RGPD-{year}-{count:06d}"
        if not self.date_limite:
            from datetime import timedelta
            self.date_limite = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)


class CategorieDonnee(models.TextChoices):
    """Catégories de données à conserver avec politique de rétention."""
    IDENTITE = "IDENTITE", _("Identité (nom, email, téléphone)")
    SCOLAIRE = "SCOLAIRE", _("Données scolaires (notes, bulletins)")
    ORIENTATION = "ORIENTATION", _("Tests d'orientation et résultats")
    MESSAGERIE = "MESSAGERIE", _("Messages et conversations")
    COMMUNAUTE = "COMMUNAUTE", _("Posts et contributions communautaires")
    FINANCIERE = "FINANCIERE", _("Données financières (paiements)")
    ANALYTICS = "ANALYTICS", _("Données d'analytics et logs")
    DOCUMENTS = "DOCUMENTS", _("Documents vérification (CNI, diplômes)")


class PolitiqueConservation(models.Model):
    """
    Définit combien de temps chaque type de donnée est conservé.
    Permet l'application automatique des règles de rétention.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categorie = models.CharField(
        _("catégorie de donnée"),
        max_length=20,
        choices=CategorieDonnee.choices,
        unique=True,
    )
    duree_conservation_jours = models.PositiveIntegerField(
        _("durée de conservation (jours)"),
        help_text=_("Durée à compter de la dernière activité de l'utilisateur"),
    )
    description = models.TextField(_("description"))
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("politique de conservation")
        verbose_name_plural = _("politiques de conservation")

    def __str__(self):
        years = self.duree_conservation_jours // 365
        months = (self.duree_conservation_jours % 365) // 30
        parts = []
        if years:
            parts.append(f"{years} an(s)")
        if months:
            parts.append(f"{months} mois")
        return f"{self.get_categorie_display()} — {', '.join(parts) or f'{self.duree_conservation_jours} jours'}"


class JournalTraitement(models.Model):
    """
    Journal d'audit des accès et traitements de données personnelles.
    Conformément à l'art. 30 du RGPD (registre des activités de traitement).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    acteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions_traitement_rgpd",
        verbose_name=_("acteur"),
    )
    cible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donnees_accedees_par",
        verbose_name=_("données appartenant à"),
    )
    action = models.CharField(
        _("action"),
        max_length=50,
        help_text=_("Ex: ACCES, MODIFICATION, EXPORT, SUPPRESSION"),
    )
    categorie_donnee = models.CharField(
        _("catégorie de donnée"),
        max_length=20,
        choices=CategorieDonnee.choices,
    )
    details = models.JSONField(
        _("détails"),
        default=dict,
        blank=True,
        help_text=_("Détails supplémentaires (objet concerné, champs modifiés, etc.)"),
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = _("entrée du journal de traitement")
        verbose_name_plural = _("entrées du journal de traitement")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["cible", "timestamp"]),
            models.Index(fields=["acteur", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.timestamp} — {self.acteur} → {self.cible} ({self.action})"
