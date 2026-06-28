"""
Énumérations pour l'app chatbot.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleMessage(models.TextChoices):
    """Rôle dans une conversation."""
    SYSTEM = "SYSTEM", _("Système")
    USER = "USER", _("Utilisateur")
    ASSISTANT = "ASSISTANT", _("Assistant")
    TOOL = "TOOL", _("Outil / Handler")


class TypeIntent(models.TextChoices):
    """Types d'intentions reconnues par le chatbot."""
    # Recherche catalogue
    CHERCHER_FORMATION = "CHERCHER_FORMATION", _("Rechercher une formation")
    CHERCHER_METIER = "CHERCHER_METIER", _("Rechercher un métier")
    CHERCHER_ETABLISSEMENT = "CHERCHER_ETABLISSEMENT", _("Rechercher un établissement")
    INFO_DOMAIN = "INFO_DOMAIN", _("Infos sur un domaine")

    # Comparaison & analyse
    COMPARER_ECOLES = "COMPARER_ECOLES", _("Comparer des écoles")
    COMPARER_FORMATIONS = "COMPARER_FORMATIONS", _("Comparer des formations")
    SIMULER_COUT = "SIMULER_COUT", _("Simuler le coût")

    # Orientation
    AIDE_ORIENTATION = "AIDE_ORIENTATION", _("Aide à l'orientation")
    TEST_ORIENTATION = "TEST_ORIENTATION", _("Passer un test")
    RESULTATS_TEST = "RESULTATS_TEST", _("Voir ses résultats")
    RECOMMANDATIONS = "RECOMMANDATIONS", _("Voir ses recommandations")

    # Métiers
    INFO_METIER = "INFO_METIER", _("Infos sur un métier")
    DEBOUCHES = "DEBOUCHES", _("Débouchés d'une formation")
    SALAIRE_METIER = "SALAIRE_METIER", _("Salaire d'un métier")

    # Démarches
    DEMARCHE_INSCRIPTION = "DEMARCHE_INSCRIPTION", _("Démarche d'inscription")
    CONCOURS_INFO = "CONCOURS_INFO", _("Infos concours")
    BOURSE_INFO = "BOURSE_INFO", _("Infos bourses")

    # Événements
    EVENEMENTS_PROCHES = "EVENEMENTS_PROCHES", _("Événements à venir")
    JPO_INFO = "JPO_INFO", _("Infos JPO")

    # Dashboard
    MES_FAVORIS = "MES_FAVORIS", _("Voir mes favoris")
    MES_VOEUX = "MES_VOEUX", _("Voir mes vœux")
    MES_ECHEANCES = "MES_ECHEANCES", _("Voir mes échéances")

    # Général
    SALUTATIONS = "SALUTATIONS", _("Salutations")
    REMERCIEMENTS = "REMERCIEMENTS", _("Remerciements")
    QUESTION_GENERALE = "QUESTION_GENERALE", _("Question générale")
    HORS_SUJET = "HORS_SUJET", _("Hors sujet / non géré")


class SourceReponse(models.TextChoices):
    """Source de la réponse du chatbot."""
    HANDLER_METIER = "HANDLER_METIER", _("Handler métier (données structurées)")
    RAG = "RAG", _("Base de connaissances (RAG)")
    LLM_DIRECT = "LLM_DIRECT", _("LLM général (sans contexte)")
    CATALOGUE = "CATALOGUE", _("Catalogue (formations/métiers)")
    ORIENTATION = "ORIENTATION", _("Résultats d'orientation")
    FALLBACK = "FALLBACK", _("Réponse par défaut")


class StatutConversation(models.TextChoices):
    """Statut d'une conversation."""
    ACTIVE = "ACTIVE", _("Active")
    ARCHIVEE = "ARCHIVEE", _("Archivée")
    SIGNELEE = "SIGNELEE", _("Signalée (modération)")


class CanalDiscussion(models.TextChoices):
    """Canal d'origine de la discussion."""
    WEB = "WEB", _("Site web")
    MOBILE = "MOBILE", _("Application mobile")
    API = "API", _("API externe")


class NiveauConfianceIntent(models.TextChoices):
    """Niveau de confiance de la détection d'intention."""
    TRES_HAUTE = "TRES_HAUTE", _("Très haute (>0.85)")
    HAUTE = "HAUTE", _("Haute (0.7-0.85)")
    MOYENNE = "MOYENNE", _("Moyenne (0.5-0.7)")
    FAIBLE = "FAIBLE", _("Faible (<0.5)")
