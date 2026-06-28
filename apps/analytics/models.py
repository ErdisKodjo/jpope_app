"""
Modèles pour l'app analytics.

Inclut : PageView, SearchQuery, FormationView, ActionLog, DailyStats,
         KPIDefinition, KPISnapshot, Report, ReportTemplate.
"""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


# ──────────────────────────────────────────────
# Tracking
# ──────────────────────────────────────────────

class PageView(models.Model):
    """Vue de page — tracking anonyme ou authentifié."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="page_views",
        verbose_name=_("utilisateur"),
    )

    path = models.CharField(_("chemin"), max_length=500, db_index=True)
    referrer = models.URLField(_("referrer"), blank=True)
    ip_address = models.GenericIPAddressField(
        _("adresse IP"),
        blank=True,
        null=True,
    )
    user_agent = models.CharField(_("user agent"), max_length=500, blank=True)
    session_key = models.CharField(
        _("clé de session"),
        max_length=100,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("vue de page")
        verbose_name_plural = _("vues de page")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["path", "-created_at"]),
            models.Index(fields=["utilisateur", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.path} — {self.created_at}"


class SearchQuery(models.Model):
    """Requête de recherche effectuée sur la plateforme."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_queries",
        verbose_name=_("utilisateur"),
    )

    query = models.CharField(_("requête"), max_length=500, db_index=True)
    result_count = models.PositiveIntegerField(_("nombre de résultats"), default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("requête de recherche")
        verbose_name_plural = _("requêtes de recherche")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["query", "-created_at"]),
            models.Index(fields=["utilisateur", "-created_at"]),
        ]

    def __str__(self):
        return f'"{self.query}" ({self.result_count} résultats)'


class FormationView(models.Model):
    """Vue d'une formation — tracking de consultation."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="formation_views",
        verbose_name=_("utilisateur"),
    )
    formation = models.ForeignKey(
        "catalog.Formation",
        on_delete=models.CASCADE,
        related_name="views",
        verbose_name=_("formation"),
    )

    duration_seconds = models.PositiveIntegerField(
        _("durée de consultation (secondes)"),
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("vue de formation")
        verbose_name_plural = _("vues de formations")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["formation", "-created_at"]),
            models.Index(fields=["utilisateur", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.formation} — {self.utilisateur or 'Anonyme'}"


class ActionLog(models.Model):
    """Log d'action utilisateur — tracking granulaire des interactions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    TYPE_CHOICES = [
        ("PAGE_VIEW", _("Vue de page")),
        ("SEARCH", _("Recherche")),
        ("FORMATION_VIEW", _("Formation consultée")),
        ("FAVORI_ADDED", _("Favori ajouté")),
        ("VOEU_CREATED", _("Vœu créé")),
        ("TEST_STARTED", _("Test démarré")),
        ("TEST_COMPLETED", _("Test terminé")),
        ("PAYMENT_INITIATED", _("Paiement initié")),
        ("PAYMENT_COMPLETED", _("Paiement réussi")),
        ("EVENT_REGISTERED", _("Inscription événement")),
    ]

    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_logs",
        verbose_name=_("utilisateur"),
    )
    type_action = models.CharField(
        _("type d'action"),
        max_length=30,
        choices=TYPE_CHOICES,
        db_index=True,
    )
    entite_type = models.CharField(_("type d'entité"), max_length=50, blank=True)
    entite_id = models.UUIDField(_("ID de l'entité"), blank=True, null=True)
    metadata = models.JSONField(_("métadonnées"), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("log d'action")
        verbose_name_plural = _("logs d'actions")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["type_action", "-created_at"]),
            models.Index(fields=["utilisateur", "-created_at"]),
        ]

    def __str__(self):
        user = self.utilisateur or "Anonyme"
        return f"[{self.type_action}] {user} — {self.created_at}"


# ──────────────────────────────────────────────
# Agrégations quotidiennes
# ──────────────────────────────────────────────

