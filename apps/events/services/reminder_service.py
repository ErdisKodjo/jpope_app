"""
Service de rappels pour les événements.
"""
import logging
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


class ReminderService:
    """Service pour l'envoi de rappels automatiques aux inscrits."""

    @classmethod
    def envoyer_rappels_j7(cls) -> int:
        """Envoie les rappels 7 jours avant l'événement."""
        return cls._envoyer_rappels(jours=7, champ_rappel="envoi_rappel_j7")

    @classmethod
    def envoyer_rappels_j1(cls) -> int:
        """Envoie les rappels 1 jour avant l'événement."""
        return cls._envoyer_rappels(jours=1, champ_rappel="envoi_rappel_j1")

    @classmethod
    def envoyer_rappels_j0(cls) -> int:
        """Envoie les rappels le jour de l'événement."""
        return cls._envoyer_rappels(jours=0, champ_rappel="envoi_rappel_j0")

    @classmethod
    def _envoyer_rappels(cls, jours: int, champ_rappel: str) -> int:
        """
        Envoie des rappels pour les événements dans `jours` jours.
        """
        from apps.events.models import Evenement, InscriptionEvenement, StatutInscription

        now = timezone.now()

        if jours == 0:
            # Aujourd'hui
            debut = now.replace(hour=0, minute=0, second=0, microsecond=0)
            fin = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            target = now + timezone.timedelta(days=jours)
            debut = target.replace(hour=0, minute=0, second=0, microsecond=0)
            fin = target.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filtre dynamique
        filtre = {
            "date_debut__gte": debut,
            "date_debut__lte": fin,
            "statut": "PUBLIE",
            champ_rappel: True,
        }

        evenements = Evenement.objects.filter(**filtre)

        nb_envoyes = 0
        for evenement in evenements:
            inscriptions = InscriptionEvenement.objects.filter(
                evenement=evenement,
                statut__in=[StatutInscription.INSCRIT, StatutInscription.CONFIRME],
            ).select_related("utilisateur")

            for inscription in inscriptions:
                try:
                    if jours == 0:
                        sujet = f"Rappel : {evenement.titre} a lieu aujourd'hui !"
                        msg_delai = "aujourd'hui"
                    elif jours == 1:
                        sujet = f"Rappel J-1 : {evenement.titre} demain !"
                        msg_delai = "demain"
                    else:
                        sujet = f"Rappel J-{jours} : {evenement.titre} dans {jours} jours"
                        msg_delai = f"dans {jours} jours"

                    message = (
                        f"Bonjour {inscription.utilisateur.first_name},\n\n"
                        f"Rappel : vous êtes inscrit(e) à l'événement "
                        f"'{evenement.titre}' qui a lieu {msg_delai}.\n\n"
                        f"Date : {evenement.date_debut.strftime('%d/%m/%Y à %H:%M')}\n"
                        f"Lieu : {evenement.lieu_nom or evenement.adresse or 'En ligne'}\n\n"
                        f"À bientôt !\nL'équipe AvenSU-Orienta"
                    )

                    send_mail(
                        subject=sujet,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[inscription.utilisateur.email],
                        fail_silently=True,
                    )
                    nb_envoyes += 1

                except Exception as e:
                    logger.error(
                        f"Erreur envoi rappel {champ_rappel} pour "
                        f"{inscription.utilisateur.email}: {e}"
                    )

        logger.info(f"Rappels {champ_rappel} : {nb_envoyes} emails envoyés")
        return nb_envoyes
