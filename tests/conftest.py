"""
Fixtures partagées pour tous les tests AvenSU-Orienta.
"""
import pytest
from django.utils.timezone import now, timedelta

from apps.accounts.models import User
from apps.accounts.models.enums import UserRole, StatutCompte


# ─── Utilisateurs ───────────────────────────────────────

@pytest.fixture
def etudiant(db):
    return User.objects.create_user(
        email="etudiant@test.tg",
        password="TestPass123!",
        first_name="Yao",
        last_name="Agbeko",
        role=UserRole.STUDENT,
        statut_compte=StatutCompte.ACTIF,
        is_active=True,
        profile_complete=True,
    )


@pytest.fixture
def conseiller(db):
    return User.objects.create_user(
        email="conseiller@test.tg",
        password="TestPass123!",
        first_name="Ama",
        last_name="Koffi",
        role=UserRole.COUNSELOR,
        statut_compte=StatutCompte.ACTIF,
        is_active=True,
        profile_complete=True,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@test.tg",
        password="AdminPass123!",
        first_name="Admin",
        last_name="Test",
    )


@pytest.fixture
def client_etudiant(client, etudiant):
    client.force_login(etudiant)
    return client


@pytest.fixture
def client_admin(client, admin_user):
    client.force_login(admin_user)
    return client


# ─── Catalog ────────────────────────────────────────────

@pytest.fixture
def domaine(db):
    from apps.catalog.models import Domaine
    return Domaine.objects.create(nom="Informatique", slug="informatique")


@pytest.fixture
def etablissement(db):
    from apps.catalog.models import Etablissement
    return Etablissement.objects.create(
        nom="Université de Lomé",
        sigle="UL",
        ville="Lomé",
        pays="Togo",
    )


@pytest.fixture
def formation(db, etablissement, domaine):
    from apps.catalog.models import Formation
    from apps.catalog.models.enums import NiveauFormation
    return Formation.objects.create(
        nom="Licence Informatique",
        etablissement=etablissement,
        domaine=domaine,
        niveau=NiveauFormation.LICENCE,
        cout_annuel=350000,
        duree_annees=3,
    )


@pytest.fixture
def formation_featured(db, etablissement, domaine):
    from apps.catalog.models import Formation
    from apps.catalog.models.enums import NiveauFormation
    return Formation.objects.create(
        nom="Master Informatique",
        etablissement=etablissement,
        domaine=domaine,
        niveau=NiveauFormation.MASTER,
        cout_annuel=500000,
        duree_annees=2,
        is_featured=True,
    )


# ─── Events ─────────────────────────────────────────────

@pytest.fixture
def evenement(db):
    from apps.events.models import Evenement
    from apps.events.models.enums import StatutEvenement
    return Evenement.objects.create(
        titre="Salon de l'Enseignement Supérieur",
        slug="salon-enseignement-2026",
        description="Grand salon annuel des formations.",
        description_courte="50+ établissements réunis.",
        date_debut=now() + timedelta(days=10),
        lieu_nom="Palais des Congrès",
        ville="Lomé",
        statut=StatutEvenement.PUBLIE,
    )


@pytest.fixture
def evenement_passe(db):
    from apps.events.models import Evenement
    from apps.events.models.enums import StatutEvenement
    return Evenement.objects.create(
        titre="Conférence passée",
        slug="conference-passee-2025",
        date_debut=now() - timedelta(days=30),
        statut=StatutEvenement.TERMINE,
    )
