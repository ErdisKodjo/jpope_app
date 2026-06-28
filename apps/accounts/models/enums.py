"""
Énumérations pour l'app accounts.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """Rôles des utilisateurs."""
    STUDENT = "STUDENT", _("Étudiant")
    PARENT = "PARENT", _("Parent/Tuteur")
    COUNSELOR = "COUNSELOR", _("Conseiller d'orientation")
    SCHOOL_REP = "SCHOOL_REP", _("Représentant d'établissement")
    ADMIN = "ADMIN", _("Administrateur")


class SerieBac(models.TextChoices):
    """Séries du baccalauréat togolais."""
    A = "A", _("Série A (Lettres)")
    C = "C", _("Série C (Maths)")
    D = "D", _("Série D (SVT)")
    E = "E", _("Série E (Technique)")
    G2 = "G2", _("Série G2 (Éco-Gestion)")
    TI = "TI", _("Série TI (Technique Industriel)")
    TGC = "TGC", _("Série TGC (Technique Comptable)")
    AUTRE = "AUTRE", _("Autre")


class Genre(models.TextChoices):
    """Genre."""
    M = "M", _("Masculin")
    F = "F", _("Féminin")
    A = "A", _("Autre/Non spécifié")


class StatutCompte(models.TextChoices):
    """Statut du compte utilisateur."""
    ACTIF = "ACTIF", _("Actif")
    INACTIF = "INACTIF", _("Inactif")
    SUSPENDU = "SUSPENDU", _("Suspendu")
    EN_ATTENTE_VERIFICATION = "EN_ATTENTE", _("En attente de vérification")
