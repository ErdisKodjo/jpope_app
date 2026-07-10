"""URLs API Marketing & CRM."""
from django.urls import path
from . import views

app_name = "marketing-api"

urlpatterns = [
    # Segments
    path("segments/", views.SegmentListCreateView.as_view(), name="segments"),
    path("segments/<uuid:pk>/", views.SegmentDetailView.as_view(), name="segment-detail"),

    # Campagnes
    path("campagnes/", views.CampagneListCreateView.as_view(), name="campagnes"),
    path("campagnes/<uuid:pk>/", views.CampagneDetailView.as_view(), name="campagne-detail"),
    path("campagnes/<uuid:pk>/activer/", views.CampagneActiverView.as_view(), name="campagne-activer"),
    path("campagnes/<uuid:pk>/stats/", views.CampagneStatsView.as_view(), name="campagne-stats"),

    # Leads
    path("leads/", views.LeadListView.as_view(), name="leads"),
    path("leads/<uuid:pk>/facturer/", views.LeadFacturerView.as_view(), name="lead-facturer"),

    # CRM Candidatures
    path("candidatures/", views.CandidatureCRMListView.as_view(), name="candidatures"),
    path("candidatures/<uuid:pk>/", views.CandidatureCRMDetailView.as_view(), name="candidature-detail"),
    path("candidatures/<uuid:pk>/<str:action>/", views.CandidatureCRMActionView.as_view(), name="candidature-action"),
    path("candidatures/<uuid:pk>/sync/", views.SyncExterneView.as_view(), name="candidature-sync"),

    # Stats
    path("pipeline/stats/", views.PipelineStatsView.as_view(), name="pipeline-stats"),
]
