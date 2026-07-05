"""
Service de gestion du mentorat.
"""
import logging
from django.db import transaction
from django.db.models import F
from django.utils import timezone

logger = logging.getLogger(__name__)


class MentoratService:
    """Service pour la gestion des relations de mentorat."""

    @classmethod
    @transaction.atomic
    def accepter_demande(cls, relation, mentor_utilisateur):
        """Accepte une demande de mentorat."""
        from apps.community.models import RelationMentorat, StatutMentorat, ProfilMentor

        if relation.statut != StatutMentorat.EN_ATTENTE:
            raise ValueError("Cette demande ne peut pas être acceptée.")

        if relation.mentor.utilisateur != mentor_utilisateur:
            raise PermissionError("Vous n'êtes pas le mentor de cette relation.")

        relation.statut = StatutMentorat.ACCEPTE
        relation.date_reponse = timezone.now()
        relation.date_debut = timezone.now()
        relation.save(update_fields=["statut", "date_reponse", "date_debut", "updated_at"])

        # Mettre à jour le compteur du mentor
        ProfilMentor.objects.filter(pk=relation.mentor.pk).update(
            nombre_mentores_actuels=F("nombre_mentores_actuels") + 1,
            nombre_mentores_total=F("nombre_mentores_total") + 1,
        )

        logger.info(
            f"Mentorat accepté: {relation.mentor} → {relation.mentoré}"
        )
        return relation

    @classmethod
    @transaction.atomic
    def refuser_demande(cls, relation, mentor_utilisateur):
        """Refuse une demande de mentorat."""
        from apps.community.models import RelationMentorat, StatutMentorat

        if relation.mentor.utilisateur != mentor_utilisateur:
            raise PermissionError("Vous n'êtes pas le mentor de cette relation.")

        relation.statut = StatutMentorat.REFUSE
        relation.date_reponse = timezone.now()
        relation.save(update_fields=["statut", "date_reponse", "updated_at"])

        logger.info(
            f"Mentorat refusé: {relation.mentor} → {relation.mentoré}"
        )
        return relation

    @classmethod
    @transaction.atomic
    def terminer_relation(cls, relation):
        """Termine une relation de mentorat."""
        from apps.community.models import RelationMentorat, StatutMentorat, ProfilMentor

        relation.statut = StatutMentorat.TERMINE
        relation.date_fin = timezone.now()
        relation.save(update_fields=["statut", "date_fin", "updated_at"])

        # Décrémenter le compteur du mentor
        ProfilMentor.objects.filter(pk=relation.mentor.pk).update(
            nombre_mentores_actuels=F("nombre_mentores_actuels") - 1,
        )

        logger.info(f"Mentorat terminé: {relation.mentor} → {relation.mentoré}")
        return relation
