"""
Tests des vues web Domaine (DomaineListView, DomaineDetailView).
"""
import pytest
from django.urls import reverse

from apps.catalog.tests.factories import DomaineFactory, MetierFactory, FormationFactory


@pytest.mark.django_db
class TestDomaineListView:
    def test_liste_domaines_accessible(self, client):
        url = reverse("catalog:domaine-list")
        response = client.get(url)
        assert response.status_code == 200

    def test_liste_affiche_domaines_actifs(self, client):
        DomaineFactory(nom="Informatique", is_active=True)
        DomaineFactory(nom="Santé", is_active=True)
        response = client.get(reverse("catalog:domaine-list"))
        contenu = response.content.decode()
        assert "Informatique" in contenu
        assert "Santé" in contenu

    def test_liste_exclut_domaines_inactifs(self, client):
        DomaineFactory(nom="Visible", is_active=True)
        DomaineFactory(nom="Cache", is_active=False)
        response = client.get(reverse("catalog:domaine-list"))
        contenu = response.content.decode()
        assert "Visible" in contenu
        assert "Cache" not in contenu

    def test_liste_contexte_contient_domaines(self, client):
        DomaineFactory.create_batch(3, is_active=True)
        response = client.get(reverse("catalog:domaine-list"))
        assert "domaines" in response.context
        assert response.context["domaines"].count() >= 3

    def test_liste_contexte_contient_stats(self, client):
        response = client.get(reverse("catalog:domaine-list"))
        assert "stats" in response.context

    def test_liste_ordre_par_ordre_puis_nom(self, client):
        DomaineFactory(nom="Zara", ordre=2, is_active=True)
        DomaineFactory(nom="Alpha", ordre=1, is_active=True)
        response = client.get(reverse("catalog:domaine-list"))
        domaines = list(response.context["domaines"])
        noms = [d.nom for d in domaines]
        assert noms.index("Alpha") < noms.index("Zara")


@pytest.mark.django_db
class TestDomaineDetailView:
    def test_detail_accessible(self, client):
        domaine = DomaineFactory(nom="Droit")
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": domaine.slug}))
        assert response.status_code == 200

    def test_detail_affiche_nom_domaine(self, client):
        domaine = DomaineFactory(nom="Gestion")
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": domaine.slug}))
        assert "Gestion" in response.content.decode()

    def test_detail_slug_invalide_404(self, client):
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": "inexistant"}))
        assert response.status_code == 404

    def test_detail_domaine_inactif_404(self, client):
        domaine = DomaineFactory(is_active=False)
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": domaine.slug}))
        assert response.status_code == 404

    def test_detail_contexte_contient_metiers(self, client):
        domaine = DomaineFactory()
        MetierFactory(domaine=domaine, is_active=True)
        MetierFactory(domaine=domaine, is_active=True)
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": domaine.slug}))
        assert "metiers" in response.context
        assert len(response.context["metiers"]) == 2

    def test_detail_exclut_metiers_inactifs(self, client):
        domaine = DomaineFactory()
        MetierFactory(domaine=domaine, is_active=True)
        MetierFactory(domaine=domaine, is_active=False)
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": domaine.slug}))
        assert len(response.context["metiers"]) == 1

    def test_detail_contexte_contient_formations(self, client):
        domaine = DomaineFactory()
        FormationFactory(domaine=domaine, is_active=True)
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": domaine.slug}))
        assert "formations" in response.context
        assert len(response.context["formations"]) == 1

    def test_detail_limite_10_metiers(self, client):
        domaine = DomaineFactory()
        MetierFactory.create_batch(15, domaine=domaine, is_active=True)
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": domaine.slug}))
        assert len(response.context["metiers"]) <= 10

    def test_detail_limite_10_formations(self, client):
        domaine = DomaineFactory()
        FormationFactory.create_batch(12, domaine=domaine, is_active=True)
        response = client.get(reverse("catalog:domaine-detail", kwargs={"slug": domaine.slug}))
        assert len(response.context["formations"]) <= 10
