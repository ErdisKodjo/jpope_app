"""
Vues dashboard — tableau de bord étudiant + workflow évaluation conseiller.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView, DetailView, ListView, TemplateView, UpdateView,
)

from apps.accounts.mixins import (
    AdminRequiredMixin, CounselorRequiredMixin, VerifiedAccountMixin,
)
from .forms import AdminReviewForm, EvaluationConseillerForm
from .models import EvaluationConseiller, StatutEvaluation

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────
# TABLEAU DE BORD PRINCIPAL
# ──────────────────────────────────────────────────────────

class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_student:
            ctx["evaluation_validee"] = (
                EvaluationConseiller.objects
                .filter(etudiant=user, statut=StatutEvaluation.VALIDEE)
                .select_related("conseiller")
                .order_by("-date_traitement")
                .first()
            )

        elif user.is_counselor:
            qs = EvaluationConseiller.objects.filter(conseiller=user)
            ctx["nb_brouillons"] = qs.filter(statut=StatutEvaluation.BROUILLON).count()
            ctx["nb_soumises"]   = qs.filter(statut=StatutEvaluation.SOUMISE).count()
            ctx["nb_a_reviser"]  = qs.filter(statut=StatutEvaluation.REVISION_DEMANDEE).count()

        elif user.is_admin_role:
            ctx["nb_evaluations_en_attente"] = (
                EvaluationConseiller.objects
                .filter(statut=StatutEvaluation.SOUMISE)
                .count()
            )

        return ctx


# ──────────────────────────────────────────────────────────
# VUES CONSEILLER
# ──────────────────────────────────────────────────────────

class CounselorEvalListView(CounselorRequiredMixin, ListView):
    """Liste des fiches du conseiller connecté."""
    model = EvaluationConseiller
    template_name = "dashboard/conseiller_eval_list.html"
    context_object_name = "evaluations"
    paginate_by = 10

    def get_queryset(self):
        return (
            EvaluationConseiller.objects
            .filter(conseiller=self.request.user)
            .select_related("etudiant")
            .order_by("-updated_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx["nb_brouillons"] = qs.filter(statut=StatutEvaluation.BROUILLON).count()
        ctx["nb_soumises"]   = qs.filter(statut=StatutEvaluation.SOUMISE).count()
        ctx["nb_a_reviser"]  = qs.filter(statut=StatutEvaluation.REVISION_DEMANDEE).count()
        return ctx


class CounselorEvalCreateView(CounselorRequiredMixin, View):
    """Création d'une nouvelle fiche d'évaluation."""
    template_name = "dashboard/conseiller_eval_form.html"

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name, {
            "form": EvaluationConseillerForm(),
            "mode": "create",
        })

    def post(self, request):
        from django.shortcuts import render
        form = EvaluationConseillerForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.conseiller = request.user
            evaluation.save()
            messages.success(request, "Fiche créée et enregistrée en brouillon.")
            return redirect("dashboard:conseiller-eval-detail", pk=evaluation.pk)
        return render(request, self.template_name, {"form": form, "mode": "create"})


class CounselorEvalDetailView(CounselorRequiredMixin, View):
    """Détail / édition d'une fiche (si BROUILLON ou REVISION_DEMANDEE)."""
    template_name = "dashboard/conseiller_eval_detail.html"

    def _get_eval(self, request, pk):
        return get_object_or_404(
            EvaluationConseiller,
            pk=pk,
            conseiller=request.user,
        )

    def get(self, request, pk):
        from django.shortcuts import render
        evaluation = self._get_eval(request, pk)
        form = EvaluationConseillerForm(instance=evaluation) if evaluation.est_editable else None
        return render(request, self.template_name, {
            "evaluation": evaluation,
            "form": form,
        })

    def post(self, request, pk):
        from django.shortcuts import render
        evaluation = self._get_eval(request, pk)
        if not evaluation.est_editable:
            messages.error(request, "Cette fiche ne peut plus être modifiée.")
            return redirect("dashboard:conseiller-eval-detail", pk=pk)
        form = EvaluationConseillerForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            messages.success(request, "Fiche mise à jour.")
            return redirect("dashboard:conseiller-eval-detail", pk=pk)
        return render(request, self.template_name, {"evaluation": evaluation, "form": form})


class CounselorEvalSubmitView(CounselorRequiredMixin, View):
    """Soumet une fiche à l'admin (BROUILLON / REVISION → SOUMISE)."""

    def post(self, request, pk):
        evaluation = get_object_or_404(
            EvaluationConseiller, pk=pk, conseiller=request.user
        )
        if not evaluation.peut_etre_soumise:
            messages.error(request, "Cette fiche ne peut pas être soumise dans son état actuel.")
            return redirect("dashboard:conseiller-eval-detail", pk=pk)
        evaluation.statut = StatutEvaluation.SOUMISE
        evaluation.date_soumission = timezone.now()
        evaluation.save(update_fields=["statut", "date_soumission", "updated_at"])
        messages.success(request, "Fiche soumise à l'administration.")
        return redirect("dashboard:conseiller-eval-detail", pk=pk)

    def get(self, request, pk):
        return redirect("dashboard:conseiller-eval-detail", pk=pk)


# ──────────────────────────────────────────────────────────
# VUES ADMIN
# ──────────────────────────────────────────────────────────

class AdminEvalListView(AdminRequiredMixin, ListView):
    """Liste de toutes les fiches, filtrable par statut."""
    model = EvaluationConseiller
    template_name = "dashboard/admin_eval_list.html"
    context_object_name = "evaluations"
    paginate_by = 15

    def get_queryset(self):
        qs = (
            EvaluationConseiller.objects
            .select_related("conseiller", "etudiant", "traite_par")
            .order_by("-updated_at")
        )
        statut = self.request.GET.get("statut")
        if statut in StatutEvaluation.values:
            qs = qs.filter(statut=statut)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statut_filtre"] = self.request.GET.get("statut", "")
        ctx["statuts"] = StatutEvaluation.choices
        ctx["nb_soumises"] = EvaluationConseiller.objects.filter(
            statut=StatutEvaluation.SOUMISE
        ).count()
        return ctx


class AdminEvalReviewView(AdminRequiredMixin, View):
    """Valide, demande révision ou archive une fiche."""

    def post(self, request, pk):
        evaluation = get_object_or_404(EvaluationConseiller, pk=pk)
        form = AdminReviewForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Données invalides.")
            return redirect("dashboard:admin-eval-list")

        action    = form.cleaned_data["action"]
        note      = form.cleaned_data.get("note_admin", "")
        now       = timezone.now()

        mapping = {
            "valider":  StatutEvaluation.VALIDEE,
            "revision": StatutEvaluation.REVISION_DEMANDEE,
            "archiver": StatutEvaluation.ARCHIVEE,
        }
        nouveau_statut = mapping.get(action)
        if not nouveau_statut:
            messages.error(request, "Action non reconnue.")
            return redirect("dashboard:admin-eval-list")

        evaluation.statut          = nouveau_statut
        evaluation.note_admin      = note
        evaluation.traite_par      = request.user
        evaluation.date_traitement = now
        evaluation.save(update_fields=[
            "statut", "note_admin", "traite_par", "date_traitement", "updated_at"
        ])

        libelle = dict(StatutEvaluation.choices).get(nouveau_statut, nouveau_statut)
        messages.success(request, f"Fiche marquée : {libelle}.")
        return redirect("dashboard:admin-eval-list")

    def get(self, request, pk):
        return redirect("dashboard:admin-eval-list")
