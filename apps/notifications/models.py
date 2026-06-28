"""
Modèles pour l'app notifications.

Note : La structure complète utilise un sous-package models/
avec enums.py, notification.py, template.py, preference.py, log.py.
Ce fichier fournit un modèle Notification simplifié conforme
aux specs du projet (référencé dans les tâches Celery).
"""
import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TypeNotification(models.TextChoices):
    INFO = "INFO", _("ℹ️ Information")
    SUCCESS = "SUCCESS", _("✅ Succès")
    WARNING = "WARNING", _("⚠️ Avertissement")
    ALERT = "ALERT", _("🚨 Alerte")
    REMINDER = "REMINDER", _("🔔 Rappel")
    # Types étendus (compatibilité avec le beat schedule)
    BIENVENUE = "BIENVENUE", _("👋 Bienvenue")
    VERIFICATION_EMAIL = "VERIF_EMAIL", _("📧 Vérification email")
    RESET_PASSWORD = "RESET_PASSWORD", _("🔐 Réinitialisation mot de passe")
    COMPTE_ACTIVE = "COMPTE_ACTIVE", _("✅ Compte activé")
    TEST_COMPLETE = "TEST_COMPLETE", _("🎯 Test d'orientation terminé")
    NOUVELLE_RECOMMANDATION = "NOUVELLE_REC", _("💡 Nouvelle recommandation")
    VŒU_SOUMIS = "VOEU_SOUMIS", _("📤 Vœu soumis")
    VŒU_ACCEPTE = "VOEU_ACCEPTE", _("✅ Vœu accepté")
    VŒU_REFUSE = "VOEU_REFUSE", _("❌ Vœu refusé")
    DEMARCHE_ECHEANCE = "DEMARCHE_ECHEANCE", _("⏰ Échéance démarche")
    INSCRIPTION_EVT = "INSCR_EVT", _("🎟️ Inscription événement")
    RAPPEL_EVT_J7 = "RAPPEL_J7", _("📅 Rappel J-7")
    RAPPEL_EVT_J1 = "RAPPEL_J1", _("📅 Rappel J-1")
    RAPPEL_EVT_J0 = "RAPPEL_J0", _("📅 Rappel jour J")
    NOUVEAU_MESSAGE = "NOUV_MESSAGE", _("💬 Nouveau message")
    PERSONNALISEE = "PERSONNALISEE", _("📝 Notification personnalisée")
    NEWSLETTER = "NEWSLETTER", _("📰 Newsletter")


class Notification(models.Model):
    """
    Notification individuelle destinée à un utilisateur.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Destinataire
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("utilisateur"),
    )

    # Contenu
    titre = models.CharField(_("titre"), max_length=255)
    message = models.TextField(_("message"))

    # Type
    type_notification = models.CharField(
        _("type"),
        max_length=30,
        choices=TypeNotification.choices,
        default=TypeNotification.INFO,
    )

    # Lecture
    is_read = models.BooleanField(_("lu"), default=False)
    read_at = models.DateTimeField(_("lu le"), blank=True, null=True)

    # Action
    action_url = models.URLField(
        _("URL d'action"),
        blank=True,
        help_text=_("Lien vers lequel rediriger l'utilisateur"),
    )

    # Timestamps
    created_at = models.DateTimeField(_("créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("modifié le"), auto_now=True)

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["type_notification", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_type_notification_display()}] → {self.user}"

    def marquer_comme_lue(self):
        """Marque la notification comme lue."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at", "updated_at"])

    @property
    def est_lue(self) -> bool:
        return self.is_read
