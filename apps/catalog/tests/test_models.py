"""
Tests des modèles catalog.
"""
import pytest

from apps.catalog.models import Domaine, Metier, Etablissement, Formation
from apps.catalog.tests.factories import (
    DomaineFactory,
    MetierFactory,
    EtablissementFactory,
    FormationFactory,
)


@pytest.mark.django_db
class TestDomaine:
    def test_slug_auto_genere(self):
        domaine = DomaineFactory(nom="Informatique & Numérique")
        assert domaine.slug == "informatique-numerique"

    def test_slug_non_ecrase_si_existant(self):
        domaine = DomaineFactory(nom="Santé", slug="sante-custom")
        assert domaine.slug == "sante-custom"

    def test_str_retourne_nom(self):
        domaine = DomaineFactory(nom="Droit")
        assert str(domaine) == "Droit"

    def test_is_active_par_defaut(self):
        domaine = DomaineFactory()
        assert domaine.is_active is True

    def test_domaine_inactif(self):
        domaine = DomaineFactory(is_active=False)
        assert domaine.is_active is False

    def test_nom_unique(self):
        from django.db import IntegrityError
        DomaineFactory(nom="Gestion")
        with pytest.raises(IntegrityError):
            DomaineFactory(nom="Gestion")

    def test_compteurs_par_defaut_zero(self):
        domaine = DomaineFactory()
        assert domaine.nombre_formations == 0
        assert domaine.nombre_metiers == 0

    def test_compteurs_mise_a_jour(self):
        domaine = DomaineFactory()
        domaine.nombre_formations = 5
        domaine.nombre_metiers = 3
        domaine.save()
        domaine.refresh_from_db()
        assert domaine.nombre_formations == 5
        assert domaine.nombre_metiers == 3

    def test_couleur_par_defaut(self):
        domaine = DomaineFactory()
        assert domaine.couleur == "#3B82F6"

    def test_ordering_par_ordre_puis_nom(self):
        DomaineFactory(nom="Zara", ordre=2)
        DomaineFactory(nom="Alpha", ordre=1)
        DomaineFactory(nom="Beta", ordre=1)
        qs = list(Domaine.objects.filter(is_active=True))
        noms = [d.nom for d in qs]
        idx_alpha = noms.index("Alpha")
        idx_beta = noms.index("Beta")
        idx_zara = noms.index("Zara")
        assert idx_alpha < idx_beta < idx_zara

    def test_metiers_lies(self):
        domaine = DomaineFactory()
        MetierFactory(domaine=domaine)
        MetierFactory(domaine=domaine)
        assert domaine.metiers.count() == 2

    def test_formations_liees(self):
        domaine = DomaineFactory()
        FormationFactory(domaine=domaine)
        assert domaine.formations.count() == 1


@pytest.mark.django_db
class TestMetier:
    def test_score_attractivite_calcule(self):
        metier = MetierFactory(
            revenu_moyen=500000,
            taux_emploi=80,
            demande_marche="TRES_FORTE",
        )
        assert metier.score_attractivite > 0
        assert metier.score_attractivite <= 100

    def test_revenu_moyen_formate(self):
        metier = MetierFactory(revenu_moyen=350000)
        assert "350 000" in metier.revenu_moyen_formate
        assert "FCFA" in metier.revenu_moyen_formate

    def test_fourchette_revenu(self):
        metier = MetierFactory(revenu_min=150000, revenu_max=800000)
        assert "150 000" in metier.fourchette_revenu
        assert "800 000" in metier.fourchette_revenu


@pytest.mark.django_db
class TestEtablissement:
    def test_slug_auto_genere(self):
        etab = EtablissementFactory(nom="Université de Lomé")
        assert etab.slug == "universite-de-lome"

    def test_fourchette_frais(self):
        etab = EtablissementFactory(
            frais_scolarite_annuel_min=500000,
            frais_scolarite_annuel_max=800000,
        )
        assert "500 000" in etab.fourchette_frais
        assert "800 000" in etab.fourchette_frais

    def test_est_abordable(self):
        etab = EtablissementFactory(frais_scolarite_annuel_max=400000)
        assert etab.est_abordable

        etab2 = EtablissementFactory(frais_scolarite_annuel_max=1500000)
        assert not etab2.est_abordable


@pytest.mark.django_db
class TestFormation:
    def test_cout_total(self):
        formation = FormationFactory(
            cout_annuel=600000,
            frais_inscription=50000,
            frais_dossier=10000,
            duree_annees=3,
        )
        # 50000 + 10000 + (600000 * 3) = 1860000
        assert formation.cout_total == 1860000

    def test_score_qualite_calcule(self):
        formation = FormationFactory(
            taux_reussite=80,
            taux_insertion_12mois=75,
            cout_annuel=500000,
            importance_strategique="ELEVEE",
            salaire_sortie_moyen=400000,
        )
        assert formation.score_qualite > 0
        assert formation.score_qualite <= 100

    def test_retour_sur_investissement(self):
        formation = FormationFactory(
            cout_annuel=600000,
            frais_inscription=50000,
            frais_dossier=10000,
            duree_annees=3,
            salaire_sortie_moyen=400000,
        )
        rsi = formation.retour_sur_investissement_annees
        assert rsi is not None
        assert rsi > 0
