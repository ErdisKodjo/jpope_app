"""
Tests unitaires pour les méthodes pures de ScoringService.

Ces tests ciblent la logique de calcul (code Holland, interprétation,
forces/axes, normalisation) sans accès base de données.
"""

from apps.orientation.services.scoring_service import ScoringService


class TestDeterminerCodeHolland:
    def test_code_riasec_classique(self):
        scores = {"R": 90, "I": 80, "A": 70, "S": 20}
        code, dominant, secondaire = ScoringService._determiner_code_holland(scores)
        assert code == "RIA"
        assert dominant == "R"
        assert secondaire == "I"

    def test_code_multi_domaine_avec_tirets(self):
        scores = {"N": 90, "ENV": 80, "I": 70}
        code, dominant, secondaire = ScoringService._determiner_code_holland(scores)
        assert code == "N-ENV-I"
        assert dominant == "N"
        assert secondaire == "ENV"

    def test_scores_vides(self):
        assert ScoringService._determiner_code_holland({}) == ("", "", "")

    def test_une_seule_dimension(self):
        code, dominant, secondaire = ScoringService._determiner_code_holland({"R": 50})
        assert code == "R"
        assert dominant == "R"
        assert secondaire == ""


class TestGenererInterpretation:
    def test_code_vide_message_indisponible(self):
        assert ScoringService._generer_interpretation({}, "", None) == "Résultat non disponible."

    def test_interpretation_contient_le_code(self):
        scores = {"R": 90, "I": 80, "A": 70}
        texte = ScoringService._generer_interpretation(scores, "RIA", None)
        assert "RIA" in texte
        assert "Réaliste" in texte

    def test_interpretation_code_multi_domaine(self):
        scores = {"N": 90, "ENV": 80}
        texte = ScoringService._generer_interpretation(scores, "N-ENV", None)
        assert "Numérique" in texte
        assert "Environnement" in texte


class TestIdentifierForces:
    def test_forces_au_dessus_de_70(self):
        forces = ScoringService._identifier_forces({"R": 75, "I": 40, "A": 90})
        assert any("R" in f or "pratique" in f for f in forces)
        assert len(forces) == 2  # R et A

    def test_aucune_force(self):
        assert ScoringService._identifier_forces({"R": 50, "I": 30}) == []

    def test_seuil_exact_70_inclus(self):
        forces = ScoringService._identifier_forces({"S": 70})
        assert len(forces) == 1


class TestIdentifierAxes:
    def test_axes_en_dessous_de_40(self):
        axes = ScoringService._identifier_axes({"R": 30, "I": 80, "A": 10})
        assert len(axes) == 2  # R et A

    def test_aucun_axe(self):
        assert ScoringService._identifier_axes({"R": 50, "I": 90}) == []

    def test_seuil_exact_40_exclu(self):
        assert ScoringService._identifier_axes({"S": 40}) == []


class TestNormaliserScores:
    def test_scores_bruts_vides(self):
        assert ScoringService._normaliser_scores({}, [], None) == {}
