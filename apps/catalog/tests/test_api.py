"""
Tests de l'API catalog.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.catalog.tests.factories import (
    DomaineFactory,
    MetierFactory,
    EtablissementFactory,
    FormationFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestDomaineAPI:
    def test_list_domaines(self, api_client):
        DomaineFactory.create_batch(3)
        url = reverse("catalog-api:domaines-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 3

    def test_retrieve_domaine(self, api_client):
        domaine = DomaineFactory(nom="Informatique")
        url = reverse("catalog-api:domaines-detail", kwargs={"slug": domaine.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nom"] == "Informatique"


@pytest.mark.django_db
class TestMetierAPI:
    def test_list_metiers(self, api_client):
        MetierFactory.create_batch(5)
        url = reverse("catalog-api:metiers-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_metier(self, api_client):
        metier = MetierFactory(nom="Développeur")
        url = reverse("catalog-api:metiers-detail", kwargs={"slug": metier.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nom"] == "Développeur"

    def test_filter_metier_by_demande(self, api_client):
        MetierFactory(demande_marche="TRES_FORTE")
        MetierFactory(demande_marche="FAIBLE")
        url = reverse("catalog-api:metiers-list")
        response = api_client.get(url, {"demande": "TRES_FORTE"})
        assert response.status_code == status.HTTP_200_OK
        for metier in response.data["results"]:
            assert metier["demande_marche"] == "TRES_FORTE"


@pytest.mark.django_db
class TestEtablissementAPI:
    def test_list_etablissements(self, api_client):
        EtablissementFactory.create_batch(3)
        url = reverse("catalog-api:etablissements-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_etablissement(self, api_client):
        etab = EtablissementFactory(nom="École Test")
        url = reverse("catalog-api:etablissements-detail", kwargs={"slug": etab.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_ville(self, api_client):
        EtablissementFactory(ville="Lomé")
        EtablissementFactory(ville="Kara")
        url = reverse("catalog-api:etablissements-list")
        response = api_client.get(url, {"ville": "Lomé"})
        assert response.status_code == status.HTTP_200_OK
        for etab in response.data["results"]:
            assert etab["ville"] == "Lomé"

    def test_create_etablissement_unauthenticated(self, api_client):
        url = reverse("catalog-api:etablissements-list")
        data = {"nom": "Nouvelle École", "ville": "Lomé"}
        response = api_client.post(url, data, format="json")
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestFormationAPI:
    def test_list_formations(self, api_client):
        FormationFactory.create_batch(4)
        url = reverse("catalog-api:formations-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_formation(self, api_client):
        formation = FormationFactory(nom="Licence Informatique")
        url = reverse("catalog-api:formations-detail", kwargs={"slug": formation.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_niveau(self, api_client):
        FormationFactory(niveau="LICENCE")
        FormationFactory(niveau="MASTER")
        url = reverse("catalog-api:formations-list")
        response = api_client.get(url, {"niveau": "LICENCE"})
        assert response.status_code == status.HTTP_200_OK
        for f in response.data["results"]:
            assert f["niveau"] == "LICENCE"


@pytest.mark.django_db
class TestCatalogStatsAPI:
    def test_stats_globales(self, api_client):
        DomaineFactory.create_batch(2)
        MetierFactory.create_batch(3)
        EtablissementFactory.create_batch(2)
        FormationFactory.create_batch(4)

        url = reverse("catalog-api:catalog-stats")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "nombre_etablissements" in response.data
        assert "nombre_formations" in response.data
        assert "nombre_metiers" in response.data
        assert "nombre_domaines" in response.data


@pytest.mark.django_db
class TestComparateurAPI:
    def test_comparer_etablissements(self, api_client):
        e1 = EtablissementFactory()
        e2 = EtablissementFactory()

        url = reverse("catalog-api:comparateur", kwargs={"type_comparaison": "etablissements"})
        response = api_client.post(url, {"ids": [str(e1.id), str(e2.id)]}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["etablissements"]) == 2

    def test_comparer_trop_detablissements(self, api_client):
        ids = [str(EtablissementFactory().id) for _ in range(4)]

        url = reverse("catalog-api:comparateur", kwargs={"type_comparaison": "etablissements"})
        response = api_client.post(url, {"ids": ids}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSimulateurAPI:
    def test_simuler_cout(self, api_client):
        formation = FormationFactory(
            cout_annuel=600000,
            frais_inscription=50000,
            frais_dossier=10000,
            duree_annees=3,
        )

        url = reverse("catalog-api:simulator-cout")
        response = api_client.post(
            url,
            {
                "formation_id": str(formation.id),
                "mode_vie_mensuel": 50000,
                "bourse_montant": 0,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "cout_total" in response.data
        assert response.data["cout_total"] > 0
