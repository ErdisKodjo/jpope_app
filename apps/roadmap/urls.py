"""URLs web roadmap."""
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

app_name = "roadmap"


class RoadmapHomeView(LoginRequiredMixin, TemplateView):
    template_name = "roadmap/home.html"


urlpatterns = [
    path("", RoadmapHomeView.as_view(), name="home"),
]
