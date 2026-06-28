"""
Tests des modèles de l'app orientation.
"""
import pytest

from apps.orientation.models import (
    TestOrientation,
    Question,
    Choice,
    ReponseUtilisateur,
    DetailReponse,
    ResultatTest,
    Recommandation,
    TypeTest,
    TypeQuestion,
    StatutTest,
    PlanRecommandation,
    NiveauConfiance,
)


@pytest.mark.django_db
class TestTestOrientation:
    """Tests du modèle TestOrientation."""

    def _make_test(self, **kwargs):
        defaults = {
            "nom": "Test RIASEC",
            "type": TypeTest.INTERETS,
            "duree_estimee_minutes": 15,
            "dimensions_evaluees": ["R", "I", "A", "S", "E", "C"],
            "is_active": True,
            "is_public": True,
        }
        defaults.update(kwargs)
        return TestOrientation.objects.create(**defaults)

    def test_creation_test_orientation(self):
        """Un test d'orientation peut être créé."""
        test = self._make_test()
        assert test.pk is not None
        assert test.slug  # Le slug est auto-généré

    def test_slug_auto_genere(self):
        """Le slug est auto-généré à partir du nom."""
        test = self._make_test(nom="Test Compétences Numériques")
        assert "test" in test.slug
        assert "comp" in test.slug

    def test_str_representation(self):
        """La représentation string inclut le nom et le type."""
        test = self._make_test()
        assert "Test RIASEC" in str(test)

    def test_peut_etre_passe_sans_questions(self):
        """Un test sans questions ne peut pas être passé."""
        test = self._make_test()
        assert test.peut_etre_passe is False


@pytest.mark.django_db
class TestReponseUtilisateur:
    """Tests du modèle ReponseUtilisateur."""

    def _make_session(self, **kwargs):
        from apps.accounts.tests.factories import StudentFactory
        from apps.orientation.tests.factories import TestOrientationFactory
        defaults = {
            "etudiant": StudentFactory(),
            "test": TestOrientationFactory(),
            "statut": StatutTest.EN_COURS,
            "nombre_questions_total": 10,
        }
        defaults.update(kwargs)
        return ReponseUtilisateur.objects.create(**defaults)

    def test_session_created(self):
        """Une session de test peut être créée."""
        session = self._make_session()
        assert session.pk is not None
        assert session.statut == StatutTest.EN_COURS

    def test_est_termine(self):
        """La propriété est_termine retourne True si statut = TERMINE."""
        session_en_cours = self._make_session(statut=StatutTest.EN_COURS)
        session_terminee = self._make_session(statut=StatutTest.TERMINE)

        assert session_en_cours.est_termine is False
        assert session_terminee.est_termine is True

    def test_progression_formatee(self):
        """La propriété progression_formatee retourne un % formaté."""
        session = self._make_session()
        session.progression = 75.0
        assert session.progression_formatee == "75%"


@pytest.mark.django_db
class TestRecommandation:
    """Tests du modèle Recommandation."""

    def _make_recommandation(self, **kwargs):
        from apps.orientation.tests.factories import ResultatTestFactory
        from apps.accounts.tests.factories import StudentFactory
        from apps.catalog.tests.factories import FormationFactory

        etudiant = StudentFactory()
        resultat = ResultatTestFactory()

        defaults = {
            "resultat_test": resultat,
            "etudiant": etudiant,
            "type_entite": "FORMATION",
            "formation": FormationFactory(),
            "taux_compatibilite": 80.0,
            "plan": PlanRecommandation.PRINCIPAL,
        }
        defaults.update(kwargs)
        return Recommandation.objects.create(**defaults)

    def test_niveau_confiance_auto(self):
        """Le niveau de confiance est calculé automatiquement à la sauvegarde."""
        rec_haute = self._make_recommandation(taux_compatibilite=90.0)
        assert rec_haute.niveau_confiance == NiveauConfiance.TRES_HAUTE

        rec_faible = self._make_recommandation(taux_compatibilite=30.0)
        assert rec_faible.niveau_confiance == NiveauConfiance.FAIBLE

    def test_entite_nom(self):
        """La propriété entite_nom retourne le nom de l'entité recommandée."""
        rec = self._make_recommandation()
        assert rec.entite_nom != "N/A"
