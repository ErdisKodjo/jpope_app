"""
Modèles pour l'app payments.

Inclut : Paiement (transaction simplifiée), PlanAbonnement,
         Abonnement, Transaction, Facture.
"""
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ──────────────────────────────────────────────
# Énumérations
# ──────────────────────────────────────────────

class StatutPaiement(models.TextChoices):
    PENDING = "PENDING", _("En attente")
    COMPLETED = "COMPLETED", _("Complété")
    FAILED = "FAILED", _("Échec")
    REFUNDED = "REFUNDED", _("Remboursé")


class ProviderPaiement(models.TextChoices):
    FLOOZ = "FLOOZ", _("Togocom Flooz")
    TMONEY = "TMONEY", _("T-Money")
    MOOV_MONEY = "MOOV_MONEY", _("Moov Money")
    ORANGE_MONEY = "ORANGE_MONEY", _("Orange Money")
    CARTE = "CARTE", _("Carte bancaire (Stripe)")
    VIREMENT = "VIREMENT", _("Virement bancaire")
    GRATUIT = "GRATUIT", _("Gratuit / Offre spéciale")


class StatutAbonnement(models.TextChoices):
    ACTIF = "ACTIF", _("Actif")
    EN_PERIODE_ESSAI = "ESSAI", _("En période d'essai")
    EXPIRE = "EXPIRE", _("Expiré")
    ANNULE = "ANNULE", _("Annulé")
    EN_RETARD_PAIEMENT = "RETARD", _("Retard de paiement")
    BLOQUE = "BLOQUE", _("Bloqué (impayé)")


