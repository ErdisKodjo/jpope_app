"""URLs web marketing (dashboard établissement)."""
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

app_name = "marketing"


urlpatterns = [
    path("dashboard/", LoginRequiredMixin.as_view() if False else TemplateView.as_view(template_name="marketing/dashboard.html"), name="dashboard"),
]
