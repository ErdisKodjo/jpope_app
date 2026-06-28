"""
Énumérations pour l'app orientation.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class TypeTest(models.TextChoices):
    """Type de test d'orientation."""
    INTERETS = "INTERETS", _("Test d'intérêts (RIASEC)")
    PERSONNALITE = "PERSONNALITE", _("Test de personnalité")
    COMPETENCES = "COMPETENCES", _("Test de compétences")
    VALEURS = "VALEURS", _("Test de valeurs professionnelles")
    MIXTE = "MIXTE", _("Test mixte (combiné)")
    DIAGNOSTIC = "DIAGNOSTIC", _("Diagnostic rapide")

class TypeQuestion(models.TextChoices):
    """Type de question."""
    CHOIX_UNIQUE = "CHOIX_UNIQUE", _("Choix unique (radio)")
    CHOIX_MULTIPLE = "CHOIX_MULTIPLE", _("Choix multiple (checkbox)")
    ECHELLE_LIKERT = "ECHELLE_LIKERT", _("Échelle de Likert (1-5)")
    CLASSEMENT = "CLASSEMENT", _("Classement / ordre de préférence")
    OUVERTE = "OUVERTE", _("Question ouverte (texte)")
    SITUATIONNELLE = "SITUATIONNELLE", _("Mise en situation")

class TypeDimension(models.TextChoices):
    """
    Dimensions RIASEC (Holland) adaptées au contexte ouest-africain.
    Chaque question évalue une ou plusieurs dimensions.
    """
    REALISTE = "R", _("Réaliste (R) — Technique, concret")
    INVESTIGATEUR = "I", _("Investigateur (I) — Analyse, recherche")
    ARTISTIQUE = "A", _("Artistique (A) — Créativité, expression")
    SOCIAL = "S", _("Social (S) — Aide, enseignement, soin")
    ENTREPRENEUR = "E", _("Entreprenant (E) — Leadership, commerce")
    CONVENTIONNEL = "C", _("Conventionnel (C) — Organisation, rigueur")
    # Dimensions complémentaires
    NUMERIQUE = "N", _("Numérique — IA, développement, data")
    ENVIRONNEMENT = "ENV", _("Environnement — Écologie, agriculture")

class PlanRecommandation(models.TextChoices):
    """Plan de la recommandation."""
    PRINCIPAL = "PRINCIPAL", _("Plan principal — Forte compatibilité")
    ALTERNATIF = "ALTERNATIF", _("Plan alternatif — Bonne compatibilité")
    EXPLORATOIRE = "EXPLORATOIRE", _("Plan exploratoire — À découvrir")
    PASSERELLE = "PASSERELLE", _("Plan passerelle — Reconversion")

class TypeEntiteRecommandee(models.TextChoices):
    """Type d'entité recommandée."""
    FORMATION = "FORMATION", _("Formation")
    METIER = "METIER", _("Métier")
    ETABLISSEMENT = "ETABLISSEMENT", _("Établissement")

class StatutTest(models.TextChoices):
    """Statut de passation d'un test."""
    EN_COURS = "EN_COURS", _("En cours")
    TERMINE = "TERMINE", _("Terminé")
    EXPIRE = "EXPIRE", _("Expiré (non terminé à temps)")
    ABANDONNE = "ABANDONNE", _("Abandonné par l'utilisateur")

class NiveauConfiance(models.TextChoices):
    """Niveau de confiance de la recommandation."""
    TRES_HAUTE = "TRES_HAUTE", _("Très haute (>85%)")
    HAUTE = "HAUTE", _("Haute (70-85%)")
    MOYENNE = "MOYENNE", _("Moyenne (50-70%)")
    FAIBLE = "FAIBLE", _("Faible (<50%)")
