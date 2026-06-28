from django.urls import path
from . import views

app_name = "dashboard-api"

urlpatterns = [
    path("dashboard/", views.DashboardSummaryView.as_view(), name="summary"),
    path("dashboard/favoris/", views.FavoriListCreateView.as_view(), name="favoris-list"),
    path("dashboard/voeux/", views.VoeuListCreateView.as_view(), name="voeux-list"),
    path("dashboard/demarches/", views.DemarcheListCreateView.as_view(), name="demarches-list"),
    path("dashboard/agenda/", views.AgendaListCreateView.as_view(), name="agenda-list"),
]
