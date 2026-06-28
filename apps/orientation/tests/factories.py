"""
Factories pour les tests orientation.
"""
import factory
from factory.django import DjangoModelFactory

from apps.orientation.models import (
    TestOrientation, Question, Choice,
    ReponseUtilisateur, DetailReponse,
    ResultatTest, Recommandation,
)
from apps.accounts.tests.factories import StudentFactory
from apps.catalog.tests.factories import FormationFactory, MetierFactory

class TestOrientationFactory(DjangoModelFactory):
    class Meta:
        model = TestOrientation

    nom = factory.Sequence(lambda n: f"Test d'orientation {n}")
    type = "MIXTE"
    duree_estimee_minutes = 15
    is_active = True
    is_public = True
    dimensions_evaluees = factory.LazyFunction(lambda: ["R", "I", "A", "S", "E", "C"])
    methode_scoring = "RIASEC_PONDERE"

class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    test = factory.SubFactory(TestOrientationFactory)
    texte = factory.Faker("sentence")
    type = "ECHELLE_LIKERT"
    ordre = factory.Sequence(lambda n: n + 1)
    poids = 1.0
    dimensions = factory.LazyFunction(lambda: {"R": 1.0, "I": 0.5})
    is_active = True

class ChoiceFactory(DjangoModelFactory):
    class Meta:
        model = Choice

    question = factory.SubFactory(QuestionFactory)
    texte = factory.Faker("sentence")
    ordre = factory.Sequence(lambda n: n + 1)
    scores = factory.LazyFunction(lambda: {"R": 3, "I": 1})

class ReponseUtilisateurFactory(DjangoModelFactory):
    class Meta:
        model = ReponseUtilisateur

    etudiant = factory.SubFactory(StudentFactory)
    test = factory.SubFactory(TestOrientationFactory)
    statut = "EN_COURS"
    nombre_questions_total = 10

class ResultatTestFactory(DjangoModelFactory):
    class Meta:
        model = ResultatTest

    reponse_utilisateur = factory.SubFactory(ReponseUtilisateurFactory)
    score_global = 72.5
    scores_par_dimension = factory.LazyFunction(
        lambda: {"R": 75, "I": 82, "A": 45, "S": 68, "E": 55, "C": 60}
    )
    code_holland = "IRS"
    profil_dominant = "I"
    profil_secondaire = "R"
