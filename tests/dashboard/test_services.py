"""Tests unitaires pour les services du tableau de bord.

Ces tests couvrent :
- `auth.get_dashboard_profile`
- `score.calculate_test_score`
- `recommendation.generate_recommendations`
- `conseiller.assign_conseiller` et `is_conseiller_accessible`
- `visibility.filter_options`
"""

import pytest
from django.contrib.auth import get_user_model
from apps.dashboard import services
from apps.orientation.models import ResultatTest
from apps.dashboard.models import Counselor

User = get_user_model()

@pytest.fixture
def student_user(db):
    user = User.objects.create_user(username='etudiant', email='etudiant@example.com', password='test', role='STUDENT')
    user.is_student = True
    return user

@pytest.fixture
def counselor_user(db):
    user = User.objects.create_user(username='conseiller', password='test', role='COUNSELOR')
    user.is_counselor = True
    return user

def test_auth_profile(student_user):
    profile = services.auth.get_dashboard_profile(student_user)
    assert profile['id'] == student_user.id
    assert profile['role'] == 'STUDENT'
    # champs spécifiques étudiant doivent être présents (même s'ils sont None)
    assert 'classe' in profile
    assert 'etablissement' in profile

def test_score_calculation(db, student_user):
    # créer quelques résultats de test fictifs
    ResultatTest.objects.create(reponse_utilisateur_id=student_user.id, score=20, category='math')
    ResultatTest.objects.create(reponse_utilisateur_id=student_user.id, score=30, category='français')
    qs = ResultatTest.objects.filter(reponse_utilisateur__etudiant=student_user)
    result = services.score.calculate_test_score(qs)
    assert result['total'] == 50
    assert result['details']['math'] == 20
    assert result['details']['français'] == 30

def test_recommendations(db, student_user):
    score = {'total': 40, 'details': {'math': 15, 'français': 25}}
    recs = services.recommendation.generate_recommendations(student_user, score)
    # doit contenir au moins une recommandation globale et une par catégorie
    types = {r['type'] for r in recs}
    assert 'overall' in types
    assert 'category' in types
    assert any(r['category'] == 'math' for r in recs)

def test_conseiller_assignment(db, student_user, counselor_user):
    # associer le conseiller au student
    student_user.conseiller = counselor_user
    student_user.save()
    assigned = services.conseiller.assign_conseiller(student_user)
    assert assigned['id'] == counselor_user.id
    # test d'accès
    assert services.conseiller.is_conseiller_accessible(student_user, counselor_user)
    # un autre conseiller ne doit pas être accessible
    other = Counselor.objects.create(user=counselor_user)  # placeholder
    assert not services.conseiller.is_conseiller_accessible(student_user, other)

def test_visibility_filters(db, student_user):
    ctx = {}
    services.visibility.filter_options(student_user, ctx)
    assert ctx['show_admin_panel'] is False
    assert ctx['show_create_voeu'] is True
    assert ctx['show_counselor_contact'] is False
