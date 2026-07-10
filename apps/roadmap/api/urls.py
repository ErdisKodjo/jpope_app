"""URLs API roadmap."""
from django.urls import path
from . import views

app_name = "roadmap-api"

urlpatterns = [
    path("progression/", views.RoadmapProgressionView.as_view(), name="progression"),
    path("init/", views.RoadmapInitView.as_view(), name="init"),
    path("etapes/", views.MesEtapesListView.as_view(), name="etapes"),
    path("etapes/<uuid:pk>/", views.EtapeDetailView.as_view(), name="etape-detail"),
    path("etapes/<uuid:pk>/<str:action>/", views.EtapeActionView.as_view(), name="etape-action"),
    path("etapes-a-venir/", views.EtapesAvenirView.as_view(), name="etapes-a-venir"),
    path("jalons/", views.JalonsAvenirView.as_view(), name="jalons"),
]
