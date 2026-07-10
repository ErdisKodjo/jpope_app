"""URLs API de l'app compliance (RGPD)."""
from django.urls import path
from . import views

app_name = "compliance-api"

urlpatterns = [
    # Consentements
    path("consentements/", views.MesConsentementsView.as_view(), name="consentements"),
    path("consentements/<str:type_consentement>/",
         views.RetirerConsentementView.as_view(), name="retirer_consentement"),

    # Demandes RGPD
    path("demandes/", views.MesDemandesRGPDView.as_view(), name="demandes"),

    # Export & droit à l'oubli
    path("export/", views.ExportDonneesView.as_view(), name="export"),
    path("droit-oubli/", views.DroitOubliView.as_view(), name="droit_oubli"),

    # Journal d'accès
    path("journal/", views.JournalAccesView.as_view(), name="journal"),

    # Politiques de conservation
    path("politiques/", views.PolitiquesConservationView.as_view(), name="politiques"),
]
