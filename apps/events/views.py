from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, View
from django.contrib import messages

from .models import Evenement, InscriptionEvenement


class EvenementListView(ListView):
    model = Evenement
    template_name = "events/event_list.html"
    context_object_name = "evenements"
    paginate_by = 12

    def get_queryset(self):
        qs = Evenement.objects.filter(statut="PUBLIE").order_by("date_debut")
        q = self.request.GET.get("q", "").strip()
        type_filtre = self.request.GET.get("type", "").strip()
        if q:
            qs = qs.filter(Q(titre__icontains=q) | Q(description__icontains=q) | Q(lieu_nom__icontains=q))
        if type_filtre:
            qs = qs.filter(type=type_filtre)
        return qs


class EvenementDetailView(DetailView):
    model = Evenement
    template_name = "events/event_detail.html"
    context_object_name = "evenement"
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["user_inscrit"] = False
        if self.request.user.is_authenticated:
            ctx["user_inscrit"] = InscriptionEvenement.objects.filter(
                utilisateur=self.request.user,
                evenement=self.object,
            ).exclude(statut="ANNULE").exists()
        return ctx


class InscriptionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        evenement = get_object_or_404(Evenement, slug=slug)
        if evenement.est_complet:
            messages.error(request, "Cet événement est complet.")
            return redirect("events:event-detail", slug=slug)
        inscription, created = InscriptionEvenement.objects.get_or_create(
            utilisateur=request.user,
            evenement=evenement,
        )
        if created:
            Evenement.objects.filter(pk=evenement.pk).update(nombre_inscrits=F("nombre_inscrits") + 1)
            messages.success(request, "Inscription confirmée !")
        else:
            messages.info(request, "Vous êtes déjà inscrit à cet événement.")
        return redirect("events:event-detail", slug=slug)


class AnnulerInscriptionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        evenement = get_object_or_404(Evenement, slug=slug)
        try:
            inscription = InscriptionEvenement.objects.get(utilisateur=request.user, evenement=evenement)
            inscription.annuler()
            messages.success(request, "Inscription annulée.")
        except InscriptionEvenement.DoesNotExist:
            messages.error(request, "Inscription introuvable.")
        return redirect("events:event-detail", slug=slug)


class MesEvenementsView(LoginRequiredMixin, ListView):
    template_name = "events/mes_evenements.html"
    context_object_name = "inscriptions"
    paginate_by = 12

    def get_queryset(self):
        return (
            InscriptionEvenement.objects
            .filter(utilisateur=self.request.user)
            .exclude(statut="ANNULE")
            .select_related("evenement")
            .order_by("evenement__date_debut")
        )
