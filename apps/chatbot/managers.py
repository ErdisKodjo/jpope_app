"""
Managers personnalisés pour les modèles chatbot.
"""
from django.db import models
from django.utils import timezone


class ConversationQuerySet(models.QuerySet):
    def actives(self):
        return self.filter(statut="ACTIVE")

    def archivees(self):
        return self.filter(statut="ARCHIVEE")

    def pour_utilisateur(self, utilisateur):
        return self.filter(utilisateur=utilisateur)

    def avec_messages(self):
        return self.prefetch_related("messages")

    def inactives_depuis(self, jours: int):
        seuil = timezone.now() - timezone.timedelta(days=jours)
        return self.filter(updated_at__lt=seuil)

    def notees(self):
        return self.filter(note_satisfaction__isnull=False)


class ConversationManager(models.Manager):
    def get_queryset(self):
        return ConversationQuerySet(self.model, using=self._db)

    def actives(self):
        return self.get_queryset().actives()

    def archivees(self):
        return self.get_queryset().archivees()

    def pour_utilisateur(self, utilisateur):
        return self.get_queryset().pour_utilisateur(utilisateur)


class MessageQuerySet(models.QuerySet):
    def utilisateur(self):
        return self.filter(role="USER")

    def assistant(self):
        return self.filter(role="ASSISTANT")

    def avec_feedback_positif(self):
        return self.filter(feedbackpositif=True)

    def avec_feedback_negatif(self):
        return self.filter(feedbackpositif=False)

    def par_intent(self, intent: str):
        return self.filter(intent_detecte=intent)

    def pour_conversation(self, conversation_id):
        return self.filter(conversation_id=conversation_id)


class MessageManager(models.Manager):
    def get_queryset(self):
        return MessageQuerySet(self.model, using=self._db)

    def pour_conversation(self, conversation_id):
        return self.get_queryset().pour_conversation(conversation_id)

    def assistant(self):
        return self.get_queryset().assistant()
