"""
Factories pour les tests catalog.
"""
import factory
from factory.django import DjangoModelFactory

from apps.catalog.models import Domaine, Metier, Etablissement, Formation


class DomaineFactory(DjangoModelFactory):
    class Meta:
        model = Domaine

    nom = factory.Sequence(lambda n: f"Domaine {n}")
    description = factory.Faker("sentence")
    icon = "📚"
    is_active = True


class MetierFactory(DjangoModelFactory):
    class Meta:
        model = Metier

    nom = factory.Sequence(lambda n: f"Métier {n}")
    domaine = factory.SubFactory(DomaineFactory)
    revenu_min = 150000
    revenu_max = 800000
    revenu_moyen = 350000
    taux_emploi = 75
    demande_marche = "FORTE"
    niveau_etude_requis = "BAC+3"
    pays_concernes = factory.LazyFunction(lambda: ["Togo", "Bénin"])
    is_active = True


class EtablissementFactory(DjangoModelFactory):
    class Meta:
        model = Etablissement

    nom = factory.Sequence(lambda n: f"Établissement {n}")
    ville = "Lomé"
    pays = "Togo"
    type = "PRIVE_LAIC"
    statut = "AGREÉ"
    frais_scolarite_annuel_max = 800000
    taux_reussite = 75
    taux_insertion_professionnelle = 70
    is_active = True
    is_verified = True


class FormationFactory(DjangoModelFactory):
    class Meta:
        model = Formation

    nom = factory.Sequence(lambda n: f"Formation {n}")
    etablissement = factory.SubFactory(EtablissementFactory)
    domaine = factory.SubFactory(DomaineFactory)
    niveau = "LICENCE"
    duree_annees = 3
    cout_annuel = 600000
    taux_reussite = 75
    taux_insertion_12mois = 70
    salaire_sortie_moyen = 300000
    importance_strategique = "MOYENNE"
    is_active = True
