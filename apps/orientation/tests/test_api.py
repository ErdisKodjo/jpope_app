"""
Tests de l'API orientation.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.orientation.models import TestOrientation, ReponseUtilisateur, StatutTest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_client(api_client):
    from apps.accounts.tests.factories import StudentFactory
    student = StudentFactory()
    api_client.force_authenticate(user=student)
    return api_client, student


@pytest.mark.django_db
class TestTestOrientationAPI:
    """Tests de l'API des tests d'orientation."""

    def test_liste_tests_publics(self, api_client):
        """La liste des tests publics est accessible sans authentification."""
        from apps.orientation.tests.factories import TestOrientationFactory
        TestOrientationFactory.create_batch(3, is_active=True, is_public=True)
        TestOrientationFactory(is_active=True, is_public=False)  # Non public

        response = api_client.get("/api/v1/orientation/tests/")

        assert response.status_code == status.HTTP_200_OK
        # Seuls les tests publics et actifs sont visibles
        data = response.data
        results = data.get("results", data)
        assert len(results) == 3

    def test_detail_test_par_slug(self, api_client):
        """Le détail d'un test est accessible via son slug."""
        from apps.orientation.tests.factories import TestOrientationFactory
        test = TestOrientationFactory(is_active=True, is_public=True)

        response = api_client.get(f"/api/v1/orientation/tests/{test.slug}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["nom"] == test.nom


@pytest.mark.django_db
class TestSoumettreTest:
    """Tests de soumission d'un test."""

    def test_soumettre_test_non_authentifie(self, api_client):
        """Un utilisateur non authentifié ne peut pas soumettre un test."""
        response = api_client.post("/api/v1/orientation/test/submit/", {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_commencer_test(self, student_client):
        """Un étudiant peut commencer un test."""
        from apps.orientation.tests.factories import TestOrientationFactory, QuestionFactory
        client, student = student_client

        test = TestOrientationFactory(is_active=True)
        QuestionFactory(test=test, is_active=True)  # Au moins une question
        # Mettre à jour le cache du nombre de questions
        test.nombre_questions = 1
        test.save(update_fields=["nombre_questions"])

        response = client.post(
            "/api/v1/orientation/test/start/",
            {"test_id": str(test.id)},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "session_id" in response.data
