"""
Tâches Celery pour le chatbot IA.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@shared_task(name="chatbot.archiver_conversations_inactives")
def archiver_conversations_inactives(jours_inactivite: int = 30):
    """
    Archive les conversations sans activité depuis N jours.
    """
    from apps.chatbot.models import Conversation, StatutConversation

    seuil = timezone.now() - timezone.timedelta(days=jours_inactivite)

    qs = Conversation.objects.filter(
        statut=StatutConversation.ACTIVE,
        updated_at__lt=seuil,
    )
    count = qs.count()
    qs.update(statut=StatutConversation.ARCHIVEE)

    logger.info(f"[Chatbot] {count} conversations archivées (inactives depuis {jours_inactivite}j).")
    return count


@shared_task(name="chatbot.archiver_conversations_anciennes")
def archiver_conversations_anciennes():
    """Alias pour archiver_conversations_inactives (60 jours)."""
    return archiver_conversations_inactives(jours_inactivite=60)


@shared_task(name="chatbot.aggreger_stats_chatbot")
def aggreger_stats_chatbot():
    """
    Agrège les statistiques du chatbot (pour le dashboard admin).
    """
    from apps.chatbot.models import Conversation, Message

    hier = timezone.now().date() - timezone.timedelta(days=1)

    stats = {
        "conversations_total": Conversation.objects.count(),
        "conversations_hier": Conversation.objects.filter(
            created_at__date=hier
        ).count(),
        "messages_total": Message.objects.count(),
        "messages_hier": Message.objects.filter(
            created_at__date=hier
        ).count(),
    }

    # Calculer la note moyenne de satisfaction
    from django.db.models import Avg
    note_moy = Conversation.objects.filter(
        note_satisfaction__isnull=False
    ).aggregate(moy=Avg("note_satisfaction"))["moy"]
    stats["note_satisfaction_moyenne"] = round(note_moy, 2) if note_moy else None

    # Calculer la latence moyenne
    latence_moy = Message.objects.filter(
        latence_ms__gt=0
    ).aggregate(moy=Avg("latence_ms"))["moy"]
    stats["latence_ms_moyenne"] = int(latence_moy) if latence_moy else None

    logger.info(f"[Chatbot] Stats agrégées : {stats}")
    return stats


@shared_task(name="chatbot.indexer_nouveaux_documents")
def indexer_nouveaux_documents():
    """
    Indexe les nouveaux documents dans la base de connaissances RAG.
    (Stub — à implémenter avec un moteur vectoriel comme Chroma ou Qdrant.)
    """
    logger.info("[Chatbot] Indexation des nouveaux documents (stub).")
    return {"status": "ok", "documents_indexed": 0}


@shared_task(name="chatbot.synchroniser_catalogue_vers_rag")
def synchroniser_catalogue_vers_rag():
    """
    Synchronise le catalogue (formations, métiers, établissements)
    vers la base vectorielle RAG du chatbot.
    (Stub — à implémenter avec Chroma/Qdrant/Weaviate.)
    """
    logger.info("[Chatbot] Synchronisation catalogue vers RAG (stub).")

    # Exemple de synchronisation :
    # formations = Formation.objects.filter(is_active=True).select_related("etablissement")
    # for formation in formations:
    #     doc = {
    #         "id": str(formation.id),
    #         "type": "formation",
    #         "titre": formation.intitule,
    #         "contenu": formation.description,
    #         "metadata": {"domaine": formation.domaine.nom, "ville": formation.ville},
    #     }
    #     rag_client.upsert(doc)

    return {"status": "ok", "synced": 0}
