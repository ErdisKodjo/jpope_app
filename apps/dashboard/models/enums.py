"""
Énumérations pour l'app dashboard.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class TypeFavori(models.TextChoices):
    """Type d'entité mise en favori."""
    FORMATION = "FORMATION", _("Formation")
    METIER = "METIER", _("Métier")
    ETABLISSEMENT = "ETABLISSEMENT", _("Établissement")
    EVENEMENT = "EVENEMENT", _("Événement")

class StatutVoeu(models.TextChoices):
    """Statut d'un vœu d'inscription."""
    BROUILLON = "BROUILLON", _("Brouillon")
    SOUMIS = "SOUMIS", _("Soumis à l'établissement")
    EN_ATTENTE = "EN_ATTENTE", _("En attente de réponse")
    ACCEPTE = "ACCEPTE", _("Accepté")
    REFUSE = "REFUSE", _("Refusé")
    LISTE_ATTENTE = "LISTE_ATTENTE", _("Liste d'attente")
    ABANDONNE = "ABANDONNE", _("Abandonné par l'étudiant")
    INSCRIT = "INSCRIT", _("Inscrit définitivement")

class PrioriteVoeu(models.TextChoices):
    """Niveau de priorité d'un vœu."""
    VITAL = "VITAL", _("Vital — Mon choix n°1")
    IMPORTANT = "IMPORTANT", _("Important — Très souhaité")
    SOUHAITE = "SOUHAITE", _("Souhaité — Intéressant")
    SECURITE = "SECURITE", _("Sécurité — Plan B")
    EXPLORATOIRE = "EXPLORATOIRE", _("Exploratoire — À voir")

class TypeDemarche(models.TextChoices):
    """Type de démarche administrative."""
    INSCRIPTION = "INSCRIPTION", _("Inscription administrative")
    CONCOURS = "CONCOURS", _("Concours d'entrée")
    PRESELECTION = "PRESELECTION", _("Présélection sur dossier")
    BOURSE = "BOURSE", _("Demande de bourse")
    LOGEMENT = "LOGEMENT", _("Demande de logement")
    VISA = "VISA", _("Demande de visa étudiant")
    EQUIVALENCE = "EQUIVALENCE", _("Demande d'équivalence")
    AUTRE = "AUTRE", _("Autre démarche")

class StatutDemarche(models.TextChoices):
    """Statut d'une démarche."""
    A_FAIRE = "A_FAIRE", _("À faire")
    EN_COURS = "EN_COURS", _("En cours")
    ENVOYEE = "ENVOYEE", _("Envoyée / Déposée")
    COMPLETEE = "COMPLETEE", _("Complétée")
    ANNULEE = "ANNULEE", _("Annulée")
    ECHEANCE_PASSEE = "ECHEANCE_PASSEE", _("Échéance passée")

class TypeEvenementAgenda(models.TextChoices):
    """Type d'événement dans l'agenda."""
    JPO = "JPO", _("Journée portes ouvertes")
    CONCOURS = "CONCOURS", _("Concours")
    DATE_LIMITE = "DATE_LIMITE", _("Date limite")
    ENTRETIEN = "ENTRETIEN", _("Entretien / Oral")
    RESULTAT = "RESULTAT", _("Publication résultats")
    INSCRIPTION = "INSCRIPTION", _("Inscription administrative")
    SALON = "SALON", _("Salon / Forum")
    WEBINAIRE = "WEBINAIRE", _("Webinaire")
    PERSONNEL = "PERSONNEL", _("Personnel")

class StatutRappel(models.TextChoices):
    """Statut d'un rappel."""
    ACTIF = "ACTIF", _("Actif")
    ENVOYE = "ENVOYE", _("Envoyé")
    IGNORE = "IGNORE", _("Ignoré")
    ANNULE = "ANNULE", _("Annulé")

class CanalNotification(models.TextChoices):
    """Canal de notification."""
    EMAIL = "EMAIL", _("Email")
    PUSH = "PUSH", _("Push mobile")
    SMS = "SMS", _("SMS")
    IN_APP = "IN_APP", _("In-app")
