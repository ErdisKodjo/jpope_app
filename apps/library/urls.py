"""URLs web de la bibliothèque (page catalogue publique)."""
from django.urls import path
from django.views.generic import TemplateView

app_name = "library"


urlpatterns = [
    path("", TemplateView.as_view(template_name="library/catalogue.html"), name="catalogue"),
    path("mes-favoris/", TemplateView.as_view(template_name="library/mes_favoris.html"), name="mes_favoris"),
]
