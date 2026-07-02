"""
Vues web pour l'application catalog.
"""
from django.db.models import Q
from django.views.generic import ListView, DetailView, TemplateView, View
from django.shortcuts import render

from .models import Domaine, Etablissement, Formation, Metier
from .services import CatalogService


class DomaineListView(ListView):
    """Liste de tous les domaines actifs."""
    model = Domaine
    template_name = "catalog/domaine_list.html"
    context_object_name = "domaines"

    def get_queryset(self):
        return Domaine.objects.filter(is_active=True).order_by("ordre", "nom")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = CatalogService.get_stats_globales()
        return context


class DomaineDetailView(DetailView):
    """Détail d'un domaine avec ses métiers et formations."""
    model = Domaine
    template_name = "catalog/domaine_detail.html"
    context_object_name = "domaine"
    slug_field = "slug"

    def get_queryset(self):
        return Domaine.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domaine = self.object
        context["metiers"] = domaine.metiers.filter(is_active=True).order_by(
            "-score_attractivite"
        )[:10]
        context["formations"] = domaine.formations.filter(is_active=True).order_by(
            "-score_qualite"
        )[:10]
        return context


class EtablissementListView(ListView):
    """Liste des établissements avec filtres."""
    model = Etablissement
    template_name = "catalog/etablissement_list.html"
    context_object_name = "etablissements"
    paginate_by = 20

    def get_queryset(self):
        qs = Etablissement.objects.filter(is_active=True).order_by("-score_qualite_global")

        # Filtres optionnels
        ville = self.request.GET.get("ville")
        if ville:
            qs = qs.filter(ville__iexact=ville)

        type_etab = self.request.GET.get("type")
        if type_etab:
            qs = qs.filter(type=type_etab)

        avec_bourses = self.request.GET.get("avec_bourses")
        if avec_bourses:
            qs = qs.filter(propose_bourses=True)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["villes"] = (
            Etablissement.objects.filter(is_active=True)
            .values_list("ville", flat=True)
            .distinct()
            .order_by("ville")
        )
        return context


class EtablissementDetailView(DetailView):
    """Détail d'un établissement."""
    model = Etablissement
    template_name = "catalog/etablissement_detail.html"
    context_object_name = "etablissement"
    slug_field = "slug"

    def get_queryset(self):
        return Etablissement.objects.filter(is_active=True).prefetch_related(
            "domaines_enseignes", "formations"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etab = self.object
        context["formations"] = etab.formations.filter(is_active=True).order_by(
            "-score_qualite"
        )
        return context


class FormationListView(ListView):
    """Liste des formations avec filtres."""
    model = Formation
    template_name = "catalog/formation_list.html"
    context_object_name = "formations"
    paginate_by = 20

    def get_queryset(self):
        qs = Formation.objects.filter(is_active=True).select_related(
            "etablissement", "domaine"
        ).order_by("-score_qualite")

        domaine = self.request.GET.get("domaine")
        if domaine:
            qs = qs.filter(domaine__slug=domaine)

        niveau = self.request.GET.get("niveau")
        if niveau:
            qs = qs.filter(niveau=niveau)

        cout_max = self.request.GET.get("cout_max")
        if cout_max:
            try:
                qs = qs.filter(cout_annuel__lte=int(cout_max))
            except ValueError:
                pass

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["domaines"] = Domaine.objects.filter(is_active=True).order_by("ordre", "nom")
        return context


class FormationDetailView(DetailView):
    """Détail d'une formation."""
    model = Formation
    template_name = "catalog/formation_detail.html"
    context_object_name = "formation"
    slug_field = "slug"

    def get_queryset(self):
        return Formation.objects.filter(is_active=True).select_related(
            "etablissement", "domaine"
        ).prefetch_related("debouches")


class MetierListView(ListView):
    """Liste des métiers avec filtres."""
    model = Metier
    template_name = "catalog/metier_list.html"
    context_object_name = "metiers"
    paginate_by = 20

    def get_queryset(self):
        qs = Metier.objects.filter(is_active=True).select_related("domaine").order_by(
            "-score_attractivite"
        )

        domaine = self.request.GET.get("domaine")
        if domaine:
            qs = qs.filter(domaine__slug=domaine)

        demande = self.request.GET.get("demande")
        if demande:
            qs = qs.filter(demande_marche=demande)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["domaines"] = Domaine.objects.filter(is_active=True).order_by("ordre", "nom")
        return context


class MetierDetailView(DetailView):
    """Détail d'un métier."""
    model = Metier
    template_name = "catalog/metier_detail.html"
    context_object_name = "metier"
    slug_field = "slug"

    def get_queryset(self):
        return Metier.objects.filter(is_active=True).select_related("domaine").prefetch_related(
            "formations_acces"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        metier = self.object
        context["formations_acces"] = metier.formations_acces.filter(
            is_active=True
        ).select_related("etablissement")[:10]
        return context


class ClassementView(TemplateView):
    """Page de classement des établissements et formations."""
    template_name = "catalog/classements.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["etablissements_top"] = Etablissement.objects.filter(
            is_active=True,
            is_verified=True,
            classement_national__isnull=False,
        ).order_by("classement_national")[:20]
        context["formations_top"] = Formation.objects.filter(
            is_active=True
        ).order_by("-score_qualite")[:20]
        return context


class ComparateurView(TemplateView):
    """Page de comparaison d'établissements ou de formations."""
    template_name = "catalog/comparateur.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["etablissements"] = Etablissement.objects.filter(
            is_active=True
        ).order_by("nom")
        context["formations"] = Formation.objects.filter(
            is_active=True
        ).select_related("etablissement").order_by("nom")
        return context


class SimulateurView(TemplateView):
    """Page du simulateur de coût de formation."""
    template_name = "catalog/simulateur.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formations"] = Formation.objects.filter(
            is_active=True
        ).select_related("etablissement").order_by("nom")
        return context


class RechercheView(View):
    """Recherche globale multi-entités."""
    template_name = "catalog/recherche.html"

    def get(self, request):
        q = request.GET.get("q", "").strip()
        ctx = {"q": q, "formations": [], "etablissements": [], "metiers": []}

        if len(q) >= 2:
            ctx["formations"] = (
                Formation.objects.filter(
                    Q(nom__icontains=q) | Q(description__icontains=q),
                    is_active=True,
                ).select_related("etablissement", "domaine").order_by("-score_qualite")[:8]
            )
            ctx["etablissements"] = (
                Etablissement.objects.filter(
                    Q(nom__icontains=q) | Q(description__icontains=q) | Q(ville__icontains=q),
                    is_active=True,
                ).order_by("-score_qualite_global")[:6]
            )
            ctx["metiers"] = (
                Metier.objects.filter(
                    Q(nom__icontains=q) | Q(description__icontains=q),
                    is_active=True,
                ).select_related("domaine").order_by("-score_attractivite")[:6]
            )
            ctx["nb_total"] = (
                len(ctx["formations"]) + len(ctx["etablissements"]) + len(ctx["metiers"])
            )
            # Community threads
            try:
                from apps.community.models import Thread
                ctx["threads"] = Thread.objects.filter(
                    Q(titre__icontains=q) | Q(contenu__icontains=q),
                ).exclude(statut="SUPPRIME").select_related("forum", "auteur").order_by("-created_at")[:4]
                ctx["nb_total"] += len(ctx["threads"])
            except Exception:
                ctx["threads"] = []
        return render(request, self.template_name, ctx)
