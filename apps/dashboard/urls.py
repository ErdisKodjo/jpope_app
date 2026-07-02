from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),

    # ── Conseiller : gestion de ses fiches ──
    path("fiches/",
         views.CounselorEvalListView.as_view(),
         name="conseiller-eval-list"),
    path("fiches/nouvelle/",
         views.CounselorEvalCreateView.as_view(),
         name="conseiller-eval-create"),
    path("fiches/<uuid:pk>/",
         views.CounselorEvalDetailView.as_view(),
         name="conseiller-eval-detail"),
    path("fiches/<uuid:pk>/soumettre/",
         views.CounselorEvalSubmitView.as_view(),
         name="conseiller-eval-submit"),

    # ── Admin : revue des fiches soumises ──
    path("admin/fiches/",
         views.AdminEvalListView.as_view(),
         name="admin-eval-list"),
    path("admin/fiches/<uuid:pk>/revue/",
         views.AdminEvalReviewView.as_view(),
         name="admin-eval-review"),

    # ── Phase 3 : Vœux ──
    path("voeux/",
         views.MesVoeuxView.as_view(),
         name="mes-voeux"),
    path("voeux/nouveau/",
         views.VoeuCreateView.as_view(),
         name="voeu-create"),
    path("voeux/<uuid:pk>/modifier/",
         views.VoeuUpdateView.as_view(),
         name="voeu-update"),
    path("voeux/<uuid:pk>/statut/",
         views.VoeuUpdateStatutView.as_view(),
         name="voeu-update-statut"),
    path("voeux/<uuid:pk>/supprimer/",
         views.VoeuDeleteView.as_view(),
         name="voeu-delete"),

    # ── Phase 3 : Démarches ──
    path("demarches/",
         views.MesDemarchesView.as_view(),
         name="mes-demarches"),
    path("demarches/nouvelle/",
         views.DemarcheCreateView.as_view(),
         name="demarche-create"),
    path("demarches/<uuid:pk>/modifier/",
         views.DemarcheUpdateView.as_view(),
         name="demarche-update"),

    # ── Phase 3 : Favoris ──
    path("favoris/",
         views.MesFavorisView.as_view(),
         name="mes-favoris"),
    path("favoris/<str:type_entite>/<uuid:pk>/toggle/",
         views.ToggleFavoriView.as_view(),
         name="favori-toggle"),
]
