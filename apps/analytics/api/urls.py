"""
URLs de l'API analytics.
"""
from django.urls import path

from . import views

app_name = "analytics-api"

urlpatterns = [
    # Tracking
    path(
        "track/pageview/",
        views.TrackPageViewAPIView.as_view(),
        name="track-pageview",
    ),

    # Statistiques
    path(
        "stats/daily/",
        views.DailyStatsListView.as_view(),
        name="daily-stats",
    ),
    path(
        "dashboard/",
        views.DashboardSummaryView.as_view(),
        name="dashboard-summary",
    ),

    # KPIs
    path(
        "kpis/",
        views.KPIListView.as_view(),
        name="kpi-list",
    ),
    path(
        "kpis/<str:kpi_code>/evolution/",
        views.KPIEvolutionView.as_view(),
        name="kpi-evolution",
    ),
]
