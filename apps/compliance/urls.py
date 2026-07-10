"""URLs web de l'app compliance (RGPD)."""
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

app_name = "compliance"


class RGPDInfoView(LoginRequiredMixin, TemplateView):
    """Page d'information centrale sur les droits RGPD de l'utilisateur."""
    template_name = "compliance/info.html"


urlpatterns = [
    path("", RGPDInfoView.as_view(), name="info"),
]
