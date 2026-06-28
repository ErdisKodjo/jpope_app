"""
Service de modération de la communauté.
"""
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class ModerationService:
    """Service pour la modération du contenu communautaire."""

    @classmethod
    def traiter_signalement(cls, signalement, moderateur, decision: str, action: str = ""):
        """Traite un signalement."""
        from apps.community.models import Signalement, StatutSignalement

        signalement.statut = StatutSignalement.TRAITE
        signalement.traite_par = moderateur
        signalement.date_traitement = timezone.now()
        signalement.decision = decision
        signalement.action_prise = action
        signalement.save(update_fields=[
            "statut", "traite_par", "date_traitement",
            "decision", "action_prise", "updated_at",
        ])

        logger.info(
            f"Signalement traité par {moderateur.email}: "
            f"type={signalement.type}, action={action}"
        )
        return signalement

    @classmethod
    def supprimer_message(cls, message, moderateur):
        """Supprime un message de forum."""
        from apps.community.models import MessageForum

        MessageForum.objects.filter(pk=message.pk).update(
            is_supprime=True,
            est_valide=False,
        )

        logger.info(
            f"Message {message.id} supprimé par {moderateur.email}"
        )

    @classmethod
    def verrouiller_thread(cls, thread, moderateur):
        """Verrouille un thread."""
        from apps.community.models import Thread, StatutThread

        Thread.objects.filter(pk=thread.pk).update(
            statut=StatutThread.VERROUILLE,
            is_ferme=True,
        )

        logger.info(
            f"Thread '{thread.titre}' verrouillé par {moderateur.email}"
        )