class StatutTransaction(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente")
    INITIEE = "INITIEE", _("Initiée")
    CONFIRMEE = "CONFIRMEE", _("Confirmée / Réussie")
    ECHEC = "ECHEC", _("Échec")
    ANNULEE = "ANNULEE", _("Annulée")
    REMBOURSEE = "REMBOURSEE", _("Remboursée")
    EXPIREE = "EXPIREE", _("Expirée")


class StatutFacture(models.TextChoices):
    BROUILLON = "BROUILLON", _("Brouillon")
    EMISE = "EMISE", _("Émise")
    PAYEE = "PAYEE", _("Payée")
    EN_RETARD = "EN_RETARD", _("En retard")
    ANNULEE = "ANNULEE", _("Annulée")


# ──────────────────────────────────────────────
# Modèle simplifié Paiement (référencé dans les specs)
# ──────────────────────────────────────────────

class Paiement(models.Model):
    """
    Transaction de paiement simplifiée.
    Référence les specs : user FK, montant, devise, statut,
    provider, reference (unique), transaction_id, description,
    metadata, created_at, updated_at.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="paiements",
        verbose_name=_("utilisateur"),
    )

    montant = models.DecimalField(
        _("montant"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    devise = models.CharField(_("devise"), max_length=10, default="XOF")

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutPaiement.choices,
        default=StatutPaiement.PENDING,
    )
    provider = models.CharField(
        _("provider"),
        max_length=20,
        choices=ProviderPaiement.choices,
        default=ProviderPaiement.FLOOZ,
    )

    reference = models.CharField(
        _("référence"),
        max_length=100,
        unique=True,
        help_text=_("Référence interne unique (ex: PAY-20260627-AB12CD)"),
    )
    transaction_id = models.CharField(
        _("ID de transaction"),
        max_length=255,
        blank=True,
        help_text=_("ID retourné par l'opérateur"),
    )

    description = models.TextField(_("description"), blank=True)

    metadata = models.JSONField(
        _("métadonnées"),
        default=dict,
        blank=True,
        help_text=_("Données additionnelles (IP, user agent, etc.)"),
    )

    created_at = models.DateTimeField(_("créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("modifié le"), auto_now=True)

    class Meta:
        verbose_name = _("paiement")
        verbose_name_plural = _("paiements")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.montant} {self.devise} ({self.get_statut_display()})"

    @property
    def montant_formate(self) -> str:
        return f"{int(self.montant):,} {self.devise}".replace(",", " ")

    @property
    def est_reussi(self) -> bool:
        return self.statut == StatutPaiement.COMPLETED

    def save(self, *args, **kwargs):
        if not self.reference:
            import secrets
            today = timezone.now().strftime("%Y%m%d")
            self.reference = f"PAY-{today}-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────
# Plan d'abonnement
# ──────────────────────────────────────────────

class PlanAbonnement(models.Model):
    """Plan d'abonnement (offre commerciale)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(_("code unique"), max_length=50, unique=True)
    nom = models.CharField(_("nom"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    description_courte = models.CharField(
        _("description courte"), max_length=300, blank=True
    )

    TYPE_CHOICES = [
        ("ETUDIANT", _("Étudiant")),
        ("CONSEILLER", _("Conseiller")),
        ("ETABLISSEMENT", _("Établissement")),
        ("ENTREPRISE", _("Entreprise / Partenaire")),
    ]
    NIVEAU_CHOICES = [
        ("GRATUIT", _("Gratuit (Basic)")),
        ("STANDARD", _("Standard")),
        ("PREMIUM", _("Premium")),
        ("PRO", _("Professionnel")),
        ("ENTREPRISE", _("Entreprise")),
    ]
    FREQUENCE_CHOICES = [
        ("MENSUEL", _("Mensuel")),
        ("TRIMESTRIEL", _("Trimestriel")),
        ("SEMESTRIEL", _("Semestriel")),
        ("ANNUEL", _("Annuel")),
        ("UNIQUE", _("Paiement unique")),
    ]

    type_abonnement = models.CharField(
        _("type"), max_length=20, choices=TYPE_CHOICES, default="ETUDIANT"
    )
    niveau = models.CharField(
        _("niveau"), max_length=20, choices=NIVEAU_CHOICES, default="STANDARD"
    )
    frequence = models.CharField(
        _("fréquence"), max_length=20, choices=FREQUENCE_CHOICES, default="MENSUEL"
    )

    prix_fcfa = models.DecimalField(
        _("prix (FCFA)"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    prix_promo_fcfa = models.DecimalField(
        _("prix promotionnel (FCFA)"),
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
    )
    devise = models.CharField(_("devise"), max_length=10, default="XOF")

    periode_essai_jours = models.PositiveIntegerField(
        _("période d'essai (jours)"), default=0
    )
    duree_mois = models.PositiveIntegerField(_("durée (mois)"), default=1)

    fonctionnalites = models.JSONField(_("fonctionnalités incluses"), default=list, blank=True)
    limites = models.JSONField(_("limites d'utilisation"), default=dict, blank=True)
    avantages = models.JSONField(_("avantages mis en avant"), default=list, blank=True)

    icone = models.CharField(_("icône"), max_length=10, default="⭐")
    couleur = models.CharField(_("couleur (hex)"), max_length=7, default="#3B82F6")

    is_active = models.BooleanField(_("actif"), default=True)
    is_public = models.BooleanField(_("public"), default=True)
    is_featured = models.BooleanField(_("mis en avant"), default=False)
    ordre = models.PositiveIntegerField(_("ordre"), default=0)

    stripe_price_id = models.CharField(
        _("Stripe Price ID"), max_length=100, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("plan d'abonnement")
        verbose_name_plural = _("plans d'abonnement")
        ordering = ["type_abonnement", "ordre", "prix_fcfa"]
        indexes = [
            models.Index(fields=["type_abonnement", "niveau"]),
            models.Index(fields=["is_active", "is_public"]),
        ]

    def __str__(self):
        return f"{self.nom} ({self.prix_fcfa} FCFA/{self.get_frequence_display()})"

    @property
    def prix_actuel(self) -> int:
        if self.prix_promo_fcfa and self.prix_promo_fcfa < self.prix_fcfa:
            return int(self.prix_promo_fcfa)
        return int(self.prix_fcfa)


# ──────────────────────────────────────────────
# Abonnement utilisateur
# ──────────────────────────────────────────────

class Abonnement(models.Model):
    """Abonnement actif d'un utilisateur à un plan."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="abonnements",
        verbose_name=_("utilisateur"),
    )
    plan = models.ForeignKey(
        PlanAbonnement,
        on_delete=models.PROTECT,
        related_name="abonnements",
        verbose_name=_("plan"),
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutAbonnement.choices,
        default=StatutAbonnement.ACTIF,
    )

    date_debut = models.DateTimeField(_("date de début"))
    date_fin = models.DateTimeField(_("date de fin"))
    date_essai_fin = models.DateTimeField(_("fin d'essai"), blank=True, null=True)
    date_annulation = models.DateTimeField(_("date annulation"), blank=True, null=True)
    date_dernier_paiement = models.DateTimeField(
        _("date dernier paiement"), blank=True, null=True
    )

    renouvellement_auto = models.BooleanField(
        _("renouvellement automatique"), default=True
    )
    methode_paiement_defaut = models.CharField(
        _("méthode paiement défaut"), max_length=20, blank=True
    )
    stripe_subscription_id = models.CharField(
        _("Stripe Subscription ID"), max_length=100, blank=True
    )

    consommation_courante = models.JSONField(
        _("consommation courante"), default=dict, blank=True
    )
    date_reset_consommation = models.DateTimeField(
        _("date reset consommation"), blank=True, null=True
    )
    nombre_renouvellements = models.PositiveIntegerField(default=0)
    motif_annulation = models.TextField(_("motif annulation"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("abonnement")
        verbose_name_plural = _("abonnements")
        ordering = ["-date_debut"]
        indexes = [
            models.Index(fields=["utilisateur", "statut"]),
            models.Index(fields=["date_fin"]),
        ]

    def __str__(self):
        return (
            f"{self.utilisateur.get_full_name()} — "
            f"{self.plan.nom} ({self.get_statut_display()})"
        )

    @property
    def est_actif(self) -> bool:
        return (
            self.statut == StatutAbonnement.ACTIF
            and self.date_fin > timezone.now()
        )

    @property
    def jours_restants(self) -> int:
        if self.date_fin <= timezone.now():
            return 0
        return (self.date_fin - timezone.now()).days


# ──────────────────────────────────────────────
# Transaction financière
# ──────────────────────────────────────────────

class Transaction(models.Model):
    """Transaction financière (paiement, remboursement, etc.)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    reference = models.CharField(
        _("référence unique"),
        max_length=100,
        unique=True,
    )

    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name=_("utilisateur"),
    )
    abonnement = models.ForeignKey(
        Abonnement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name=_("abonnement lié"),
    )
    plan = models.ForeignKey(
        PlanAbonnement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name=_("plan concerné"),
    )

    TYPE_CHOICES = [
        ("ABONNEMENT", _("Abonnement")),
        ("RENOUVELLEMENT", _("Renouvellement automatique")),
        ("ACHAT_UNITE", _("Achat à l'unité")),
        ("UPGRADE", _("Upgrade de plan")),
        ("REMBOURSEMENT", _("Remboursement")),
        ("CREDIT", _("Crédit / Bonus")),
    ]

    type = models.CharField(
        _("type de transaction"), max_length=20, choices=TYPE_CHOICES
    )
    methode_paiement = models.CharField(
        _("méthode de paiement"),
        max_length=20,
        choices=ProviderPaiement.choices,
    )

    montant = models.DecimalField(
        _("montant (FCFA)"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    frais_transaction = models.DecimalField(
        _("frais transaction (FCFA)"), max_digits=10, decimal_places=0, default=0
    )
    montant_net = models.DecimalField(
        _("montant net reçu (FCFA)"), max_digits=12, decimal_places=0, default=0
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutTransaction.choices,
        default=StatutTransaction.EN_ATTENTE,
    )

    telephone_payeur = models.CharField(
        _("téléphone du payeur"), max_length=20, blank=True
    )
    reference_externe = models.CharField(
        _("référence externe"), max_length=255, blank=True
    )

    description = models.TextField(_("description"), blank=True)
    metadata = models.JSONField(_("métadonnées"), default=dict, blank=True)

    date_initiation = models.DateTimeField(auto_now_add=True)
    date_confirmation = models.DateTimeField(blank=True, null=True)
    date_expiration = models.DateTimeField(blank=True, null=True)

    nombre_tentatives = models.PositiveIntegerField(default=0)
    message_erreur = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
        ordering = ["-date_initiation"]
        indexes = [
            models.Index(fields=["utilisateur", "-date_initiation"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return (
            f"{self.reference} — {self.montant} FCFA "
            f"({self.get_statut_display()})"
        )

    def save(self, *args, **kwargs):
        if self.montant_net is None and self.montant is not None:
            self.montant_net = self.montant - self.frais_transaction
        super().save(*args, **kwargs)

    @property
    def est_reussie(self) -> bool:
        return self.statut == StatutTransaction.CONFIRMEE

    @property
    def montant_formate(self) -> str:
        return f"{int(self.montant):,} FCFA".replace(",", " ")


# ──────────────────────────────────────────────
# Facture
# ──────────────────────────────────────────────

class Facture(models.Model):
    """Facture émise à un utilisateur."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="factures",
        verbose_name=_("utilisateur"),
    )
    abonnement = models.ForeignKey(
        Abonnement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="factures",
        verbose_name=_("abonnement"),
    )

    numero = models.CharField(
        _("numéro de facture"), max_length=50, unique=True
    )

    montant_ht = models.DecimalField(
        _("montant HT (FCFA)"), max_digits=12, decimal_places=0, default=0
    )
    taux_tva = models.DecimalField(
        _("taux TVA (%)"), max_digits=5, decimal_places=2, default=18
    )
    montant_tva = models.DecimalField(
        _("montant TVA (FCFA)"), max_digits=12, decimal_places=0, default=0
    )
    montant_ttc = models.DecimalField(
        _("montant TTC (FCFA)"), max_digits=12, decimal_places=0, default=0
    )
    remise = models.DecimalField(
        _("remise (FCFA)"), max_digits=12, decimal_places=0, default=0
    )

    lignes = models.JSONField(_("lignes de facture"), default=list, blank=True)

    date_emission = models.DateField(_("date d'émission"), auto_now_add=True)
    date_echeance = models.DateField(_("date d'échéance"), blank=True, null=True)
    date_paiement = models.DateField(_("date de paiement"), blank=True, null=True)

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutFacture.choices,
        default=StatutFacture.EMISE,
    )

    fichier_pdf = models.FileField(
        _("fichier PDF"), upload_to="factures/%Y/%m/", blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("facture")
        verbose_name_plural = _("factures")
        ordering = ["-date_emission"]
        indexes = [
            models.Index(fields=["utilisateur", "-date_emission"]),
            models.Index(fields=["statut"]),
        ]

    def __str__(self):
        return f"Facture {self.numero} — {self.montant_ttc} FCFA"

    @property
    def est_payee(self) -> bool:
        return self.statut == StatutFacture.PAYEE

    @property
    def montant_ttc_formate(self) -> str:
        return f"{int(self.montant_ttc):,} FCFA".replace(",", " ")

    def save(self, *args, **kwargs):
        if not self.numero:
            import secrets
            today = timezone.now().strftime("%Y%m%d")
            for _ in range(5):
                numero = f"FAC-{today}-{secrets.token_hex(4).upper()}"
                if not Facture.objects.filter(numero=numero).exists():
                    self.numero = numero
                    break
            else:
                raise ValueError("Impossible de générer un numéro de facture unique.")
        # Auto-calcul TVA et TTC
        recalculate = kwargs.pop("recalculate", True)
        if recalculate:
            self.montant_tva = (self.montant_ht * self.taux_tva) / 100
            self.montant_ttc = self.montant_ht + self.montant_tva - self.remise
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────
# Ristourne conseiller
# ──────────────────────────────────────────────

class StatutRistourne(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente de paiement")
    PAYEE = "PAYEE", _("Payée")
    ANNULEE = "ANNULEE", _("Annulée")


class RistourneConseiller(models.Model):
    """
    Commission gagnée par un conseiller suite à un accompagnement évalué.
    Calculée en fonction du tarif_consultation du CounselorProfile et du taux_ristourne.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conseiller = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="ristournes",
        limit_choices_to={"role": "COUNSELOR"},
        verbose_name=_("conseiller"),
    )
    demande_accompagnement = models.OneToOneField(
        "orientation.DemandeAccompagnement",
        on_delete=models.CASCADE,
        related_name="ristourne",
        verbose_name=_("demande d'accompagnement"),
    )

    montant = models.DecimalField(
        _("montant de la ristourne (FCFA)"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    taux_applique = models.FloatField(
        _("taux appliqué (%)"),
        default=10.0,
    )
    note_etudiant = models.FloatField(
        _("note donnée par l'étudiant"),
        null=True,
        blank=True,
    )

    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutRistourne.choices,
        default=StatutRistourne.EN_ATTENTE,
        db_index=True,
    )
    reference = models.CharField(
        _("référence"),
        max_length=50,
        unique=True,
        blank=True,
    )
    notes_admin = models.TextField(_("notes admin"), blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("ristourne conseiller")
        verbose_name_plural = _("ristournes conseillers")
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["conseiller", "statut"]),
        ]

    def __str__(self):
        return f"Ristourne {self.reference} — {self.conseiller} — {self.montant} FCFA ({self.get_statut_display()})"

    def save(self, *args, **kwargs):
        if not self.reference:
            import secrets
            today = timezone.now().strftime("%Y%m%d")
            for _ in range(5):
                ref = f"RST-{today}-{secrets.token_hex(5).upper()}"
                if not RistourneConseiller.objects.filter(reference=ref).exists():
                    self.reference = ref
                    break
            else:
                raise ValueError("Impossible de générer une référence unique.")
        super().save(*args, **kwargs)
