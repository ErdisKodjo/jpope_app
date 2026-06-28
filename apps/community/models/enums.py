"""
Énumérations pour l'app community.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TypeForum(models.TextChoices):
    """Type de forum."""
    GENERAL = "GENERAL", _("Forum général")
    DOMAINE = "DOMAINE", _("Forum par domaine")
    ETABLISSEMENT = "ETABLISSEMENT", _("Forum par établissement")
    ENTRAIDE = "ENTRAIDE", _("Forum d'entraide")
    TEMOIGNAGE = "TEMOIGNAGE", _("Forum témoignages")
    OFFICIEL = "OFFICIEL", _("Forum officiel (annonces)")


class StatutThread(models.TextChoices):
    """Statut d'un thread de discussion."""
    OUVERT = "OUVERT", _("Ouvert")
    RESOLU = "RESOLU", _("Résolu")
    VERROUILLE = "VERROUILLE", _("Verrouillé")
    SIGNALE = "SIGNALE", _("Signalé")
    SUPPRIME = "SUPPRIME", _("Supprimé")
    EPINGLE = "EPINGLE", _("Épinglé")


class TypeMessageForum(models.TextChoices):
    """Type de message dans un forum."""
    MESSAGE = "MESSAGE", _("Message standard")
    QUESTION = "QUESTION", _("Question")
    REPONSE = "REPONSE", _("Réponse")
    SOLUTION = "SOLUTION", _("Solution marquée")
    ANNOUNCE = "ANNONCE", _("Annonce officielle")


class StatutMentorat(models.TextChoices):
    """Statut d'une relation de mentorat."""
    EN_ATTENTE = "EN_ATTENTE", _("En attente d'acceptation")
    ACCEPTE = "ACCEPTE", _("Accepté — Mentorat actif")
    REFUSE = "REFUSE", _("Refusé")
    TERMINE = "TERMINE", _("Terminé")
    ANNULE = "ANNULE", _("Annulé")
    SUSPENDU = "SUSPENDU", _("Suspendu")


class TypeMentor(models.TextChoices):
    """Type de mentor."""
    CONSEILLER = "CONSEILLER", _("Conseiller d'orientation")
    ANCIEN = "ANCIEN", _("Ancien élève / Alumni")
    PROFESSIONNEL = "PROFESSIONNEL", _("Professionnel")
    ENSEIGNANT = "ENSEIGNANT", _("Enseignant")
    PAIR = "PAIR", _("Pair (étudiant expérimenté)")


class StatutMessagerie(models.TextChoices):
    """Statut d'un message privé."""
    ENVOYE = "ENVOYE", _("Envoyé")
    LU = "LU", _("Lu")
    SUPPRIME_DESTINATAIRE = "SUPPRIME_DEST", _("Supprimé par le destinataire")
    SUPPRIME_EXPEDITEUR = "SUPPRIME_EXP", _("Supprimé par l'expéditeur")


class TypeSignalement(models.TextChoices):
    """Type de signalement pour modération."""
    SPAM = "SPAM", _("Spam")
    HARCELEMENT = "HARCELEMENT", _("Harcèlement")
    CONTENU_INAPPROPRIE = "INAPPROPRIE", _("Contenu inapproprié")
    DESINFORMATION = "DESINFORMATION", _("Désinformation")
    USURPATION = "USURPATION", _("Usurpation d'identité")
    AUTRE = "AUTRE", _("Autre")


class StatutSignalement(models.TextChoices):
    """Statut d'un signalement."""
    EN_ATTENTE = "EN_ATTENTE", _("En attente de traitement")
    TRAITE = "TRAITE", _("Traité")
    REJETE = "REJETE", _("Rejeté (non fondé)")
    ACTION_PRISE = "ACTION_PRISE", _("Action prise")


class NiveauBlocage(models.TextChoices):
    """Niveau de blocage entre utilisateurs."""
    MASQUER_MESSAGES = "MASQUER", _("Masquer les messages")
    BLOQUER_CONTACT = "BLOQUER", _("Bloquer tout contact")
    SIGNALER_AUTO = "SIGNALER", _("Signaler automatiquement")
