"""
Signals pour la création automatique des profils.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, StudentProfile, CounselorProfile, SchoolRepProfile, ParentProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement le profil associé lors de la création d'un utilisateur."""
    if created:
        from .models.enums import UserRole

        profile_creators = {
            UserRole.STUDENT: lambda u: StudentProfile.objects.get_or_create(user=u),
            UserRole.COUNSELOR: lambda u: CounselorProfile.objects.get_or_create(user=u),
            UserRole.SCHOOL_REP: lambda u: SchoolRepProfile.objects.get_or_create(user=u),
            UserRole.PARENT: lambda u: ParentProfile.objects.get_or_create(user=u),
        }

        creator = profile_creators.get(instance.role)
        if creator:
            try:
                creator(instance)
            except Exception as e:
                # Log l'erreur mais ne bloque pas la création de l'utilisateur
                import logging
                logging.getLogger(__name__).error(
                    f"Erreur création profil pour {instance.email}: {e}"
                )