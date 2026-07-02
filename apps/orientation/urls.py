"""
URLs web pour l'application orientation.
"""
from django.urls import path

from . import views

app_name = "orientation"

urlpatterns = [
    path("", views.OrientationHomeView.as_view(), name="home"),
    path("tests/", views.TestListView.as_view(), name="test-list"),
    path("tests/<slug:slug>/", views.TestDetailView.as_view(), name="test-detail"),
    path("tests/<slug:slug>/passer/", views.TakeTestView.as_view(), name="take-test"),
    path("tests/<slug:slug>/soumettre/", views.SubmitTestView.as_view(), name="submit-test"),
    path("resultats/", views.ResultatListView.as_view(), name="resultats"),
    path("resultats/<uuid:pk>/", views.ResultatDetailView.as_view(), name="resultat-detail"),
    path("recommandations/", views.RecommandationListView.as_view(), name="recommandations"),
    path("conseiller/resultats/", views.ResultatsConseillerView.as_view(), name="resultats-conseiller"),

    # ── Phase 2 : Accompagnement ──────────────────────────────────
    path("accompagnement/nouveau/", views.DemandeAccompagnementCreateView.as_view(), name="accompagnement-create"),
    path("accompagnement/nouveau/<uuid:resultat_pk>/", views.DemandeAccompagnementCreateView.as_view(), name="accompagnement-create-from-resultat"),
    path("accompagnement/mes-demandes/", views.MesDemandesEtudiantView.as_view(), name="mes-demandes"),
    path("accompagnement/<uuid:pk>/", views.DemandeDetailView.as_view(), name="demande-detail"),
    path("accompagnement/<uuid:pk>/message/", views.EnvoyerMessageView.as_view(), name="envoyer-message"),
    path("accompagnement/<uuid:pk>/evaluer/", views.EvaluerConseillerView.as_view(), name="evaluer-conseiller"),

    # ── Phase 2 : Vues conseillers ────────────────────────────────
    path("conseiller/demandes/", views.DemandesConseillerView.as_view(), name="conseiller-demandes"),
    path("conseiller/demandes/<uuid:pk>/accepter/", views.AccepterDemandeView.as_view(), name="accepter-demande"),
    path("conseiller/demandes/<uuid:pk>/refuser/", views.RefuserDemandeView.as_view(), name="refuser-demande"),
    path("conseiller/questions/proposer/", views.QuestionProposerView.as_view(), name="question-proposer"),
    path("conseiller/questions/", views.MesQuestionsProposees.as_view(), name="mes-questions-proposees"),

    # ── Court terme : Conseillers & RDV ──────────────────────────
    path("conseillers/", views.ListeConseillersView.as_view(), name="conseillers"),
    path("conseillers/<uuid:pk>/", views.ConseillerDetailPublicView.as_view(), name="conseiller-detail"),
    path("mes-rdv/", views.MesRendezVousView.as_view(), name="mes-rdv"),
    path("accompagnement/<uuid:pk>/rdv/proposer/", views.ProposerRendezVousView.as_view(), name="rdv-proposer"),
    path("rdv/<uuid:pk>/confirmer/", views.ConfirmerRendezVousView.as_view(), name="rdv-confirmer"),
    path("rdv/<uuid:pk>/annuler/", views.AnnulerRendezVousView.as_view(), name="rdv-annuler"),

    # ── Phase 2 : Vues admin ──────────────────────────────────────
    path("admin/questions-proposees/", views.AdminQuestionsProposees.as_view(), name="admin-questions-proposees"),
    path("admin/questions-proposees/<uuid:pk>/approuver/", views.AdminApprouverQuestion.as_view(), name="admin-approuver-question"),
    path("admin/questions-proposees/<uuid:pk>/rejeter/", views.AdminRejeterQuestion.as_view(), name="admin-rejeter-question"),
    path("admin/ristournes/", views.AdminRistournesView.as_view(), name="admin-ristournes"),
    path("admin/ristournes/<uuid:pk>/payer/", views.AdminPayerRistourneView.as_view(), name="admin-payer-ristourne"),
]
