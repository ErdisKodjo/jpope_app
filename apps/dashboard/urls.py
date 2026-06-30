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
]
