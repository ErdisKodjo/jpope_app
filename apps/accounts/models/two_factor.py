"""
Modèle TOTPDevice pour l'authentification à deux facteurs (2FA).

Le 2FA est obligatoire pour les comptes Établissement (SCHOOL_REP) et Conseiller (COUNSELOR),
conformément au cahier des charges (section 3 — Sécurité).
"""
import binascii
import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import pyotp

from apps.accounts.models.enums import UserRole


class TOTPDevice(models.Model):
    """
    Dispositif TOTP (Time-based One-Time Password) associé à un utilisateur.

    Le secret est chiffré au repos via django-cryptography (si disponible),
    sinon stocké en clair (configuration par défaut).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="totp_device",
        verbose_name=_("utilisateur"),
    )
    # Secret base32 — généré par pyotp.random_base32()
    secret = models.CharField(
        _("secret TOTP"),
        max_length=64,
        help_text=_("Secret base32 partagé entre le serveur et l'app d'authentification"),
    )
    # Nom du dispositif (pour identifier l'app authenticator)
    name = models.CharField(
        _("nom du dispositif"),
        max_length=128,
        default="AvenSU-Orienta",
        help_text=_("Nom affiché dans l'application d'authentification (Google Authenticator, etc.)"),
    )
    # État
    is_enabled = models.BooleanField(_("activé"), default=False)
    is_verified = models.BooleanField(
        _("vérifié"),
        default=False,
        help_text=_("Indique si l'utilisateur a confirmé possession du secret en saisissant un code valide"),
    )
    # Codes de secours (backup codes) — hashés en SHA-256
    backup_codes = models.JSONField(
        _("codes de secours"),
        default=list,
        blank=True,
        help_text=_("Liste de codes hashés permettant de récupérer l'accès en cas de perte du téléphone"),
    )
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(
        _("dernière utilisation"),
        blank=True,
        null=True,
    )
    last_challenge_at = models.DateTimeField(
        _("dernier défi envoyé"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("dispositif TOTP")
        verbose_name_plural = _("dispositifs TOTP")

    def __str__(self):
        return f"TOTP — {self.user.email} ({'activé' if self.is_enabled else 'désactivé'})"

    @classmethod
    def generate_secret(cls) -> str:
        """Génère un secret TOTP base32 aléatoire."""
        return pyotp.random_base32()

    @property
    def totp(self) -> pyotp.TOTP:
        """Retourne l'instance pyotp.TOTP configurée."""
        return pyotp.TOTP(self.secret, interval=30, digits=6)

    def verify_code(self, code: str) -> bool:
        """
        Vérifie un code TOTP fourni par l'utilisateur.
        Tolérance de ±1 fenêtre de 30s (comme Google Authenticator).
        """
        if not code or not self.secret:
            return False
        try:
            valid = self.totp.verify(code, valid_window=1)
        except Exception:
            valid = False
        if valid:
            self.last_used_at = timezone.now()
            self.save(update_fields=["last_used_at"])
        return valid

    def provisioning_uri(self) -> str:
        """URI otpauth:// utilisée pour générer le QR code."""
        return self.totp.provisioning_uri(
            name=self.user.email,
            issuer_name=self.name or "AvenSU-Orienta",
        )

    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """
        Génère `count` codes de secours, les stocke hashés et retourne la liste en clair
        (une seule fois, pour affichage à l'utilisateur).
        """
        import hashlib
        plain_codes = []
        hashed = []
        for _ in range(count):
            raw = binascii.hexlify(os.urandom(8)).decode()
            formatted = f"{raw[:5]}-{raw[5:10]}-{raw[10:15]}"
            plain_codes.append(formatted.upper())
            hashed.append(hashlib.sha256(formatted.upper().encode()).hexdigest())
        self.backup_codes = hashed
        self.save(update_fields=["backup_codes"])
        return plain_codes

    def verify_backup_code(self, code: str) -> bool:
        """
        Vérifie un code de secours. Si valide, le consomme (one-shot).
        """
        import hashlib
        if not code or not self.backup_codes:
            return False
        normalized = code.strip().upper()
        hashed = hashlib.sha256(normalized.encode()).hexdigest()
        if hashed in self.backup_codes:
            # Consume the code
            self.backup_codes.remove(hashed)
            self.save(update_fields=["backup_codes"])
            return True
        return False


class TwoFactorChallenge(models.Model):
    """
    Défi 2FA temporaire créé après la première étape de connexion (email + mot de passe).
    L'utilisateur doit saisir un code TOTP valide pour obtenir un token JWT complet.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="two_factor_challenges",
        verbose_name=_("utilisateur"),
    )
    # Token intermédiaire — permet à l'utilisateur de soumettre son code TOTP
    challenge_token = models.CharField(
        _("token de défi"),
        max_length=128,
        unique=True,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(_("expire le"))
    is_consumed = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text=_("Adresse IP à l'origine du défi (audit)"),
    )

    class Meta:
        verbose_name = _("défi 2FA")
        verbose_name_plural = _("défis 2FA")
        ordering = ["-created_at"]

    @classmethod
    def create_for_user(cls, user, ip_address=None) -> "TwoFactorChallenge":
        """Crée un défi 2FA avec une durée de validité de 5 minutes."""
        return cls.objects.create(
            user=user,
            challenge_token=binascii.hexlify(os.urandom(32)).decode(),
            expires_at=timezone.now() + timedelta(minutes=5),
            ip_address=ip_address,
        )

    @property
    def is_valid(self) -> bool:
        return not self.is_consumed and self.expires_at > timezone.now()

    def consume(self):
        self.is_consumed = True
        self.save(update_fields=["is_consumed"])


def is_2fa_required(user) -> bool:
    """
    Détermine si un utilisateur doit activer et utiliser le 2FA.
    Conformément au cahier des charges : obligatoire pour Établissements et Conseillers.
    """
    if not user or not user.is_authenticated:
        return False
    return user.role in (UserRole.SCHOOL_REP, UserRole.COUNSELOR)


def has_active_2fa(user) -> bool:
    """Indique si l'utilisateur a un dispositif 2FA activé et vérifié."""
    if not user or not user.is_authenticated:
        return False
    try:
        device = user.totp_device
        return device.is_enabled and device.is_verified
    except TOTPDevice.DoesNotExist:
        return False
