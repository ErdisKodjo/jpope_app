"""
Modèle ConsentementParental pour le rattachement parent/tuteur des mineurs.

Cahier des charges (section 2.1 — Candidat, Inscription) :
"Pour les utilisateurs mineurs (collégiens/lycéens), une option de rattachement
d'un compte parent/tuteur avec validation par email est requise pour se conformer
à la protection des mineurs."

Flow :
1. Étudiant mineur crée son compte
2. Saisit l'email de son parent/tuteur
3. Système génère un token + envoie un email au parent
4. Parent clique sur le lien → voit le consentement RGPD parental
5. Parent crée son compte (si pas existant) + signe le consentement
6. Lien ParentProfile ↔ StudentProfile créé avec statut VALIDATED
"""
import binascii
import os
import uuid
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.compliance.encryption_fields import EncryptedCharField


class StatutConsentementParental(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente — email envoyé au parent")
    VALIDE = "VALIDE", _("Validé par le parent")
    REFUSE = "REFUSE", _("Refusé par le parent")
    EXPIRE = "EXPIRE", _("Expiré (délai de 14 jours dépassé)")


class ConsentementParental(models.Model):
    """
    Demande de consentement parental pour un utilisateur mineur.
    Associe un étudiant mineur à son parent/tuteur via un token email.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Étudiant mineur
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="demandes_consentement_parental",
        verbose_name=_("étudiant mineur"),
    )

    # Parent (créé après validation si n'existe pas)
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consentements_enfants",
        verbose_name=_("parent/tuteur"),
    )

    # Email du parent saisi par l'étudiant
    email_parent = models.EmailField(
        _("email du parent"),
        help_text=_("Email saisi par l'étudiant mineur lors de l'inscription"),
    )
    nom_parent = EncryptedCharField(
        _("nom du parent"),
        max_length=255,
        blank=True,
        help_text=_("Nom saisi par l'étudiant (prénom + nom) — chiffré au repos"),
    )
    relation = models.CharField(
        _("relation avec l'étudiant"),
        max_length=20,
        choices=[
            ("PERE", _("Père")),
            ("MERE", _("Mère")),
            ("TUTEUR_LEGAL", _("Tuteur légal")),
            ("AUTRE", _("Autre")),
        ],
        default="PERE",
    )

    # Token de validation
    token = models.CharField(
        _("token de validation"),
        max_length=128,
        unique=True,
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(
        _("date d'expiration"),
        help_text=_("Délai de 14 jours pour valider"),
    )
    date_validation = models.DateTimeField(blank=True, null=True)

    # Statut
    statut = models.CharField(
        _("statut"),
        max_length=15,
        choices=StatutConsentementParental.choices,
        default=StatutConsentementParental.EN_ATTENTE,
    )

    # Lien vers le consentement RGPD signé par le parent
    consentement_rgpd = models.ForeignKey(
        "compliance.ConsentementRGPD",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consentements_parentaux",
        verbose_name=_("consentement RGPD signé"),
    )

    # Métadonnées
    ip_validation = models.GenericIPAddressField(blank=True, null=True)
    user_agent_validation = models.CharField(max_length=512, blank=True)

    class Meta:
        verbose_name = _("consentement parental")
        verbose_name_plural = _("consentements parentaux")
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["etudiant", "statut"]),
            models.Index(fields=["email_parent", "statut"]),
        ]

    def __str__(self):
        return f"Consentement parental — {self.etudiant.email} → {self.email_parent} ({self.statut})"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = binascii.hexlify(os.urandom(32)).decode()
        if not self.date_expiration:
            self.date_expiration = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        return self.statut == StatutConsentementParental.EN_ATTENTE and self.date_expiration < timezone.now()

    @property
    def is_validated(self) -> bool:
        return self.statut == StatutConsentementParental.VALIDE

    def valider(self, parent_user, ip_address=None, user_agent=""):
        """Marque le consentement comme validé et crée le lien ParentProfile ↔ StudentProfile."""
        from apps.accounts.models import ParentProfile
        from apps.compliance.models import ConsentementRGPD, TypeConsentement
        from apps.compliance.services import RGPDService

        self.parent = parent_user
        self.statut = StatutConsentementParental.VALIDE
        self.date_validation = timezone.now()
        self.ip_validation = ip_address
        self.user_agent_validation = user_agent[:512]

        # Crée le consentement RGPD parental
        texte = (
            "Je soussigné(e) {nom}, agissant en qualité de parent/tuteur légal de {enfant}, "
            "consens au traitement des données personnelles de mon enfant par la plateforme "
            "AvenSU-Orienta, conformément au RGPD. J'autorise notamment : "
            "la collecte de ses notes scolaires, résultats de tests d'orientation, "
            "messages dans la messagerie encadrée, et l'accès aux outils d'apprentissage IA. "
            "Je peux retirer ce consentement à tout moment."
        ).format(
            nom=parent_user.get_full_name(),
            enfant=self.etudiant.get_full_name(),
        )
        consentement = RGPDService.donner_consentement(
            utilisateur=parent_user,
            type_consentement=TypeConsentement.PARENTAL,
            texte=texte,
            ip_address=ip_address,
            user_agent=user_agent,
            parent=parent_user,
        )
        self.consentement_rgpd = consentement
        self.save()

        # Crée ou récupère le ParentProfile du parent
        parent_profile, _created = ParentProfile.objects.get_or_create(
            user=parent_user,
            defaults={"relation_avec_enfant": self.relation},
        )
        # Ajoute l'étudiant aux enfants suivis
        parent_profile.enfants_suivis.add(self.etudiant)

        return self

    def refuser(self):
        self.statut = StatutConsentementParental.REFUSE
        self.save(update_fields=["statut"])

    def generer_url_validation(self, request=None) -> str:
        """URL de validation à envoyer par email au parent."""
        from django.urls import reverse
        path = reverse("accounts:parental_consent_validate", kwargs={"token": self.token})
        if request:
            return request.build_absolute_uri(path)
        return path
