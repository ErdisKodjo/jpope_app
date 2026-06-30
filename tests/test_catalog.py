"""
Tests d'intégration — module catalog (formations, établissements).
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestFormationList:

    def test_liste_formations_accessible(self, client):
        resp = client.get(reverse("catalog:formation-list"))
        assert resp.status_code == 200

    def test_liste_formations_contient_formation(self, client, formation):
        resp = client.get(reverse("catalog:formation-list"))
        assert resp.status_code == 200
        assert formation.nom in resp.content.decode()

    def test_liste_formations_filtre_niveau(self, client, formation, formation_featured):
        resp = client.get(reverse("catalog:formation-list") + "?niveau=LICENCE")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert formation.nom in content
        assert formation_featured.nom not in content

    def test_liste_formations_filtre_recherche(self, client, formation):
        resp = client.get(reverse("catalog:formation-list") + "?q=Licence")
        assert resp.status_code == 200
        assert formation.nom in resp.content.decode()

    def test_liste_formations_duree_annees_affichee(self, client, formation):
        resp = client.get(reverse("catalog:formation-list"))
        content = resp.content.decode()
        assert "3 an" in content

    def test_liste_formations_aucun_resultat(self, client):
        resp = client.get(reverse("catalog:formation-list") + "?q=xqznotexist")
        assert resp.status_code == 200
        assert "Aucune formation" in resp.content.decode()


class TestFormationDetail:

    def test_detail_formation_accessible(self, client, formation):
        resp = client.get(reverse("catalog:formation-detail", kwargs={"slug": formation.slug}))
        assert resp.status_code == 200

    def test_detail_formation_affiche_nom(self, client, formation):
        resp = client.get(reverse("catalog:formation-detail", kwargs={"slug": formation.slug}))
        assert formation.nom in resp.content.decode()

    def test_detail_formation_slug_invalide_404(self, client):
        resp = client.get(reverse("catalog:formation-detail", kwargs={"slug": "inexistant-zzz"}))
        assert resp.status_code == 404


class TestEtablissementList:

    def test_liste_etablissements_accessible(self, client):
        resp = client.get(reverse("catalog:etablissement-list"))
        assert resp.status_code == 200

    def test_liste_etablissements_contient_etablissement(self, client, etablissement):
        resp = client.get(reverse("catalog:etablissement-list"))
        assert etablissement.nom in resp.content.decode()


class TestEtablissementDetail:

    def test_detail_etablissement_accessible(self, client, etablissement):
        resp = client.get(reverse("catalog:etablissement-detail", kwargs={"slug": etablissement.slug}))
        assert resp.status_code == 200

    def test_detail_etablissement_slug_invalide_404(self, client):
        resp = client.get(reverse("catalog:etablissement-detail", kwargs={"slug": "inexistant-zzz"}))
        assert resp.status_code == 404
