"""
Tests unitaires pour les permissions DRF de core.permissions.
"""

from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser

from core.permissions import IsAdminOrReadOnly, IsCounselor, IsSchoolRep, IsStudent


def _request(user, method="GET"):
    return SimpleNamespace(user=user, method=method)


def _user(role):
    return SimpleNamespace(is_authenticated=True, role=role)


class TestRolePermissions:
    def test_is_student_autorise_etudiant(self):
        assert IsStudent().has_permission(_request(_user("STUDENT")), None)

    def test_is_student_refuse_autre_role(self):
        assert not IsStudent().has_permission(_request(_user("COUNSELOR")), None)

    def test_is_student_refuse_anonyme(self):
        assert not IsStudent().has_permission(_request(AnonymousUser()), None)

    def test_is_counselor_autorise_conseiller(self):
        assert IsCounselor().has_permission(_request(_user("COUNSELOR")), None)

    def test_is_counselor_refuse_etudiant(self):
        assert not IsCounselor().has_permission(_request(_user("STUDENT")), None)

    def test_is_school_rep_autorise(self):
        assert IsSchoolRep().has_permission(_request(_user("SCHOOL_REP")), None)

    def test_is_school_rep_refuse_anonyme(self):
        assert not IsSchoolRep().has_permission(_request(AnonymousUser()), None)


class TestIsAdminOrReadOnly:
    def test_lecture_autorisee_pour_anonyme(self):
        perm = IsAdminOrReadOnly()
        for methode in ("GET", "HEAD", "OPTIONS"):
            assert perm.has_permission(_request(AnonymousUser(), methode), None)

    def test_ecriture_autorisee_pour_admin(self):
        assert IsAdminOrReadOnly().has_permission(_request(_user("ADMIN"), "POST"), None)

    def test_ecriture_refusee_pour_non_admin(self):
        assert not IsAdminOrReadOnly().has_permission(_request(_user("STUDENT"), "POST"), None)

    def test_ecriture_refusee_pour_anonyme(self):
        assert not IsAdminOrReadOnly().has_permission(_request(AnonymousUser(), "DELETE"), None)
