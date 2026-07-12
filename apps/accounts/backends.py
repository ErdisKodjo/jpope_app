"""
Backend d'authentification personnalisé.
Permet la connexion par email ou téléphone.

🔒 Sécurité (cahier des charges §3) :
- L'email doit être vérifié avant de pouvoir se connecter
- Lockout via django-axes (5 tentatives / 1h)
"""
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailOrPhoneBackend(ModelBackend):
    """
    Backend permettant la connexion par email OU par téléphone.
    Exige que l'email soit vérifié (is_email_verified=True) sauf pour les superusers.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authentifie un utilisateur par email ou téléphone.
        Le paramètre 'username' peut contenir un email ou un téléphone.
        """
        if username is None or password is None:
            return None

        # Essayer de trouver par email
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # Essayer par téléphone
            try:
                # Normalisation du téléphone (enlever espaces, tirets)
                phone_clean = username.replace(" ", "").replace("-", "").replace(".", "")
                user = User.objects.get(phone=phone_clean)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                User().set_password(password)  # Timing attack prevention
                return None

        # Vérifier le mot de passe
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def user_can_authenticate(self, user):
        """
        Vérifie que l'utilisateur peut se connecter :
        - Compte actif
        - Statut du compte OK (ACTIF ou EN_ATTENTE_VERIFICATION pour comptes pro en attente)
        - Email vérifié (sauf superusers)
        """
        if not user:
            return False
        is_active = getattr(user, "is_active", True)
        from .models.enums import StatutCompte
        statut_ok = user.statut_compte in [StatutCompte.ACTIF, StatutCompte.EN_ATTENTE_VERIFICATION]

        # Superusers bypass email verification (accès admin via 2FA django-otp)
        if user.is_superuser:
            return is_active and statut_ok

        # Pour les autres : email vérifié obligatoire
        email_verified = getattr(user, "is_email_verified", False)
        if not email_verified:
            logger.warning(
                f"Login bloqué — email non vérifié : {user.email}"
            )
            return False

        return is_active and statut_ok
