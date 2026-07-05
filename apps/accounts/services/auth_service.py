"""
Service d'authentification — logique métier.
"""
import secrets
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AuthService:
    """Service pour les opérations d'authentification."""

    @staticmethod
    @shared_task(queue="notifications")
    def send_verification_email(user_id):
        """Envoie un email de vérification (tâche asynchrone)."""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return

        if user.is_email_verified:
            return

        # Générer un token
        token = secrets.token_urlsafe(32)
        user.email_verification_token = token
        user.email_verification_token_expires = timezone.now() + timedelta(hours=24)
        user.save(update_fields=["email_verification_token", "email_verification_token_expires"])

        # Construire le lien
        frontend_url = getattr(settings, "FRONTEND_URL", "")
        verification_url = f"{frontend_url}/verify-email?token={token}" if frontend_url else ""

        # Envoyer l'email
        subject = _("Vérifiez votre adresse email — AvenSU-Orienta")
        message = render_to_string(
            "accounts/emails/verification.html",
            {
                "user": user,
                "verification_url": verification_url,
                "expiry_hours": 24,
            },
        )

        send_mail(
            subject=subject,
            message="",
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    @staticmethod
    def verify_email_token(token):
        """Vérifie un token de vérification d'email."""
        try:
            user = User.objects.get(email_verification_token=token)
        except User.DoesNotExist:
            return False

        if user.email_verification_token_expires < timezone.now():
            return False

        user.mark_email_verified()
        return True

    @staticmethod
    @shared_task(queue="notifications")
    def send_password_reset_email(email):
        """Envoie un email de réinitialisation de mot de passe."""
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Ne rien faire pour ne pas révéler l'existence du compte
            return

        # Générer un token
        token = secrets.token_urlsafe(32)
        user.email_verification_token = token
        user.email_verification_token_expires = timezone.now() + timedelta(hours=1)
        user.save(update_fields=["email_verification_token", "email_verification_token_expires"])

        frontend_url = getattr(settings, "FRONTEND_URL", "")
        reset_url = f"{frontend_url}/reset-password?token={token}" if frontend_url else ""

        subject = _("Réinitialisation de votre mot de passe — AvenSU-Orienta")
        message = render_to_string(
            "accounts/emails/password_reset.html",
            {
                "user": user,
                "reset_url": reset_url,
                "expiry_hours": 1,
            },
        )

        send_mail(
            subject=subject,
            message="",
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    @staticmethod
    def reset_password_with_token(token, new_password):
        """Réinitialise le mot de passe avec un token."""
        try:
            user = User.objects.get(email_verification_token=token)
        except User.DoesNotExist:
            return False

        if user.email_verification_token_expires < timezone.now():
            return False

        user.set_password(new_password)
        user.email_verification_token = None
        user.email_verification_token_expires = None
        user.save()
        return True
