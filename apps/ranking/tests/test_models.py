"""
Tests des modèles de l'app ranking.
"""
import pytest

from apps.ranking.models import Classement


@pytest.mark.django_db
class TestClassement:
    """Tests du modèle Classement."""

    def _make_classement(self, **kwargs):
        """Helper pour créer un classement de test."""
        from apps.catalog.tests.factories import EtablissementFactory
        defaults = {
            "etablissement": EtablissementFactory(),
            "annee": 2025,
            "rang_national": 1,
            "rang_regional": 1,
            "score_final": 88.5,
            "details_scores": {
                "qualite_enseignement": 90,
                "insertion_professionnelle": 85,
                "recherche": 80,
            },
            "methodology": "Méthode AvenSU 2025",
            "is_published": True,
        }
        defaults.update(kwargs)
        return Classement.objects.create(**defaults)

    def test_creation_classement(self):
        """Un classement peut être créé avec tous les champs."""
        classement = self._make_classement()
        assert classement.pk is not None
        assert classement.annee == 2025
        assert classement.rang_national == 1
        assert classement.score_final == 88.5

    def test_str_representation(self):
        """La représentation string inclut l'établissement et l'année."""
        classement = self._make_classement()
        assert "2025" in str(classement)
        assert "rang national: 1" in str(classement)

    def test_score_formate(self):
        """La propriété score_formate retourne le format attendu."""
        classement = self._make_classement(score_final=88.5)
        assert classement.score_formate == "88.5/100"

    def test_est_top_10(self):
        """est_top_10 est True pour les rangs 1-10."""
        classement_top = self._make_classement(rang_national=5)
        classement_hors_top = self._make_classement(rang_national=15)

        assert classement_top.est_top_10 is True
        assert classement_hors_top.est_top_10 is False

    def test_criteres_principaux_tri(self):
        """Les critères sont triés par score décroissant."""
        classement = self._make_classement(details_scores={
            "recherche": 60,
            "qualite_enseignement": 90,
            "insertion_professionnelle": 75,
        })
        criteres = classement.criteres_principaux
        # Premier critère doit avoir le score le plus élevé
        assert criteres[0][1] >= criteres[1][1] >= criteres[2][1]

    def test_contrainte_unique_etablissement_annee(self):
        """Un établissement ne peut avoir qu'un seul classement par année."""
        from django.db import IntegrityError
        from apps.catalog.tests.factories import EtablissementFactory

        etab = EtablissementFactory()
        self._make_classement(etablissement=etab, annee=2025)

        with pytest.raises(IntegrityError):
            self._make_classement(etablissement=etab, annee=2025)

    def test_rang_national_null_autorise(self):
        """Un classement peut exister sans rang national."""
        classement = self._make_classement(rang_national=None)
        assert classement.rang_national is None
        assert classement.est_top_10 is False
