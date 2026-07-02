from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.EvenementListView.as_view(), name="event-list"),
    path("mes-evenements/", views.MesEvenementsView.as_view(), name="mes-evenements"),
    path("<slug:slug>/", views.EvenementDetailView.as_view(), name="event-detail"),
    path("<slug:slug>/inscription/", views.InscriptionView.as_view(), name="event-register"),
    path("<slug:slug>/annuler/", views.AnnulerInscriptionView.as_view(), name="event-cancel"),
]