class DailyStats(models.Model):
    """Statistiques agrégées par jour."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    date = models.DateField(_("date"), unique=True, db_index=True)

    nouveaux_utilisateurs = models.PositiveIntegerField(default=0)
    utilisateurs_actifs = models.PositiveIntegerField(default=0)
    pages_vues = models.PositiveIntegerField(default=0)
    sessions_uniques = models.PositiveIntegerField(default=0)

    tests_demarres = models.PositiveIntegerField(default=0)
    tests_completes = models.PositiveIntegerField(default=0)
    recommandations_generees = models.PositiveIntegerField(default=0)

    formations_consultees = models.PositiveIntegerField(default=0)
    voeux_crees = models.PositiveIntegerField(default=0)

    paiements_reussis = models.PositiveIntegerField(default=0)
    revenus_fcfa = models.DecimalField(
        _("revenus (FCFA)"),
        max_digits=15,
        decimal_places=0,
        default=0,
    )

    top_formations = models.JSONField(default=list, blank=True)
    top_recherches = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("statistique quotidienne")
        verbose_name_plural = _("statistiques quotidiennes")
        ordering = ["-date"]

    def __str__(self):
        return f"Stats {self.date}"

    @property
    def taux_completion_tests(self) -> float:
        if self.tests_demarres == 0:
            return 0
        return round((self.tests_completes / self.tests_demarres) * 100, 1)


# ──────────────────────────────────────────────
# KPIs
# ──────────────────────────────────────────────

class KPIDefinition(models.Model):
    """Définition d'un KPI (indicateur clé de performance)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    CATEGORIE_CHOICES = [
        ("ACQUISITION", _("Acquisition")),
        ("ENGAGEMENT", _("Engagement")),
        ("ORIENTATION", _("Orientation")),
        ("CONVERSION", _("Conversion")),
        ("RETENTION", _("Rétention")),
        ("IMPACT", _("Impact social")),
        ("TECHNIQUE", _("Technique")),
    ]

    code = models.CharField(_("code unique"), max_length=100, unique=True)
    nom = models.CharField(_("nom"), max_length=200)
    description = models.TextField(_("description"))
    formule = models.TextField(_("formule de calcul"), blank=True)
    categorie = models.CharField(
        _("catégorie"), max_length=20, choices=CATEGORIE_CHOICES
    )
    periode = models.CharField(
        _("période"), max_length=20, default="MENSUELLE"
    )
    unite = models.CharField(_("unité"), max_length=50, default="nombre")
    icone = models.CharField(_("icône"), max_length=10, default="📊")
    couleur = models.CharField(_("couleur (hex)"), max_length=7, default="#3B82F6")
    cible = models.FloatField(_("valeur cible"), blank=True, null=True)
    seuil_alerte_bas = models.FloatField(_("seuil alerte bas"), blank=True, null=True)
    seuil_alerte_haut = models.FloatField(_("seuil alerte haut"), blank=True, null=True)
    is_active = models.BooleanField(_("actif"), default=True)
    roles_access = models.JSONField(_("rôles ayant accès"), default=list, blank=True)
    ordre = models.PositiveIntegerField(_("ordre"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("définition KPI")
        verbose_name_plural = _("définitions KPI")
        ordering = ["categorie", "ordre"]

    def __str__(self):
        return f"{self.icone} {self.nom}"


class KPISnapshot(models.Model):
    """Snapshot d'un KPI à une date donnée."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    kpi = models.ForeignKey(
        KPIDefinition,
        on_delete=models.CASCADE,
        related_name="snapshots",
        verbose_name=_("KPI"),
    )
    date = models.DateField(_("date"), db_index=True)
    periode = models.CharField(_("période"), max_length=20, default="MENSUELLE")
    valeur = models.FloatField(_("valeur"))
    valeur_precedente = models.FloatField(_("valeur précédente"), blank=True, null=True)
    variation = models.FloatField(_("variation (%)"), blank=True, null=True)
    details = models.JSONField(_("détails"), default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("snapshot KPI")
        verbose_name_plural = _("snapshots KPI")
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["kpi", "date", "periode"],
                name="unique_kpi_snapshot",
            )
        ]
        indexes = [
            models.Index(fields=["kpi", "-date"]),
        ]

    def __str__(self):
        return f"{self.kpi.nom} — {self.date} : {self.valeur}"

    @property
    def atteint_cible(self):
        if self.kpi.cible is None:
            return None
        return self.valeur >= self.kpi.cible

    @property
    def statut_alerte(self) -> str:
        if self.kpi.seuil_alerte_bas and self.valeur < self.kpi.seuil_alerte_bas:
            return "bas"
        if self.kpi.seuil_alerte_haut and self.valeur > self.kpi.seuil_alerte_haut:
            return "haut"
        return "normal"


# ──────────────────────────────────────────────
# Rapports
# ──────────────────────────────────────────────

class ReportTemplate(models.Model):
    """Template de rapport réutilisable."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(_("code"), max_length=100, unique=True)
    nom = models.CharField(_("nom"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    sections = models.JSONField(_("sections du rapport"), default=list)
    filtres_defaut = models.JSONField(_("filtres par défaut"), default=dict, blank=True)
    formats_disponibles = models.JSONField(_("formats d'export"), default=list)
    roles_access = models.JSONField(_("rôles ayant accès"), default=list, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("template de rapport")
        verbose_name_plural = _("templates de rapport")

    def __str__(self):
        return self.nom


class Report(models.Model):
    """Rapport généré (instance d'un template)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    FORMAT_CHOICES = [
        ("CSV", _("CSV")),
        ("EXCEL", _("Excel")),
        ("PDF", _("PDF")),
        ("JSON", _("JSON")),
    ]

    STATUT_CHOICES = [
        ("EN_COURS", _("En cours de génération")),
        ("TERMINE", _("Terminé")),
        ("ECHEC", _("Échec")),
    ]

    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.PROTECT,
        related_name="reports",
        verbose_name=_("template"),
    )
    genere_par = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports_genres",
        verbose_name=_("généré par"),
    )

    titre = models.CharField(_("titre"), max_length=255)
    filtres_appliques = models.JSONField(_("filtres appliqués"), default=dict, blank=True)
    date_debut = models.DateField(_("date de début"))
    date_fin = models.DateField(_("date de fin"))
    donnees = models.JSONField(_("données du rapport"), default=dict, blank=True)

    format_export = models.CharField(
        _("format d'export"), max_length=10, choices=FORMAT_CHOICES
    )
    fichier = models.FileField(
        _("fichier"), upload_to="reports/%Y/%m/", blank=True, null=True
    )

    statut = models.CharField(
        _("statut"), max_length=20, choices=STATUT_CHOICES, default="EN_COURS"
    )
    message_erreur = models.TextField(blank=True)

    nombre_telechargements = models.PositiveIntegerField(default=0)
    dernier_telechargement = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("rapport")
        verbose_name_plural = _("rapports")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.titre} ({self.get_format_export_display()})"
