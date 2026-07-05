"""
Tests d'intégration AvenSU-Orienta.
Couvre : rôles & accès, dashboard, favoris, vœux, démarches, conseillers,
         orientation, community, notifications.
"""
import pytest
from datetime import timedelta

from django.urls import reverse
from django.utils.timezone import now

from apps.accounts.models import User
from apps.accounts.models.enums import UserRole, StatutCompte


# ══════════════════════════════════════════════════════════════
# FIXTURES SUPPLÉMENTAIRES
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def etudiant_complet(db):
    """Étudiant avec profile_complete=True pour ne pas être intercepté par le middleware."""
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
def conseiller_complet(db):
    """Conseiller avec profile_complete=True."""
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
def admin_complet(db):
    user = User.objects.create_superuser(
        email="admin@test.tg",
        password="AdminPass123!",
        first_name="Admin",
        last_name="Test",
    )
    user.profile_complete = True
    user.save(update_fields=["profile_complete"])
    return user


@pytest.fixture
def compte_en_attente(db):
    return User.objects.create_user(
        email="attente@test.tg",
        password="TestPass123!",
        role=UserRole.STUDENT,
        statut_compte=StatutCompte.EN_ATTENTE_VERIFICATION,
        is_active=True,
        profile_complete=True,
    )


@pytest.fixture
def conseiller_disponible(db):
    """Conseiller disponible — le signal crée CounselorProfile automatiquement."""
    user = User.objects.create_user(
        email="cons.dispo@test.tg",
        password="TestPass123!",
        first_name="Kokou",
        last_name="Mensah",
        role=UserRole.COUNSELOR,
        statut_compte=StatutCompte.ACTIF,
        is_active=True,
        profile_complete=True,
    )
    # Le signal auto-crée CounselorProfile ; on met juste is_available=True
    profile = user.counselor_profile
    profile.is_available = True
    profile.tarif_consultation = 15000
    profile.annees_experience = 5
    profile.save()
    return user


@pytest.fixture
def domaine(db):
    from apps.catalog.models import Domaine
    return Domaine.objects.create(nom="Informatique", slug="informatique")


