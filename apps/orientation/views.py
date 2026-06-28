"""
Vues web pour l'application orientation.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView

from .models import TestOrientation, ResultatTest, Recommandation, StatutTest


class OrientationHomeView(TemplateView):
    """Page d'accueil du module orientation."""
    template_name = "orientation/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tests_featured"] = TestOrientation.objects.filter(
            is_active=True,
            is_public=True,
            is_featured=True,
        ).order_by("ordre")[:3]
        return context


class TestListView(ListView):
    """Liste des tests d'orientation disponibles."""
    model = TestOrientation
    template_name = "orientation/test_list.html"
    context_object_name = "tests"

    def get_queryset(self):
        return TestOrientation.objects.filter(
            is_active=True,
            is_public=True,
        ).order_by("ordre", "nom")


class TestDetailView(DetailView):
    """Détail et présentation d'un test d'orientation."""
    model = TestOrientation
    template_name = "orientation/test_detail.html"
    context_object_name = "test"
    slug_field = "slug"

    def get_queryset(self):
        return TestOrientation.objects.filter(is_active=True, is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Vérifier si l'étudiant a déjà passé ce test
            context["dernier_resultat"] = (
                ResultatTest.objects
                .filter(
                    reponse_utilisateur__etudiant=self.request.user,
                    reponse_utilisateur__test=self.object,
                )
                .order_by("-date_calcul")
                .first()
            )
        return context


class ResultatListView(LoginRequiredMixin, ListView):
    """Liste des résultats de l'utilisateur connecté."""
    model = ResultatTest
    template_name = "orientation/resultat_list.html"
    context_object_name = "resultats"

    def get_queryset(self):
        return ResultatTest.objects.filter(
            reponse_utilisateur__etudiant=self.request.user,
        ).select_related(
            "reponse_utilisateur__test"
        ).order_by("-date_calcul")


class ResultatDetailView(LoginRequiredMixin, DetailView):
    """Détail d'un résultat d'orientation."""
    model = ResultatTest
    template_name = "orientation/resultat_detail.html"
    context_object_name = "resultat"

    def get_queryset(self):
        return ResultatTest.objects.filter(
            reponse_utilisateur__etudiant=self.request.user,
        ).select_related("reponse_utilisateur__test")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recommandations"] = Recommandation.objects.filter(
            resultat_test=self.object,
        ).select_related("formation", "metier", "etablissement").order_by(
            "plan", "ordre", "-taux_compatibilite"
        )
        return context


class RecommandationListView(LoginRequiredMixin, ListView):
    """Liste des recommandations de l'utilisateur."""
    model = Recommandation
    template_name = "orientation/recommandation_list.html"
    context_object_name = "recommandations"

    def get_queryset(self):
        qs = Recommandation.objects.filter(
            etudiant=self.request.user,
        ).select_related("formation", "metier", "etablissement")

        # Filtre par plan
        plan = self.request.GET.get("plan")
        if plan:
            qs = qs.filter(plan=plan)

        return qs.order_by("plan", "ordre", "-taux_compatibilite")
