"""
Shared helpers for triggering recommendation generation.

Centralises the duplicated pattern of extracting student-profile
preferences and calling ``RecommendationEngine.generer_recommandations``.
Previously duplicated in:
- ``apps.orientation.views.SubmitTestView.post``
- ``apps.accounts.views.NotesEtudiantView._regenerer_recommandations``
- ``apps.orientation.tasks.calculer_resultat_et_recommandations``
"""
import logging

logger = logging.getLogger(__name__)


def generate_recommendations_for_resultat(resultat, user=None):
    """Generate recommendations for a ``ResultatTest``, using the student's profile prefs.

    Parameters
    ----------
    resultat : ResultatTest
        The result to generate recommendations for.
    user : User | None
        The student user. If *None* it is resolved from *resultat*.

    Returns
    -------
    list[Recommandation] | None
        The created recommendations, or *None* on error.
    """
    from apps.orientation.services.recommendation_engine import RecommendationEngine

    if user is None:
        user = resultat.reponse_utilisateur.etudiant

    profile = getattr(user, "student_profile", None)
    budget_max = None
    villes_preferees = None

    if profile:
        budget_max = int(profile.budget_max_annuel) if profile.budget_max_annuel else None
        villes_preferees = profile.villes_preferees or None

    try:
        return RecommendationEngine.generer_recommandations(
            resultat=resultat,
            budget_max=budget_max,
            villes_preferees=villes_preferees,
        )
    except Exception as exc:
        logger.error("Erreur génération recommandations: %s", exc)
        return None
