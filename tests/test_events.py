"""
Tests d'intégration — module events (événements).
"""
import html
import pytest
from django.urls import reverse
from django.utils.timezone import now, timedelta

pytestmark = pytest.mark.django_db


class TestEvenementList:

    def test_liste_evenements_accessible(self, client):
        resp = client.get(reverse("events:event-list"))
        assert resp.status_code == 200

    def test_liste_affiche_evenement_publie(self, client, evenement):
        resp = client.get(reverse("events:event-list"))
        content = html.unescape(resp.content.decode())
        assert evenement.titre in content

    def test_liste_evenement_termine_absent(self, client, evenement_passe):
        resp = client.get(reverse("events:event-list"))
        assert resp.status_code == 200
        content = html.unescape(resp.content.decode())
        assert evenement_passe.titre not in content

    def test_liste_evenement_filtre_type(self, client, evenement):
        resp = client.get(reverse("events:event-list") + "?type=SALON")
        assert resp.status_code == 200


class TestEvenementDetail:

    def test_detail_evenement_accessible(self, client, evenement):
        resp = client.get(reverse("events:event-detail", kwargs={"slug": evenement.slug}))
        assert resp.status_code == 200

    def test_detail_evenement_affiche_titre(self, client, evenement):
        resp = client.get(reverse("events:event-detail", kwargs={"slug": evenement.slug}))
        content = html.unescape(resp.content.decode())
        assert evenement.titre in content

    def test_detail_evenement_affiche_lieu(self, client, evenement):
        resp = client.get(reverse("events:event-detail", kwargs={"slug": evenement.slug}))
        assert evenement.lieu_nom in resp.content.decode()

    def test_detail_evenement_affiche_connexion_si_anon(self, client, evenement):
        resp = client.get(reverse("events:event-detail", kwargs={"slug": evenement.slug}))
        assert "Se connecter" in resp.content.decode()

    def test_detail_evenement_affiche_inscription_si_connecte(self, client_etudiant, evenement):
        resp = client_etudiant.get(reverse("events:event-detail", kwargs={"slug": evenement.slug}))
        assert "S" in resp.content.decode()

    def test_detail_evenement_slug_invalide_404(self, client):
        resp = client.get(reverse("events:event-detail", kwargs={"slug": "inexistant-zzz"}))
        assert resp.status_code == 404


class TestHomeEvenements:

    def test_home_affiche_evenements_a_venir(self, client, evenement):
        resp = client.get(reverse("accounts:home"))
        content = html.unescape(resp.content.decode())
        assert evenement.titre in content

    def test_home_naffiche_pas_evenement_termine(self, client, evenement_passe):
        resp = client.get(reverse("accounts:home"))
        content = html.unescape(resp.content.decode())
        assert evenement_passe.titre not in content

    def test_home_max_2_evenements(self, client):
        from apps.events.models import Evenement
        from apps.events.models.enums import StatutEvenement
        for i in range(5):
            Evenement.objects.create(
                titre=f"Evenement test {i}",
                slug=f"evenement-test-{i}",
                date_debut=now() + timedelta(days=i + 1),
                statut=StatutEvenement.PUBLIE,
            )
        resp = client.get(reverse("accounts:home"))
        assert len(resp.context["evenements_a_venir"]) <= 2
