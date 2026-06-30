"""
Tests d'intégration — module accounts (authentification, profil).
"""
import html
import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.models.enums import UserRole, StatutCompte

pytestmark = pytest.mark.django_db


# ─── Connexion ──────────────────────────────────────────

class TestLogin:

    def test_page_login_accessible(self, client):
        resp = client.get(reverse("accounts:login"))
        assert resp.status_code == 200

    def test_login_email_valide(self, client, etudiant):
        resp = client.post(reverse("accounts:login"), {"username": etudiant.email, "password": "TestPass123!"})
        assert resp.status_code == 302
        assert resp.url == reverse("accounts:home")

    def test_login_mauvais_mot_de_passe(self, client, etudiant):
        resp = client.post(reverse("accounts:login"), {"username": etudiant.email, "password": "mauvaismdp"})
        assert resp.status_code == 200
        assert not resp.wsgi_request.user.is_authenticated

    def test_login_is_active_false_bloque(self, client):
        """is_active=False bloque définitivement la connexion (tous les backends)."""
        u = User.objects.create_user(
            email="desactive@test.tg", password="TestPass123!",
            statut_compte=StatutCompte.INACTIF, is_active=False,
        )
        resp = client.post(reverse("accounts:login"), {"username": u.email, "password": "TestPass123!"})
        assert resp.status_code == 200
        assert not resp.wsgi_request.user.is_authenticated

    def test_login_statut_suspendu_bloque_si_inactif(self, client):
        """Compte suspendu avec is_active=False ne peut pas se connecter."""
        u = User.objects.create_user(
            email="suspendu@test.tg", password="TestPass123!",
            statut_compte=StatutCompte.SUSPENDU, is_active=False,
        )
        resp = client.post(reverse("accounts:login"), {"username": u.email, "password": "TestPass123!"})
        assert resp.status_code == 200
        assert not resp.wsgi_request.user.is_authenticated

    def test_login_statut_en_attente_autorise(self, client):
        u = User.objects.create_user(
            email="attente@test.tg", password="TestPass123!",
            statut_compte=StatutCompte.EN_ATTENTE_VERIFICATION,
            is_active=True,
        )
        resp = client.post(reverse("accounts:login"), {"username": u.email, "password": "TestPass123!"})
        assert resp.status_code == 302

    def test_deconnexion(self, client_etudiant):
        resp = client_etudiant.get(reverse("accounts:logout"))
        assert resp.status_code == 302
        assert not resp.wsgi_request.user.is_authenticated

    def test_redirect_si_deja_connecte(self, client_etudiant):
        resp = client_etudiant.get(reverse("accounts:login"))
        assert resp.status_code == 302


# ─── Inscription ────────────────────────────────────────

class TestRegister:

    def test_page_inscription_accessible(self, client):
        resp = client.get(reverse("accounts:register"))
        assert resp.status_code == 200

    def test_inscription_etudiant_valide(self, client):
        data = {
            "email": "nouveau@test.tg",
            "first_name": "Kofi",
            "last_name": "Mensah",
            "role": "STUDENT",
            "password1": "MonMotDePasse123!",
            "password2": "MonMotDePasse123!",
            "cgu": "on",
        }
        resp = client.post(reverse("accounts:register"), data)
        assert resp.status_code == 302
        assert User.objects.filter(email="nouveau@test.tg").exists()

    def test_inscription_email_existant_echec(self, client, etudiant):
        data = {
            "email": etudiant.email,
            "first_name": "Test", "last_name": "Test",
            "role": "STUDENT",
            "password1": "MonMotDePasse123!",
            "password2": "MonMotDePasse123!",
            "cgu": "on",
        }
        resp = client.post(reverse("accounts:register"), data)
        assert resp.status_code == 200
        assert User.objects.filter(email=etudiant.email).count() == 1

    def test_inscription_mot_de_passe_trop_court(self, client):
        data = {
            "email": "court@test.tg",
            "first_name": "Test", "last_name": "Test",
            "role": "STUDENT",
            "password1": "court",
            "password2": "court",
            "cgu": "on",
        }
        resp = client.post(reverse("accounts:register"), data)
        assert resp.status_code == 200
        assert not User.objects.filter(email="court@test.tg").exists()


# ─── Profil ─────────────────────────────────────────────

class TestProfil:

    def test_profil_inaccessible_sans_connexion(self, client):
        resp = client.get(reverse("accounts:profile"))
        assert resp.status_code == 302
        assert "/login" in resp.url

    def test_profil_accessible_connecte(self, client_etudiant):
        resp = client_etudiant.get(reverse("accounts:profile"))
        assert resp.status_code == 200

    def test_profil_affiche_phone(self, client, etudiant):
        etudiant.phone = "+228 90 12 34 56"
        etudiant.save()
        client.force_login(etudiant)
        resp = client.get(reverse("accounts:profile"))
        assert "+228 90 12 34 56" in resp.content.decode()

    def test_edition_profil_accessible(self, client_etudiant):
        resp = client_etudiant.get(reverse("accounts:profile_edit"))
        assert resp.status_code == 200

    def test_edition_profil_sauvegarde(self, client, etudiant):
        client.force_login(etudiant)
        data = {
            "first_name": "Nouveau",
            "last_name": "Nom",
            "phone": "+228 99 88 77 66",
            "genre": "M",
            "langue_preferee": "fr",
            "timezone": "Africa/Lome",
        }
        resp = client.post(reverse("accounts:profile_edit"), data)
        assert resp.status_code == 302
        etudiant.refresh_from_db()
        assert etudiant.first_name == "Nouveau"
        assert etudiant.phone == "+228 99 88 77 66"


# ─── Accueil ────────────────────────────────────────────

class TestAccueil:

    def test_page_accueil_accessible(self, client):
        resp = client.get(reverse("accounts:home"))
        assert resp.status_code == 200

    def test_accueil_contexte_formations(self, client, formation_featured):
        resp = client.get(reverse("accounts:home"))
        assert resp.status_code == 200
        assert "formations_populaires" in resp.context
        assert formation_featured in resp.context["formations_populaires"]

    def test_accueil_contexte_evenements(self, client, evenement):
        resp = client.get(reverse("accounts:home"))
        assert resp.status_code == 200
        assert "evenements_a_venir" in resp.context
        assert evenement in resp.context["evenements_a_venir"]

    def test_accueil_evenement_passe_absent(self, client, evenement_passe):
        resp = client.get(reverse("accounts:home"))
        assert resp.status_code == 200
        assert evenement_passe not in resp.context["evenements_a_venir"]
