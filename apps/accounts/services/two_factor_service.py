"""
Service 2FA : setup, vérification, gestion des codes de secours, génération de QR codes.
"""
import io
import base64
import qrcode
import qrcode.image.svg

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions

from apps.accounts.models.two_factor import (
    TOTPDevice,
    TwoFactorChallenge,
    is_2fa_required,
    has_active_2fa,
)


class TwoFactorService:
    """
    Centralise toute la logique métier du 2FA :
    - setup (génération du secret + QR code)
    - verify (confirmation du secret par l'utilisateur)
    - login challenge (défi après étape 1 du login)
    - backup codes (génération + consommation)
    - disable
    """

    @staticmethod
    def initiate_setup(user) -> dict:
        """
        Crée (ou réinitialise) un dispositif TOTP pour l'utilisateur.
        Retourne le secret en clair + l'URI otpauth + le QR code en base64.
        L'utilisateur doit ensuite appeler confirm_setup(code) pour activer.
        """
        if not is_2fa_required(user) and not user.is_superuser:
            raise exceptions.PermissionDenied(
                _("Le 2FA n'est obligatoire que pour les conseillers et établissements.")
            )

        device, _created = TOTPDevice.objects.get_or_create(
            user=user,
            defaults={"secret": TOTPDevice.generate_secret()},
        )
        if not device.secret:
            device.secret = TOTPDevice.generate_secret()
        # Si déjà activé, on refuse (sécurité — doit passer par disable d'abord)
        if device.is_enabled:
            raise exceptions.ValidationError(
                _("Le 2FA est déjà activé. Désactivez-le d'abord pour le reconfigurer.")
            )
        # Régénère le secret à chaque setup pour sécurité
        device.secret = TOTPDevice.generate_secret()
        device.is_verified = False
        device.save()

        return {
            "secret": device.secret,
            "uri": device.provisioning_uri(),
            "qr_svg_base64": TwoFactorService._generate_qr_svg(device.provisioning_uri()),
        }

    @staticmethod
    def confirm_setup(user, code: str) -> dict:
        """
        Confirme le setup en vérifiant un code TOTP fourni par l'utilisateur.
        Active le dispositif, génère les codes de secours.
        """
        try:
            device = user.totp_device
        except TOTPDevice.DoesNotExist:
            raise exceptions.ValidationError(_("Aucun setup 2FA en cours."))

        if device.is_enabled:
            raise exceptions.ValidationError(_("Le 2FA est déjà activé."))

        if not device.verify_code(code):
            raise exceptions.ValidationError(_("Code TOTP invalide. Réessayez."))

        device.is_enabled = True
        device.is_verified = True
        device.save(update_fields=["is_enabled", "is_verified"])

        backup_codes = device.generate_backup_codes(count=10)

        return {
            "is_enabled": True,
            "backup_codes": backup_codes,
            "message": _("2FA activé avec succès. Conservez vos codes de secours en lieu sûr."),
        }

    @staticmethod
    def disable(user, code: str = None, backup_code: str = None) -> bool:
        """Désactive le 2FA après vérification d'un code valide."""
        try:
            device = user.totp_device
        except TOTPDevice.DoesNotExist:
            raise exceptions.ValidationError(_("Aucun 2FA à désactiver."))

        if not device.is_enabled:
            return True

        valid = False
        if code and device.verify_code(code):
            valid = True
        elif backup_code and device.verify_backup_code(backup_code):
            valid = True

        if not valid:
            raise exceptions.ValidationError(_("Code TOTP ou code de secours invalide."))

        device.is_enabled = False
        device.is_verified = False
        device.backup_codes = []
        device.save(update_fields=["is_enabled", "is_verified", "backup_codes"])
        return True

    @staticmethod
    def create_challenge(user, ip_address=None) -> TwoFactorChallenge:
        """
        Crée un défi 2FA après validation de l'étape 1 (email + password).
        L'utilisateur doit soumettre un code TOTP + ce challenge_token pour obtenir
        son token JWT final.
        """
        if not has_active_2fa(user):
            raise exceptions.ValidationError(
                _("Le 2FA n'est pas activé pour ce compte. Activez-le avant de vous connecter.")
            )
        # Invalide les défis antérieurs non consommés
        TwoFactorChallenge.objects.filter(user=user, is_consumed=False).update(is_consumed=True)
        return TwoFactorChallenge.create_for_user(user, ip_address=ip_address)

    @staticmethod
    def verify_challenge(challenge_token: str, code: str, ip_address=None):
        """
        Vérifie le code TOTP contre le défi en cours. Si valide :
        - consomme le défi
        - retourne l'utilisateur pour génération du JWT final
        """
        try:
            challenge = TwoFactorChallenge.objects.select_related("user", "user__totp_device").get(
                challenge_token=challenge_token
            )
        except TwoFactorChallenge.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Défi 2FA invalide."))

        if not challenge.is_valid:
            raise exceptions.AuthenticationFailed(_("Défi 2FA expiré ou déjà utilisé."))

        user = challenge.user
        try:
            device = user.totp_device
        except TOTPDevice.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Dispositif 2FA introuvable."))

        if not device.is_enabled or not device.is_verified:
            raise exceptions.AuthenticationFailed(_("2FA non activé."))

        # Accepte soit un code TOTP, soit un code de secours
        if not (device.verify_code(code) or device.verify_backup_code(code)):
            raise exceptions.AuthenticationFailed(_("Code 2FA invalide."))

        challenge.consume()
        return user

    @staticmethod
    def regenerate_backup_codes(user, code: str) -> list[str]:
        """
        Régénère les codes de secours après vérification d'un code TOTP.
        Les anciens codes sont invalidés.
        """
        try:
            device = user.totp_device
        except TOTPDevice.DoesNotExist:
            raise exceptions.ValidationError(_("2FA non activé."))

        if not device.is_enabled:
            raise exceptions.ValidationError(_("2FA non activé."))

        if not device.verify_code(code):
            raise exceptions.ValidationError(_("Code TOTP invalide."))

        return device.generate_backup_codes(count=10)

    @staticmethod
    def _generate_qr_svg(uri: str) -> str:
        """Génère un QR code SVG en base64 pour l'URI otpauth."""
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(uri, image_factory=factory, box_size=10, border=2)
        buffer = io.BytesIO()
        img.save(buffer)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
