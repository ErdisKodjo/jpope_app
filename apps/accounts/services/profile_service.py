"""
Service de gestion des profils utilisateurs.
"""
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ProfileService:
    """Service pour les opérations sur les profils."""

    @staticmethod
    def update_student_profile(user, data):
        """Met à jour le profil étudiant et vérifie sa complétion."""
        profile = getattr(user, "student_profile", None)
        if not profile:
            return None

        for field, value in data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        profile.save()

        # Mettre à jour le flag profile_complete sur l'utilisateur
        if profile.is_complete and not user.profile_complete:
            user.profile_complete = True
            user.save(update_fields=["profile_complete"])

        return profile

    @staticmethod
    def update_counselor_stats(counselor_id):
        """Met à jour les statistiques d'un conseiller."""
        from apps.accounts.models import CounselorProfile

        try:
            profile = CounselorProfile.objects.get(id=counselor_id)
        except CounselorProfile.DoesNotExist:
            return

        # Compter les élèves suivis via le modèle de mentorat (si disponible)
        # Logique à adapter selon le modèle de relation mentorat
        try:
            from apps.mentoring.models import MentoringSession
            count = MentoringSession.objects.filter(
                counselor=profile.user,
                is_active=True,
            ).values("student").distinct().count()
            profile.nombre_eleves_suivis = count
            profile.save(update_fields=["nombre_eleves_suivis"])
        except ImportError:
            pass

    @staticmethod
    def get_profile_completion_percentage(user):
        """Retourne le pourcentage de complétion du profil."""
        base_fields = [
            user.first_name,
            user.last_name,
            user.phone,
            user.avatar,
            user.genre,
            user.date_naissance,
        ]
        base_filled = sum(1 for f in base_fields if f)
        base_total = len(base_fields)

        profile = user.profile
        if not profile:
            return int((base_filled / base_total) * 100)

        # Champs spécifiques au profil étudiant
        from apps.accounts.models.enums import UserRole
        if user.role == UserRole.STUDENT:
            profile_fields = [
                profile.serie_bac,
                profile.annee_bac,
                profile.centres_interet,
                profile.etablissement_scolaire,
                profile.projet_professionnel,
            ]
            profile_filled = sum(1 for f in profile_fields if f)
            profile_total = len(profile_fields)
            total = base_total + profile_total
            filled = base_filled + profile_filled
        else:
            total = base_total
            filled = base_filled

        return int((filled / total) * 100) if total > 0 else 0

    @staticmethod
    def delete_user_account(user, reason=""):
        """Désactive le compte utilisateur (soft delete)."""
        from apps.accounts.models.enums import StatutCompte

        user.is_active = False
        user.statut_compte = StatutCompte.INACTIF
        user.save(update_fields=["is_active", "statut_compte"])

        # Log la suppression si nécessaire
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Compte désactivé: {user.email} (reason: {reason or 'non spécifiée'})"
        )

        return True
