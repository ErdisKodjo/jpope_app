"""
Énumérations pour l'app catalog.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TypeEtablissement(models.TextChoices):
    """Type d'établissement d'enseignement supérieur."""
    PUBLIC = "PUBLIC", _("Public")
    PRIVE_LAIC = "PRIVE_LAIC", _("Privé laïc")
    PRIVE_CONFESSIONNEL = "PRIVE_CONFESSIONNEL", _("Privé confessionnel")
    INTERNATIONAL = "INTERNATIONAL", _("International")
    GRANDE_ECOLE = "GRANDE_ECOLE", _("Grande école")


class StatutEtablissement(models.TextChoices):
    """Statut officiel de l'établissement."""
    AGREÉ = "AGREÉ", _("Agéé par l'État")
    RECONNU = "RECONNU", _("Reconnu par l'État")
    AUTORISE = "AUTORISE", _("Autorisé à fonctionner")
    ACCREDITE = "ACCREDITE", _("Accrédité CAMES")
    NON_ACCREDITE = "NON_ACCREDITE", _("Non accrédité")
    EN_EVALUATION = "EN_EVALUATION", _("En cours d'évaluation")


class NiveauFormation(models.TextChoices):
    """Niveau de la formation (système LMD + technique)."""
    CERTIFICAT = "CERTIFICAT", _("Certificat")
    BTS = "BTS", _("BTS/BT")
    DUT = "DUT", _("DUT/Licence Pro")
    LICENCE = "LICENCE", _("Licence (BAC+3)")
    MASTER = "MASTER", _("Master (BAC+5)")
    DOCTORAT = "DOCTORAT", _("Doctorat (BAC+8)")
    DIPLOME_INGENIEUR = "INGENIEUR", _("Diplôme d'ingénieur")
    DIPLOME_ECOLE = "ECOLE", _("Diplôme d'école")


class NiveauEtudeRequis(models.TextChoices):
    """Niveau d'étude requis pour un métier."""
    BAC = "BAC", _("BAC")
    BAC_PLUS_2 = "BAC+2", _("BAC+2")
    BAC_PLUS_3 = "BAC+3", _("BAC+3")
    BAC_PLUS_5 = "BAC+5", _("BAC+5")
    BAC_PLUS_8 = "BAC+8", _("BAC+8")


class ImportanceStrategique(models.TextChoices):
    """Importance stratégique d'une formation pour le pays."""
    CRITIQUE = "CRITIQUE", _("Critique — Secteur prioritaire national")
    ELEVEE = "ELEVEE", _("Élevée — Forte demande marché")
    MOYENNE = "MOYENNE", _("Moyenne — Demande stable")
    FAIBLE = "FAIBLE", _("Faible — Demande limitée")


class DemandeMarche(models.TextChoices):
    """Niveau de demande sur le marché du travail."""
    TRES_FORTE = "TRES_FORTE", _("Très forte")
    FORTE = "FORTE", _("Forte")
    MOYENNE = "MOYENNE", _("Moyenne")
    FAIBLE = "FAIBLE", _("Faible")
    EN_DECLIN = "EN_DECLIN", _("En déclin")


class ModaliteFormation(models.TextChoices):
    """Modalité d'enseignement."""
    PRESENTIEL = "PRESENTIEL", _("Présentiel")
    DISTANCIEL = "DISTANCIEL", _("100% à distance")
    HYBRIDE = "HYBRIDE", _("Hybride")
    ALTERNANCE = "ALTERNANCE", _("Alternance")


class TypeClassement(models.TextChoices):
    """Type de classement."""
    NATIONAL = "NATIONAL", _("Classement national")
    REGIONAL = "REGIONAL", _("Classement régional")
    PAR_DOMAINE = "PAR_DOMAINE", _("Classement par domaine")
    PAR_VILLE = "PAR_VILLE", _("Classement par ville")
