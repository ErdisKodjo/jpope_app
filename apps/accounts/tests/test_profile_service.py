"""
Tests unitaires pour apps.accounts.services.profile_service.ProfileService.
"""

import datetime

import pytest

from apps.accounts.models import CounselorProfile
from apps.accounts.models.enums import SerieBac, StatutCompte
from apps.accounts.services.profile_service import ProfileService
from apps.accounts.tests.factories import CounselorFactory, StudentFactory


@pytest.mark.django_db
class TestUpdateStudentProfile:
    def test_met_a_jour_les_champs(self):
        user = StudentFactory()
        profile = ProfileService.update_student_profile(
            user, {"etablissement_scolaire": "Lycée de Tokoin"}
        )
        assert profile is not None
        assert profile.etablissement_scolaire == "Lycée de Tokoin"

    def test_ignore_champs_inconnus(self):
        user = StudentFactory()
        profile = ProfileService.update_student_profile(
            user, {"champ_inexistant": "x", "etablissement_scolaire": "Lycée"}
        )
        assert profile.etablissement_scolaire == "Lycée"
        assert not hasattr(profile, "champ_inexistant")

    def test_marque_profile_complete_si_complet(self):
        user = StudentFactory(profile_complete=False)
        # is_complete exige serie_bac + annee_bac + centres_interet
        ProfileService.update_student_profile(
            user,
            {
                "serie_bac": SerieBac.D,
                "annee_bac": 2026,
                "centres_interet": ["informatique"],
            },
        )
        user.refresh_from_db()
        assert user.profile_complete is True

    def test_retourne_none_sans_profil_etudiant(self):
        counselor = CounselorFactory()
        assert ProfileService.update_student_profile(counselor, {}) is None


@pytest.mark.django_db
class TestGetProfileCompletionPercentage:
    def test_pourcentage_partiel(self):
        user = StudentFactory(
            first_name="Yao",
            last_name="Agbeko",
            phone="",
            genre="",
            date_naissance=None,
        )
        pct = ProfileService.get_profile_completion_percentage(user)
        assert 0 < pct < 100

    def test_pourcentage_augmente_avec_champs_remplis(self):
        user = StudentFactory(phone="", genre="", date_naissance=None)
        avant = ProfileService.get_profile_completion_percentage(user)
        user.phone = "+22890123456"
        user.genre = "M"
        user.date_naissance = datetime.date(2005, 1, 1)
        user.save()
        apres = ProfileService.get_profile_completion_percentage(user)
        assert apres > avant

    def test_retourne_entier(self):
        user = StudentFactory()
        pct = ProfileService.get_profile_completion_percentage(user)
        assert isinstance(pct, int)
        assert 0 <= pct <= 100


@pytest.mark.django_db
class TestDeleteUserAccount:
    def test_soft_delete_desactive_le_compte(self):
        user = StudentFactory(is_active=True)
        result = ProfileService.delete_user_account(user, reason="test")
        user.refresh_from_db()
        assert result is True
        assert user.is_active is False
        assert user.statut_compte == StatutCompte.INACTIF


@pytest.mark.django_db
class TestUpdateCounselorStats:
    def test_id_inexistant_retourne_none(self):
        assert ProfileService.update_counselor_stats(999999) is None

    def test_profil_valide_sans_module_mentoring(self):
        """Le module apps.mentoring n'existe pas : ImportError avalée."""
        counselor = CounselorFactory()
        profile = CounselorProfile.objects.get(user=counselor)
        # Ne doit pas lever d'exception
        ProfileService.update_counselor_stats(profile.id)