@pytest.fixture
def etablissement(db):
    from apps.catalog.models import Etablissement
    return Etablissement.objects.create(
        nom="Université de Lomé", sigle="UL", ville="Lomé", pays="Togo",
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
def evenement(db):
    from apps.events.models import Evenement
    from apps.events.models.enums import StatutEvenement
    return Evenement.objects.create(
        titre="Salon de l'Enseignement Supérieur",
        slug="salon-enseignement-2026",
        description="Grand salon annuel.",
        description_courte="50+ établissements.",
        date_debut=now() + timedelta(days=10),
        lieu_nom="Palais des Congrès",
        ville="Lomé",
        statut=StatutEvenement.PUBLIE,
    )


@pytest.fixture
def voeu(db, etudiant_complet, formation):
    from apps.dashboard.models import Voeu, StatutVoeu
    return Voeu.objects.create(
        etudiant=etudiant_complet,
        formation=formation,
        priorite=1,
        statut=StatutVoeu.BROUILLON,
    )


@pytest.fixture
def demarche(db, etudiant_complet, voeu):
    from apps.dashboard.models import DemarcheInscription, StatutDemarche, TypeDemarche
    return DemarcheInscription.objects.create(
        etudiant=etudiant_complet,
        voeu=voeu,
        formation=voeu.formation,
        titre="Dossier de candidature",
        type=TypeDemarche.INSCRIPTION,
        statut=StatutDemarche.A_FAIRE,
        date_echeance=now() + timedelta(days=7),
    )


@pytest.fixture
def forum(db, domaine):
    from apps.community.models import Forum
    return Forum.objects.create(
        nom="Forum Informatique",
        slug="forum-informatique",
        domaine=domaine,
    )


@pytest.fixture
def client_etudiant(client, etudiant_complet):
    client.force_login(etudiant_complet)
    return client


@pytest.fixture
def client_conseiller(client, conseiller_complet):
    client.force_login(conseiller_complet)
    return client


@pytest.fixture
def client_admin(client, admin_complet):
    client.force_login(admin_complet)
    return client


# ══════════════════════════════════════════════════════════════
# 1. AUTHENTIFICATION & CONNEXION
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestConnexion:
    def test_login_valide_etudiant(self, client, etudiant_complet):
        resp = client.post(reverse("accounts:login"), {
            "username": etudiant_complet.email,
            "password": "TestPass123!",
        })
        assert resp.status_code == 302
        assert resp.url == reverse("accounts:home")

    def test_login_mauvais_mot_de_passe(self, client, etudiant_complet):
        resp = client.post(reverse("accounts:login"), {
            "username": etudiant_complet.email,
            "password": "mauvais!",
        })
        assert resp.status_code == 200

    def test_login_email_inexistant(self, client):
        resp = client.post(reverse("accounts:login"), {
            "username": "inconnu@test.tg",
            "password": "TestPass123!",
        })
        assert resp.status_code == 200

    def test_login_compte_inactif_bloque(self, client, db):
        """Compte INACTIF doit être refusé — seul EmailOrPhoneBackend est actif."""
        user = User.objects.create_user(
            email="inactif@test.tg",
            password="TestPass123!",
            role=UserRole.STUDENT,
            statut_compte=StatutCompte.INACTIF,
            is_active=True,
        )
        resp = client.post(reverse("accounts:login"), {
            "username": user.email,
            "password": "TestPass123!",
        })
        assert resp.status_code == 200

    def test_deconnexion(self, client_etudiant):
        resp = client_etudiant.get(reverse("accounts:logout"))
        assert resp.status_code == 302

    def test_redirect_si_deja_connecte(self, client_etudiant):
        resp = client_etudiant.get(reverse("accounts:login"))
        assert resp.status_code == 302


# ══════════════════════════════════════════════════════════════
# 2. CONTRÔLE D'ACCÈS PAR RÔLE
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestControleAcces:
    def test_anonyme_redirige_vers_login_dashboard(self, client):
        resp = client.get(reverse("dashboard:home"))
        assert resp.status_code == 302
        assert "/login" in resp.url

    def test_anonyme_redirige_vers_login_voeux(self, client):
        resp = client.get(reverse("dashboard:mes-voeux"))
        assert resp.status_code == 302
        assert "/login" in resp.url

    def test_etudiant_acces_dashboard(self, client_etudiant):
        resp = client_etudiant.get(reverse("dashboard:home"))
        assert resp.status_code == 200

    def test_etudiant_acces_mes_voeux(self, client_etudiant):
        resp = client_etudiant.get(reverse("dashboard:mes-voeux"))
        assert resp.status_code == 200

    def test_etudiant_acces_mes_favoris(self, client_etudiant):
        resp = client_etudiant.get(reverse("dashboard:mes-favoris"))
        assert resp.status_code == 200

    def test_etudiant_acces_mes_demarches(self, client_etudiant):
        resp = client_etudiant.get(reverse("dashboard:mes-demarches"))
        assert resp.status_code == 200

    def test_etudiant_bloque_sur_vue_conseiller(self, client_etudiant):
        resp = client_etudiant.get(reverse("dashboard:conseiller-eval-list"))
        assert resp.status_code == 403

    def test_etudiant_bloque_sur_vue_admin(self, client_etudiant):
        resp = client_etudiant.get(reverse("dashboard:admin-eval-list"))
        assert resp.status_code == 403

    def test_conseiller_acces_eval_list(self, client_conseiller):
        resp = client_conseiller.get(reverse("dashboard:conseiller-eval-list"))
        assert resp.status_code == 200

    def test_conseiller_bloque_admin_eval(self, client_conseiller):
        resp = client_conseiller.get(reverse("dashboard:admin-eval-list"))
        assert resp.status_code == 403

    def test_admin_acces_admin_eval_list(self, client_admin):
        resp = client_admin.get(reverse("dashboard:admin-eval-list"))
        assert resp.status_code == 200

    def test_compte_en_attente_bloque_voeux(self, client, compte_en_attente):
        client.force_login(compte_en_attente)
        resp = client.get(reverse("dashboard:mes-voeux"))
        assert resp.status_code == 302
        assert "verification" in resp.url

    def test_compte_en_attente_bloque_demarches(self, client, compte_en_attente):
        client.force_login(compte_en_attente)
        resp = client.get(reverse("dashboard:mes-demarches"))
        assert resp.status_code == 302

    def test_compte_en_attente_bloque_favoris(self, client, compte_en_attente):
        client.force_login(compte_en_attente)
        resp = client.get(reverse("dashboard:mes-favoris"))
        assert resp.status_code == 302


# ══════════════════════════════════════════════════════════════
# 3. DASHBOARD HOME — CONTEXTE SELON LE RÔLE
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestDashboardHome:
    def test_etudiant_voit_compteurs(self, client_etudiant):
        resp = client_etudiant.get(reverse("dashboard:home"))
        assert resp.status_code == 200
        assert "favoris_count" in resp.context
        assert "voeux_count" in resp.context
        assert "demarches_count" in resp.context

    def test_conseiller_voit_compteurs_eval(self, client_conseiller):
        resp = client_conseiller.get(reverse("dashboard:home"))
        assert resp.status_code == 200
        assert "nb_brouillons" in resp.context
        assert "nb_soumises" in resp.context

    def test_admin_voit_evaluations_en_attente(self, client_admin):
        resp = client_admin.get(reverse("dashboard:home"))
        assert resp.status_code == 200
        assert "nb_evaluations_en_attente" in resp.context

    def test_dashboard_timedelta_sans_erreur(self, client, etudiant_complet, formation):
        """Vérifie que timezone.timedelta n'est plus utilisé (bug corrigé)."""
        from apps.dashboard.models import DemarcheInscription, StatutDemarche, TypeDemarche
        DemarcheInscription.objects.create(
            etudiant=etudiant_complet,
            titre="Test urgence",
            type=TypeDemarche.INSCRIPTION,
            statut=StatutDemarche.A_FAIRE,
            date_echeance=now() + timedelta(days=5),
        )
        client.force_login(etudiant_complet)
        resp = client.get(reverse("dashboard:home"))
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════
# 4. VŒUX
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestVoeux:
    def test_creer_voeu(self, client_etudiant, formation):
        resp = client_etudiant.post(
            reverse("dashboard:voeu-create") + f"?formation={formation.pk}",
            {"priorite": 1, "niveau_priorite": "SOUHAITE", "lettre_motivation": "", "notes_etudiant": ""},
        )
        assert resp.status_code == 302
        from apps.dashboard.models import Voeu
        assert Voeu.objects.filter(formation=formation).exists()

    def test_creer_voeu_doublon_bloque(self, client_etudiant, voeu):
        resp = client_etudiant.get(
            reverse("dashboard:voeu-create") + f"?formation={voeu.formation.pk}"
        )
        assert resp.status_code == 302

    def test_supprimer_voeu_brouillon(self, client_etudiant, voeu):
        from apps.dashboard.models import Voeu
        pk = voeu.pk
        resp = client_etudiant.post(reverse("dashboard:voeu-delete", kwargs={"pk": pk}))
        assert resp.status_code == 302
        assert not Voeu.objects.filter(pk=pk).exists()

    def test_supprimer_voeu_soumis_interdit(self, client_etudiant, voeu):
        from apps.dashboard.models import Voeu, StatutVoeu
        voeu.statut = StatutVoeu.SOUMIS
        voeu.save()
        resp = client_etudiant.post(reverse("dashboard:voeu-delete", kwargs={"pk": voeu.pk}))
        assert resp.status_code == 302
        assert Voeu.objects.filter(pk=voeu.pk).exists()

    def test_autre_etudiant_ne_peut_pas_supprimer(self, client, db, voeu):
        autre = User.objects.create_user(
            email="autre@test.tg", password="Pass123456!",
            role=UserRole.STUDENT, statut_compte=StatutCompte.ACTIF,
            is_active=True, profile_complete=True,
        )
        client.force_login(autre)
        resp = client.post(reverse("dashboard:voeu-delete", kwargs={"pk": voeu.pk}))
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════
# 5. FAVORIS
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestFavoris:
    def test_ajouter_favori_formation(self, client_etudiant, formation):
        resp = client_etudiant.post(
            reverse("dashboard:favori-toggle",
                    kwargs={"type_entite": "FORMATION", "pk": formation.pk})
        )
        assert resp.status_code == 302
        from apps.dashboard.models import Favori
        assert Favori.objects.filter(type_entite="FORMATION", formation=formation).exists()

    def test_retirer_favori_formation(self, client_etudiant, etudiant_complet, formation):
        from apps.dashboard.models import Favori
        Favori.objects.create(utilisateur=etudiant_complet, type_entite="FORMATION", formation=formation)
        resp = client_etudiant.post(
            reverse("dashboard:favori-toggle",
                    kwargs={"type_entite": "FORMATION", "pk": formation.pk})
        )
        assert resp.status_code == 302
        assert not Favori.objects.filter(type_entite="FORMATION", formation=formation).exists()

    def test_ajouter_favori_evenement(self, client_etudiant, evenement):
        resp = client_etudiant.post(
            reverse("dashboard:favori-toggle",
                    kwargs={"type_entite": "EVENEMENT", "pk": evenement.pk})
        )
        assert resp.status_code == 302
        from apps.dashboard.models import Favori
        assert Favori.objects.filter(type_entite="EVENEMENT", evenement=evenement).exists()

    def test_type_inconnu_retourne_erreur(self, client_etudiant, formation):
        resp = client_etudiant.post(
            reverse("dashboard:favori-toggle",
                    kwargs={"type_entite": "INCONNU", "pk": formation.pk})
        )
        assert resp.status_code == 302


# ══════════════════════════════════════════════════════════════
# 6. DÉMARCHES
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestDemarches:
    def test_creer_demarche(self, client_etudiant, voeu):
        from apps.dashboard.models import TypeDemarche, StatutDemarche
        resp = client_etudiant.post(reverse("dashboard:demarche-create"), {
            "titre": "Dossier de candidature",
            "type": TypeDemarche.INSCRIPTION,
            "statut": StatutDemarche.A_FAIRE,
            "progression": 0,
            "cout_estime": 0,
            "voeu_pk": str(voeu.pk),
        })
        assert resp.status_code == 302
        from apps.dashboard.models import DemarcheInscription
        assert DemarcheInscription.objects.filter(voeu=voeu).exists()

    def test_demarche_urgente_dans_contexte_dashboard(self, client_etudiant, demarche):
        resp = client_etudiant.get(reverse("dashboard:home"))
        assert resp.status_code == 200
        urgentes = resp.context.get("demarches_urgentes")
        assert urgentes is not None
        assert demarche in urgentes

    def test_modifier_demarche(self, client_etudiant, demarche):
        from apps.dashboard.models import StatutDemarche, TypeDemarche
        resp = client_etudiant.post(
            reverse("dashboard:demarche-update", kwargs={"pk": demarche.pk}),
            {
                "titre": "Dossier modifié",
                "type": TypeDemarche.INSCRIPTION,
                "statut": StatutDemarche.EN_COURS,
                "progression": 30,
                "cout_estime": 0,
            }
        )
        assert resp.status_code == 302
        demarche.refresh_from_db()
        assert demarche.titre == "Dossier modifié"


# ══════════════════════════════════════════════════════════════
# 7. LISTE CONSEILLERS
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestListeConseillers:
    def test_conseillers_actifs_visibles(self, client, conseiller_disponible):
        resp = client.get(reverse("orientation:conseillers"))
        assert resp.status_code == 200
        assert conseiller_disponible in resp.context["conseillers"]

    def test_conseiller_indisponible_masque(self, client, db):
        user = User.objects.create_user(
            email="indisp@test.tg", password="TestPass123!",
            role=UserRole.COUNSELOR, statut_compte=StatutCompte.ACTIF, is_active=True,
        )
        # Le signal crée CounselorProfile avec is_available=True par défaut — on le désactive
        profile = user.counselor_profile
        profile.is_available = False
        profile.save(update_fields=["is_available"])
        resp = client.get(reverse("orientation:conseillers"))
        assert user not in resp.context["conseillers"]

    def test_recherche_par_nom(self, client, conseiller_disponible):
        resp = client.get(reverse("orientation:conseillers") + "?q=Kokou")
        assert resp.status_code == 200
        assert conseiller_disponible in resp.context["conseillers"]

    def test_recherche_sans_resultat(self, client, conseiller_disponible):
        resp = client.get(reverse("orientation:conseillers") + "?q=XYZUNKNOWN")
        assert resp.status_code == 200
        assert len(resp.context["conseillers"]) == 0


# ══════════════════════════════════════════════════════════════
# 8. COMMUNITY — FORUMS & THREADS
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCommunity:
    def test_liste_forums_accessible_anonyme(self, client):
        resp = client.get(reverse("community:forum-list"))
        assert resp.status_code == 200

    def test_detail_forum_accessible(self, client, forum):
        resp = client.get(reverse("community:forum-detail", kwargs={"slug": forum.slug}))
        assert resp.status_code == 200

    def test_creer_thread_necessite_connexion(self, client, forum):
        resp = client.get(
            reverse("community:thread-create", kwargs={"forum_slug": forum.slug})
        )
        assert resp.status_code == 302
        assert "/login" in resp.url

    def test_creer_thread_etudiant_connecte(self, client_etudiant, forum):
        resp = client_etudiant.post(
            reverse("community:thread-create", kwargs={"forum_slug": forum.slug}),
            {"titre": "Ma question sur l'informatique", "contenu": "Bonjour à tous !"}
        )
        assert resp.status_code in (200, 302)


# ══════════════════════════════════════════════════════════════
# 9. NOTIFICATIONS
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestNotifications:
    def test_liste_notifs_necessite_connexion(self, client):
        resp = client.get(reverse("notifications:list"))
        assert resp.status_code == 302

    def test_liste_notifs_accessible_connecte(self, client_etudiant):
        resp = client_etudiant.get(reverse("notifications:list"))
        assert resp.status_code == 200

    def test_marquer_notif_lue(self, client_etudiant, etudiant_complet):
        from apps.notifications.models import Notification
        notif = Notification.objects.create(user=etudiant_complet, titre="Test", message="Msg")
        assert not notif.is_read
        resp = client_etudiant.post(
            reverse("notifications:mark-read", kwargs={"pk": notif.pk})
        )
        assert resp.status_code == 302
        notif.refresh_from_db()
        assert notif.is_read

    def test_marquer_toutes_lues(self, client_etudiant, etudiant_complet):
        from apps.notifications.models import Notification
        for i in range(3):
            Notification.objects.create(user=etudiant_complet, titre=f"Notif {i}", message="msg")
        resp = client_etudiant.post(reverse("notifications:mark-all-read"))
        assert resp.status_code == 302
        assert Notification.objects.filter(user=etudiant_complet, is_read=False).count() == 0


# ══════════════════════════════════════════════════════════════
# 10. CATALOGUE
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCatalogue:
    def test_home_catalogue_accessible(self, client):
        resp = client.get(reverse("catalog:formation-list"))
        assert resp.status_code == 200

    def test_detail_formation_accessible(self, client, formation):
        resp = client.get(
            reverse("catalog:formation-detail", kwargs={"slug": formation.slug})
        )
        assert resp.status_code == 200

    def test_formation_inactive_retourne_404(self, client, formation):
        formation.is_active = False
        formation.save()
        resp = client.get(
            reverse("catalog:formation-detail", kwargs={"slug": formation.slug})
        )
        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════
# 11. ORIENTATION
# ══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestOrientation:
    def test_orientation_home_accessible(self, client):
        resp = client.get(reverse("orientation:home"))
        assert resp.status_code == 200

    def test_liste_tests_necesssite_connexion(self, client):
        resp = client.get(reverse("orientation:test-list"))
        assert resp.status_code == 302

    def test_liste_tests_accessible_etudiant(self, client_etudiant):
        resp = client_etudiant.get(reverse("orientation:test-list"))
        assert resp.status_code == 200

    def test_mes_recommandations_necesssite_connexion(self, client):
        resp = client.get(reverse("orientation:recommandations"))
        assert resp.status_code == 302

    def test_mes_recommandations_accessible_etudiant(self, client_etudiant):
        resp = client_etudiant.get(reverse("orientation:recommandations"))
        assert resp.status_code == 200
