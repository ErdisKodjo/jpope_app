"""
Tests de l'API accounts.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory, StudentFactory, AdminFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestRegisterAPI:
    def test_register_success(self, api_client):
        url = reverse("accounts-api:register")
        data = {
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
            "role": "STUDENT",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "new@example.com"

    def test_register_password_mismatch(self, api_client):
        url = reverse("accounts-api:register")
        data = {
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass123!",
            "first_name": "New",
            "last_name": "User",
            "role": "STUDENT",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_admin_role_forbidden(self, api_client):
        url = reverse("accounts-api:register")
        data = {
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
            "role": "ADMIN",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    def test_login_success(self, api_client):
        user = StudentFactory(email="test@example.com")
        user.set_password("TestPass123!")
        user.save()

        url = reverse("accounts-api:login")
        data = {"email": "test@example.com", "password": "TestPass123!"}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "user" in response.data

    def test_login_invalid_credentials(self, api_client):
        url = reverse("accounts-api:login")
        data = {"email": "wrong@example.com", "password": "WrongPass123!"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCurrentUserAPI:
    def test_get_current_user(self, api_client):
        user = StudentFactory()
        api_client.force_authenticate(user=user)

        url = reverse("accounts-api:current_user")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_get_current_user_unauthenticated(self, api_client):
        url = reverse("accounts-api:current_user")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
