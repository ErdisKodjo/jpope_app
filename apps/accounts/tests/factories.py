"""
Factories pour les tests.
"""
import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.accounts.models import StudentProfile, CounselorProfile
from apps.accounts.models.enums import UserRole, SerieBac

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")
    role = UserRole.STUDENT
    is_active = True
    is_email_verified = True


class StudentFactory(UserFactory):
    role = UserRole.STUDENT

    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if create:
            StudentProfile.objects.get_or_create(
                user=self,
                defaults={
                    "serie_bac": SerieBac.D,
                    "annee_bac": 2026,
                    "moyenne_generale": 14.5,
                },
            )


class CounselorFactory(UserFactory):
    role = UserRole.COUNSELOR

    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if create:
            CounselorProfile.objects.get_or_create(
                user=self,
                defaults={
                    "annees_experience": 5,
                    "is_available": True,
                },
            )


class AdminFactory(UserFactory):
    role = UserRole.ADMIN
    is_staff = True
    is_superuser = True
