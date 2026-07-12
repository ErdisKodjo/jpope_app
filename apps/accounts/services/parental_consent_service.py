"""
Service de consentement parental — gestion du rattachement parent/tuteur.

Flow :
1. Étudiant mineur demande le rattachement → génère un token + envoie l'email
2. Parent reçoit l'email, clique sur le lien
3. Parent valide (et crée son compte si nécessaire)
4. Lien ParentProfile ↔ StudentProfile établi avec consentement RGPD tracé
"""
import logging
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions

from apps.accounts.models import (
    ConsentementParental, StatutConsentementParental,
    User, UserRole, ParentProfile,
)

logger = logging.getLogger(__name__)


class ParentalConsentService:
    """Centralise la logique du consentement parental."""

    @staticmethod
    def determiner_si_mineur(etudiant: User) -> bool:
        """Vérifie si l'étudiant est mineur (< 18 ans à la date actuelle)."""
        if not etudiant.date_naissance:
            return False
        age = (timezone.now().date() - etudiant.date_naissance).days / 365.25
        return age < 18

    @staticmethod
    def demander_consentement(
        etudiant: User,
        email_parent: str,
        nom_parent: str = "",
        relation: str = "PERE",
    ) -> ConsentementParental:
        """
        Crée une demande de consentement parental.
        Si l'étudiant n'est pas mineur, lève une exception.
        """
        if not ParentalConsentService.determiner_si_mineur(etudiant):
            raise exceptions.ValidationError(
                _("Le consentement parental n'est requis que pour les utilisateurs mineurs.")
            )

        # Invalide les demandes précédentes en attente
        ConsentementParental.objects.filter(
            etudiant=etudiant,
            statut=StatutConsentementParental.EN_ATTENTE,
        ).update(statut=StatutConsentementParental.EXPIRE)

        demande = ConsentementParental.objects.create(
            etudiant=etudiant,
            email_parent=email_parent.lower().strip(),
            nom_parent=nom_parent,
            relation=relation,
        )

        # Envoie l'email au parent (asynchrone si Celery disponible)
        try:
            from apps.accounts.tasks import send_parental_consent_email
            send_parental_consent_email.delay(str(demande.id))
        except Exception:
            # Fallback synchrone
            ParentalConsentService._envoyer_email_sync(demande)

        logger.info(
            f"Demande consentement parental créée : {etudiant.email} → {email_parent}"
        )
        return demande

    @staticmethod
    def valider_consentement(
        token: str,
        parent_email: str,
        parent_first_name: str,
        parent_last_name: str,
        parent_password: str,
        ip_address=None,
        user_agent: str = "",
    ) -> ConsentementParental:
        """
        Valide une demande de consentement parental.
        Si le parent n'a pas de compte → le crée avec le rôle PARENT.
        Si le parent a déjà un compte → vérifie l'email correspond.
        """
        try:
            demande = ConsentementParental.objects.get(token=token)
        except ConsentementParental.DoesNotExist:
            raise exceptions.NotFound(_("Token de validation invalide."))

        if demande.statut == StatutConsentementParental.VALIDE:
            raise exceptions.ValidationError(_("Ce consentement a déjà été validé."))
        if demande.is_expired:
            demande.statut = StatutConsentementParental.EXPIRE
            demande.save(update_fields=["statut"])
            raise exceptions.ValidationError(_("Ce lien a expiré. Demandez à votre enfant de renouveler la demande."))
        if demande.email_parent.lower() != parent_email.lower():
            raise exceptions.ValidationError(
                _("L'email du parent ne correspond pas à celui saisi par l'étudiant.")
            )

        # Récupère ou crée le parent
        parent, created = User.objects.get_or_create(
            email=parent_email.lower(),
            defaults={
                "first_name": parent_first_name,
                "last_name": parent_last_name,
                "role": UserRole.PARENT,
                "is_email_verified": True,
            },
        )
        if created:
            parent.set_password(parent_password)
            parent.save()

        # Valide le consentement
        demande.valider(
            parent_user=parent,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info(f"Consentement parental validé : {parent.email} → {demande.etudiant.email}")
        return demande

    @staticmethod
    def refuser_consentement(token: str) -> ConsentementParental:
        """Le parent refuse explicitement le consentement."""
        try:
            demande = ConsentementParental.objects.get(token=token)
        except ConsentementParental.DoesNotExist:
            raise exceptions.NotFound(_("Token invalide."))
        demande.refuser()
        return demande

    @staticmethod
    def lister_enfants_suivis(parent: User):
        """Liste les enfants suivis par un parent (avec leurs consentements)."""
        return ConsentementParental.objects.filter(
            parent=parent,
            statut=StatutConsentementParental.VALIDE,
        ).select_related("etudiant")

    @staticmethod
    def _envoyer_email_sync(demande: ConsentementParental):
        """Envoie l'email de consentement de manière synchrone (fallback)."""
        from django.core.mail import send_mail
        from django.conf import settings

        url_validation = f"{settings.FRONTEND_URL}/parent/consent/{demande.token}/"
        subject = _("[AvenSU-Orienta] Consentement parental — Validation requise")
        message = (
            f"Bonjour {demande.nom_parent or 'Madame/Monsieur'},\n\n"
            f"Votre enfant {demande.etudiant.get_full_name()} s'est inscrit sur "
            f"la plateforme AvenSU-Orienta. En tant que mineur(e), son inscription "
            f"nécessite votre consentement parental conformément au RGPD.\n\n"
            f"Pour valider et créer votre compte parent, cliquez sur le lien suivant :\n"
            f"{url_validation}\n\n"
            f"Ce lien expirera dans 14 jours.\n\n"
            f"Si vous refusez, votre enfant ne pourra pas utiliser la plateforme.\n\n"
            f"Cordialement,\n"
            f"L'équipe AvenSU-Orienta"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[demande.email_parent],
            fail_silently=False,
        )
