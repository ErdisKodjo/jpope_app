"""
Modèle User personnalisé pour AvenSU-Orienta.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .enums import UserRole, Genre, StatutCompte
from ..managers import UserManager


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé.
    Utilise l'email comme identifiant principal au lieu du username.
    """
    # Remplacement du username par email
    username = None
    email = models.EmailField(
        _("adresse e-mail"),
        unique=True,
        db_index=True,
        error_messages={
            "unique": _("Un utilisateur avec cet e-mail existe déjà."),
        },
    )

    # Identifiant public (pour API, pas d'auto-incrémenté exposé)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )

    # Informations personnelles
    first_name = models.CharField(_("prénom"), max_length=150)
    last_name = models.CharField(_("nom"), max_length=150)
    phone = models.CharField(
        _("téléphone"),
        max_length=20,
        blank=True,
        help_text=_("Format international : +228 90 00 00 00"),
    )
    avatar = models.ImageField(
        _("photo de profil"),
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
    )
    genre = models.CharField(
        _("genre"),
        max_length=1,
        choices=Genre.choices,
        default=Genre.A,
    )
    date_naissance = models.DateField(
        _("date de naissance"),
        blank=True,
        null=True,
    )

    # Rôle et statut
    role = models.CharField(
        _("rôle"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        db_index=True,
    )
    statut_compte = models.CharField(
        _("statut du compte"),
        max_length=20,
        choices=StatutCompte.choices,
        default=StatutCompte.ACTIF,
    )

    # Vérifications
    is_email_verified = models.BooleanField(
        _("e-mail vérifié"),
        default=False,
    )
    is_phone_verified = models.BooleanField(
        _("téléphone vérifié"),
        default=False,
    )
    email_verification_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    email_verification_token_expires = models.DateTimeField(
        blank=True,
        null=True,
    )

    # Token de réinitialisation de mot de passe (séparé du token email)
    password_reset_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    password_reset_token_expires = models.DateTimeField(
        blank=True,
        null=True,
    )

    # Métadonnées
    last_login_ip = models.GenericIPAddressField(
        _("dernière IP de connexion"),
        blank=True,
        null=True,
    )
    timezone = models.CharField(
        _("fuseau horaire"),
        max_length=50,
        default="Africa/Lome",
    )
    langue_preferee = models.CharField(
        _("langue préférée"),
        max_length=10,
        default="fr",
    )

    # Profil complété ?
    profile_complete = models.BooleanField(
        _("profil complété"),
        default=False,
    )

    # Timestamps
    created_at = models.DateTimeField(_("créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("mis à jour le"), auto_now=True)
    last_activity_at = models.DateTimeField(
        _("dernière activité"),
        blank=True,
        null=True,
    )

    # Manager personnalisé
    objects = UserManager()

    # Configuration
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def is_student(self):
        return self.role == UserRole.STUDENT

    @property
    def is_counselor(self):
        return self.role == UserRole.COUNSELOR

    @property
    def is_school_rep(self):
        return self.role == UserRole.SCHOOL_REP

    @property
    def is_parent(self):
        return self.role == UserRole.PARENT

    @property
    def is_admin_role(self):
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def profile(self):
        """Retourne le profil associé au rôle de l'utilisateur."""
        from .profiles import StudentProfile, CounselorProfile, SchoolRepProfile, ParentProfile

        profile_map = {
            UserRole.STUDENT: ("student_profile", StudentProfile),
            UserRole.COUNSELOR: ("counselor_profile", CounselorProfile),
            UserRole.SCHOOL_REP: ("school_rep_profile", SchoolRepProfile),
            UserRole.PARENT: ("parent_profile", ParentProfile),
        }

        if self.role in profile_map:
            attr_name, _ = profile_map[self.role]
            return getattr(self, attr_name, None)
        return None

    def update_last_activity(self):
        """Met à jour la date de dernière activité."""
        self.last_activity_at = timezone.now()
        self.save(update_fields=["last_activity_at"])

    def mark_email_verified(self):
        """Marque l'email comme vérifié."""
        self.is_email_verified = True
        self.email_verification_token = None
        self.email_verification_token_expires = None
        self.save(update_fields=[
            "is_email_verified",
            "email_verification_token",
            "email_verification_token_expires",
        ])
