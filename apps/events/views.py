from django.contrib.auth.mixins import LoginRequiredMixin
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
        return Evenement.objects.filter(statut="PUBLIE").order_by("date_debut")


class EvenementDetailView(DetailView):
    model = Evenement
    template_name = "events/event_detail.html"
    context_object_name = "evenement"
    slug_field = "slug"


class InscriptionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        evenement = get_object_or_404(Evenement, slug=slug)
        InscriptionEvenement.objects.get_or_create(
            utilisateur=request.user,
            evenement=evenement,
        )
        messages.success(request, "Inscription confirmée !")
        return redirect("events:event-detail", slug=slug)
