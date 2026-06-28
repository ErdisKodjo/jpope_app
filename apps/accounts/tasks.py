"""
Tâches Celery pour l'app accounts.
"""
from celery import shared_task


@shared_task(queue="notifications")
def send_verification_email_task(user_id):
    """Tâche Celery : envoie un email de vérification."""
    from apps.accounts.services.auth_service import AuthService
    AuthService.send_verification_email(user_id)


@shared_task(queue="notifications")
def send_password_reset_email_task(email):
    """Tâche Celery : envoie un email de réinitialisation de mot de passe."""
    from apps.accounts.services.auth_service import AuthService
    AuthService.send_password_reset_email(email)


@shared_task(queue="default")
def update_counselor_stats_task(counselor_id):
    """Tâche Celery : met à jour les statistiques d'un conseiller."""
    from apps.accounts.services.profile_service import ProfileService
    ProfileService.update_counselor_stats(counselor_id)


@shared_task(queue="default")
def cleanup_expired_tokens_task():
    """Tâche Celery périodique : nettoie les tokens de vérification expirés."""
    from django.utils import timezone
    from apps.accounts.models import User

    count = User.objects.filter(
        email_verification_token_expires__lt=timezone.now(),
        is_email_verified=False,
    ).update(
        email_verification_token=None,
        email_verification_token_expires=None,
    )
    return f"{count} tokens expirés nettoyés."


@shared_task(queue="default")
def nettoyer_sessions():
    """
    Tâche Celery périodique : nettoie les sessions expirées.
    Référencé dans config/celery.py beat schedule :
      "nettoyer-sessions-expirees": {
          "task": "apps.accounts.tasks.nettoyer_sessions",
          "schedule": crontab(hour=4, minute=0),
      }
    Planifié tous les jours à 4h00.
    """
    from django.utils import timezone

    count = 0

    try:
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.sessions.models import Session

        # Supprimer les sessions expirées
        expired = Session.objects.filter(expire_date__lt=timezone.now())
        count = expired.count()
        expired.delete()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Nettoyage sessions : {e}")

    return f"{count} sessions expirées supprimées."
