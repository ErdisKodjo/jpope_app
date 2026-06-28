"""
Managers personnalisés pour le modèle User.
"""
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager personnalisé pour User avec email comme identifiant."""

    def create_user(self, email, password=None, **extra_fields):
        """Crée et retourne un utilisateur standard."""
        if not email:
            raise ValueError(_("L'adresse e-mail est obligatoire"))

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_student(self, email, password, **extra_fields):
        """Crée un utilisateur avec le rôle étudiant."""
        extra_fields["role"] = "STUDENT"
        return self.create_user(email, password, **extra_fields)

    def create_counselor(self, email, password, **extra_fields):
        """Crée un utilisateur avec le rôle conseiller."""
        extra_fields["role"] = "COUNSELOR"
        return self.create_user(email, password, **extra_fields)

    def create_school_rep(self, email, password, **extra_fields):
        """Crée un utilisateur avec le rôle représentant d'établissement."""
        extra_fields["role"] = "SCHOOL_REP"
        return self.create_user(email, password, **extra_fields)

    def create_parent(self, email, password, **extra_fields):
        """Crée un utilisateur avec le rôle parent."""
        extra_fields["role"] = "PARENT"
        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Crée et retourne un superutilisateur."""
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Un superutilisateur doit avoir is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Un superutilisateur doit avoir is_superuser=True."))

        return self.create_user(email, password, **extra_fields)

    def get_students(self):
        """Retourne tous les étudiants actifs."""
        return self.filter(role="STUDENT", is_active=True)

    def get_counselors(self):
        """Retourne tous les conseillers actifs."""
        return self.filter(role="COUNSELOR", is_active=True)
