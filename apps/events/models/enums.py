"""
Énumérations pour l'app events.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TypeEvenement(models.TextChoices):
    """Type d'événement d'orientation."""
    JPO = "JPO", _("Journée portes ouvertes")
    SALON = "SALON", _("Salon / Forum des formations")
    CONFERENCE = "CONFERENCE", _("Conférence / Table ronde")
    WEBINAIRE = "WEBINAIRE", _("Webinaire / Live en ligne")
    ATELIER = "ATELIER", _("Atelier pratique")
    SEANCE_INFO = "SEANCE_INFO", _("Séance d'information")
    CONCOURS = "CONCOURS", _("Concours d'entrée")
    PRESELECTION = "PRESELECTION", _("Épreuve de présélection")
    ORIENTATION = "ORIENTATION", _("Session d'orientation")
    RENCONTRE = "RENCONTRE", _("Rencontre avec des professionnels")
    VISITE = "VISITE", _("Visite d'entreprise / campus")
    AUTRE = "AUTRE", _("Autre")


class FormatEvenement(models.TextChoices):
    """Format de déroulement de l'événement."""
    PRESENTIEL = "PRESENTIEL", _("Présentiel")
    EN_LIGNE = "EN_LIGNE", _("100% en ligne")
    HYBRIDE = "HYBRIDE", _("Hybride (présentiel + en ligne)")


class StatutEvenement(models.TextChoices):
    """Statut de publication d'un événement."""
    BROUILLON = "BROUILLON", _("Brouillon")
    PUBLIE = "PUBLIE", _("Publié")
    ANNULE = "ANNULE", _("Annulé")
    REPORTE = "REPORTÉ", _("Reporté")
    TERMINE = "TERMINE", _("Terminé (passé)")


class StatutInscription(models.TextChoices):
    """Statut d'une inscription à un événement."""
    INSCRIT = "INSCRIT", _("Inscrit")
    CONFIRME = "CONFIRME", _("Confirmé (email vérifié)")
    LISTE_ATTENTE = "LISTE_ATTENTE", _("Liste d'attente")
    ANNULE = "ANNULE", _("Inscription annulée")
    PRESENT = "PRESENT", _("Présent (a participé)")
    ABSENT = "ABSENT", _("Inscrit mais absent")


class CibleEvenement(models.TextChoices):
    """Public cible de l'événement."""
    TOUS = "TOUS", _("Tous les étudiants")
    TERMINALES = "TERMINALES", _("Élèves de Terminale")
    LICENCE = "LICENCE", _("Étudiants en Licence")
    MASTER = "MASTER", _("Étudiants en Master")
    PARENTS = "PARENTS", _("Parents / Tuteurs")
    CONSEILLERS = "CONSEILLERS", _("Conseillers d'orientation")
    PROFESSIONNELS = "PROFESSIONNELS", _("Professionnels")


class PrioriteEvenement(models.TextChoices):
    """Priorité / importance de l'événement."""
    BASSE = "BASSE", _("Basse")
    NORMALE = "NORMALE", _("Normale")
    HAUTE = "HAUTE", _("Haute — À ne pas manquer")
    CRITIQUE = "CRITIQUE", _("Critique — Incontournable")
