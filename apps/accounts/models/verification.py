"""
Modèle de vérification de document pour les comptes non-étudiants.
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class StatutVerification(models.TextChoices):
    SOUMIS = "SOUMIS", _("Soumis — en attente de traitement")
    APPROUVE = "APPROUVE", _("Approuvé")
    REJETE = "REJETE", _("Rejeté")


class TypeDocument(models.TextChoices):
    CNI = "CNI", _("Carte Nationale d'Identité")
    PASSEPORT = "PASSEPORT", _("Passeport")
    DIPLOME = "DIPLOME", _("Diplôme ou attestation")
    LETTRE_MISSION = "LETTRE_MISSION", _("Lettre de mission / d'employeur")
    AUTRE = "AUTRE", _("Autre document officiel")


class DocumentVerification(models.Model):
    """
    Document justificatif soumis lors de l'inscription par un utilisateur
    non-étudiant (PARENT, COUNSELOR, SCHOOL_REP).
    L'approbation par un admin active le compte (statut_compte → ACTIF).
    """
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="verification_document",
        verbose_name=_("utilisateur"),
    )
    document = models.FileField(
        _("document justificatif"),
        upload_to="verifications/%Y/%m/",
        help_text=_("PDF, JPG ou PNG — 5 Mo max."),
    )
    type_document = models.CharField(
        _("type de document"),
        max_length=20,
        choices=TypeDocument.choices,
        default=TypeDocument.CNI,
    )
    statut = models.CharField(
        _("statut"),
        max_length=20,
        choices=StatutVerification.choices,
        default=StatutVerification.SOUMIS,
        db_index=True,
    )
    note_admin = models.TextField(
        _("note / motif de rejet"),
        blank=True,
        help_text=_("Visible par l'utilisateur en cas de rejet."),
    )
    date_soumission = models.DateTimeField(_("soumis le"), auto_now_add=True)
    date_traitement = models.DateTimeField(_("traité le"), blank=True, null=True)
    traite_par = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verifications_traitees",
        verbose_name=_("traité par"),
    )

    class Meta:
        verbose_name = _("document de vérification")
        verbose_name_plural = _("documents de vérification")
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"Vérification {self.user.get_full_name()} — {self.get_statut_display()}"

    def approuver(self, admin_user):
        """Active le compte et marque le document comme approuvé."""
        from .enums import StatutCompte
        self.statut = StatutVerification.APPROUVE
        self.date_traitement = timezone.now()
        self.traite_par = admin_user
        self.save(update_fields=["statut", "date_traitement", "traite_par"])
        self.user.statut_compte = StatutCompte.ACTIF
        self.user.save(update_fields=["statut_compte"])

    def rejeter(self, admin_user, motif=""):
        """Désactive le compte et consigne le motif de rejet."""
        from .enums import StatutCompte
        self.statut = StatutVerification.REJETE
        self.note_admin = motif
        self.date_traitement = timezone.now()
        self.traite_par = admin_user
        self.save(update_fields=["statut", "note_admin", "date_traitement", "traite_par"])
        self.user.statut_compte = StatutCompte.INACTIF
        self.user.save(update_fields=["statut_compte"])
