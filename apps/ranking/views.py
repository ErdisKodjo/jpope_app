"""
Vues web pour l'application ranking.
"""
from django.views.generic import ListView, DetailView, TemplateView

from .models import Classement


class ClassementListView(ListView):
    """Liste des classements publiés."""
    model = Classement
    template_name = "ranking/classement_list.html"
    context_object_name = "classements"
    paginate_by = 20

    def get_queryset(self):
        qs = Classement.objects.filter(is_published=True).select_related("etablissement")

        annee = self.request.GET.get("annee")
        if annee:
            qs = qs.filter(annee=annee)
        else:
            # Par défaut, afficher l'année la plus récente
            derniere_annee = (
                Classement.objects.filter(is_published=True)
                .order_by("-annee")
                .values_list("annee", flat=True)
                .first()
            )
            if derniere_annee:
                qs = qs.filter(annee=derniere_annee)

        return qs.order_by("rang_national", "-score_final")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["annees"] = (
            Classement.objects.filter(is_published=True)
            .values_list("annee", flat=True)
            .distinct()
            .order_by("-annee")
        )
        context["annee_selectionnee"] = self.request.GET.get("annee")
        return context


class ClassementDetailView(DetailView):
    """Détail d'un classement (établissement + scores)."""
    model = Classement
    template_name = "ranking/classement_detail.html"
    context_object_name = "classement"

    def get_queryset(self):
        return Classement.objects.filter(is_published=True).select_related("etablissement")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classement = self.object
        # Historique des classements de cet établissement
        context["historique"] = (
            Classement.objects
            .filter(
                etablissement=classement.etablissement,
                is_published=True,
            )
            .exclude(pk=classement.pk)
            .order_by("-annee")[:5]
        )
        return context


class TopNationalView(TemplateView):
    """Page du top classement national."""
    template_name = "ranking/top_national.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        annee = self.request.GET.get("annee")

        qs = Classement.objects.filter(
            is_published=True,
            rang_national__isnull=False,
        ).select_related("etablissement")

        if annee:
            qs = qs.filter(annee=annee)
        else:
            derniere_annee = (
                qs.order_by("-annee").values_list("annee", flat=True).first()
            )
            if derniere_annee:
                qs = qs.filter(annee=derniere_annee)
                context["annee"] = derniere_annee

        context["top_classements"] = qs.order_by("rang_national")[:20]
        context["annees"] = (
            Classement.objects.filter(is_published=True)
            .values_list("annee", flat=True)
            .distinct()
            .order_by("-annee")
        )
        return context
