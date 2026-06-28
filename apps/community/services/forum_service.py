"""
Service de gestion des forums et discussions.
"""
import logging
from django.db import transaction
from django.db.models import F

logger = logging.getLogger(__name__)


class ForumService:
    """Service pour la gestion des forums et threads."""

    @classmethod
    def abonner_utilisateur(cls, utilisateur, forum) -> bool:
        """Abonne un utilisateur à un forum."""
        from apps.community.models import AbonnementForum
        _, created = AbonnementForum.objects.get_or_create(
            utilisateur=utilisateur,
            forum=forum,
        )
        if created:
            from apps.community.models import Forum
            Forum.objects.filter(pk=forum.pk).update(
                nombre_abonnes=F("nombre_abonnes") + 1
            )
        return created

    @classmethod
    def desabonner_utilisateur(cls, utilisateur, forum) -> bool:
        """Désabonne un utilisateur d'un forum."""
        from apps.community.models import AbonnementForum, Forum
        deleted_count, _ = AbonnementForum.objects.filter(
            utilisateur=utilisateur,
            forum=forum,
        ).delete()
        if deleted_count:
            Forum.objects.filter(pk=forum.pk).update(
                nombre_abonnes=F("nombre_abonnes") - 1
            )
        return bool(deleted_count)

    @classmethod
    @transaction.atomic
    def creer_thread(cls, forum, auteur, titre: str, contenu: str, tags: list = None):
        """Crée un nouveau thread dans un forum."""
        from apps.community.models import Thread, Forum

        thread = Thread.objects.create(
            forum=forum,
            auteur=auteur,
            titre=titre,
            contenu=contenu,
            tags=tags or [],
        )

        # Mettre à jour les compteurs du forum
        Forum.objects.filter(pk=forum.pk).update(
            nombre_threads=F("nombre_threads") + 1,
        )

        logger.info(f"Thread créé: '{titre}' dans {forum.nom} par {auteur.email}")
        return thread

    @classmethod
    @transaction.atomic
    def marquer_solution(cls, thread, message, moderateur_ou_auteur) -> bool:
        """Marque un message comme solution d'un thread."""
        from apps.community.models import Thread, MessageForum, StatutThread

        # Vérifier les droits
        if (
            thread.auteur != moderateur_ou_auteur
            and not getattr(moderateur_ou_auteur, 'is_staff', False)
        ):
            raise PermissionError("Seul l'auteur peut marquer une solution.")

        # Désélectionner l'ancienne solution si elle existe
        MessageForum.objects.filter(
            thread=thread, is_solution=True
        ).update(is_solution=False)

        # Marquer la nouvelle solution
        MessageForum.objects.filter(pk=message.pk).update(is_solution=True)

        # Mettre à jour le thread
        Thread.objects.filter(pk=thread.pk).update(
            reponse_solution=message,
            statut=StatutThread.RESOLU,
        )

        logger.info(f"Solution marquée: message {message.id} dans '{thread.titre}'")
        return True
