"""
Tests unitaires pour apps.payments.services.utils.
"""

import pytest

from apps.payments.services.utils import normaliser_telephone


class TestNormaliserTelephone:
    def test_numero_local_8_chiffres(self):
        assert normaliser_telephone("90123456") == "+22890123456"

    def test_numero_avec_zero_initial(self):
        assert normaliser_telephone("090123456") == "+22890123456"

    def test_prefixe_indicatif_228(self):
        assert normaliser_telephone("22890123456") == "+22890123456"

    def test_prefixe_international_plus(self):
        assert normaliser_telephone("+22890123456") == "+22890123456"

    def test_prefixe_00228(self):
        assert normaliser_telephone("0022890123456") == "+22890123456"

    def test_espaces_et_tirets_supprimes(self):
        assert normaliser_telephone(" 90-12.34 56 ") == "+22890123456"

    def test_parentheses_supprimees(self):
        assert normaliser_telephone("(228)90123456") == "+22890123456"

    @pytest.mark.parametrize(
        "entree",
        ["90123456", "090123456", "22890123456", "+22890123456", "0022890123456"],
    )
    def test_toutes_formes_convergent(self, entree):
        assert normaliser_telephone(entree) == "+22890123456"

    def test_format_international_autre_pays_conserve(self):
        assert normaliser_telephone("+33612345678") == "+33612345678"

    def test_resultat_commence_toujours_par_plus(self):
        assert normaliser_telephone("90123456").startswith("+")
