"""
Backend d'authentification personnalisé.
Permet la connexion par email ou téléphone.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    """
    Backend permettant la connexion par email OU par téléphone.
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
        """Vérifie que l'utilisateur peut se connecter."""
        is_active = getattr(user, "is_active", True)
        from .models.enums import StatutCompte
        statut_ok = user.statut_compte in [StatutCompte.ACTIF, StatutCompte.EN_ATTENTE_VERIFICATION]
        return is_active and statut_ok
