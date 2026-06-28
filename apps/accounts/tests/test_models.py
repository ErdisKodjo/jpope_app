"""
Tests des modèles accounts.
"""
import pytest
from django.db import IntegrityError

from apps.accounts.models import User, StudentProfile
from apps.accounts.models.enums import UserRole
from apps.accounts.tests.factories import UserFactory, StudentFactory


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="Test",
            last_name="User",
        )
        assert user.email == "test@example.com"
        assert user.check_password("TestPass123!")
        assert user.role == UserRole.STUDENT
        assert user.is_active

    def test_create_user_without_email_raises(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="TestPass123!")

    def test_email_is_unique(self):
        UserFactory(email="unique@example.com")
        with pytest.raises(IntegrityError):
            UserFactory(email="unique@example.com")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass123!",
            first_name="Admin",
            last_name="User",
        )
        assert admin.is_superuser
        assert admin.is_staff
        assert admin.role == UserRole.ADMIN

    def test_get_full_name(self):
        user = UserFactory(first_name="Kossi", last_name="Mensah")
        assert user.get_full_name() == "Kossi Mensah"

    def test_is_student_property(self):
        student = StudentFactory()
        assert student.is_student
        assert not student.is_counselor

    def test_profile_auto_creation(self):
        """Le profil est créé automatiquement via signal."""
        user = UserFactory(role=UserRole.STUDENT)
        assert hasattr(user, "student_profile")
        assert user.student_profile is not None


@pytest.mark.django_db
class TestStudentProfile:
    def test_is_complete(self):
        profile = StudentFactory().student_profile
        profile.serie_bac = "D"
        profile.annee_bac = 2026
        profile.centres_interet = ["informatique", "maths"]
        profile.save()
        assert profile.is_complete

    def test_is_incomplete(self):
        profile = StudentFactory().student_profile
        profile.serie_bac = ""
        profile.save()
        assert not profile.is_complete
