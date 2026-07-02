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
from .forms import AdminReviewForm, EvaluationConseillerForm, VoeuForm, VoeuStatutForm, DemarcheForm
from .models import (
    EvaluationConseiller, StatutEvaluation,
    Voeu, DemarcheInscription, Favori, StatutVoeu, StatutDemarche, TypeFavori,
)

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
            # Vœux
            voeux = Voeu.objects.filter(etudiant=user)
            ctx["voeux_recents"] = voeux.select_related("formation__etablissement").order_by("priorite")[:3]
            ctx["voeux_count"] = voeux.count()
            ctx["favoris_count"] = Favori.objects.filter(utilisateur=user).count()
            # Démarches urgentes (dans les 14 prochains jours)
            ctx["demarches_urgentes"] = DemarcheInscription.objects.filter(
                etudiant=user,
                statut__in=[StatutDemarche.A_FAIRE, StatutDemarche.EN_COURS],
                date_echeance__isnull=False,
                date_echeance__gte=timezone.now(),
                date_echeance__lte=timezone.now() + timezone.timedelta(days=14),
            ).order_by("date_echeance")[:5]
            ctx["demarches_count"] = DemarcheInscription.objects.filter(
                etudiant=user,
                statut__in=[StatutDemarche.A_FAIRE, StatutDemarche.EN_COURS],
            ).count()
            ctx["demarches_retard"] = DemarcheInscription.objects.filter(
                etudiant=user,
                statut__in=[StatutDemarche.A_FAIRE, StatutDemarche.EN_COURS],
                date_echeance__lt=timezone.now(),
            ).count()
            # Dernier résultat de test
            try:
                from apps.orientation.models import ResultatTest, Recommandation
                ctx["dernier_resultat"] = ResultatTest.objects.filter(
                    reponse_utilisateur__etudiant=user
                ).select_related("reponse_utilisateur__test").order_by("-created_at").first()
                ctx["top_recommandations"] = Recommandation.objects.filter(
                    etudiant=user
                ).order_by("-taux_compatibilite")[:3]
            except Exception:
                pass
            # Accompagnement actif
            try:
                from apps.orientation.models import DemandeAccompagnement
                ctx["accompagnement_actif"] = DemandeAccompagnement.objects.filter(
                    etudiant=user,
                    statut__in=["ACCEPTEE", "EN_COURS"],
                ).select_related("conseiller").first()
            except Exception:
                pass
            # Notifications non lues
            try:
                from apps.notifications.models import Notification
                ctx["nb_notifs_non_lues"] = Notification.objects.filter(user=user, is_read=False).count()
                ctx["notifs_recentes"] = Notification.objects.filter(user=user).order_by("-created_at")[:5]
            except Exception:
                pass

        elif user.is_counselor:
            qs = EvaluationConseiller.objects.filter(conseiller=user)
            ctx["nb_brouillons"] = qs.filter(statut=StatutEvaluation.BROUILLON).count()
            ctx["nb_soumises"]   = qs.filter(statut=StatutEvaluation.SOUMISE).count()
            ctx["nb_a_reviser"]  = qs.filter(statut=StatutEvaluation.REVISION_DEMANDEE).count()
            try:
                from apps.orientation.models import DemandeAccompagnement, StatutDemande
                ctx["demandes_actives"] = DemandeAccompagnement.objects.filter(
                    conseiller=user, statut__in=["ACCEPTEE", "EN_COURS"]
                ).select_related("etudiant").count()
                ctx["demandes_en_attente"] = DemandeAccompagnement.objects.filter(
                    conseiller__isnull=True, statut="EN_ATTENTE"
                ).count()
            except Exception:
                pass

        elif user.is_admin_role:
            ctx["nb_evaluations_en_attente"] = (
                EvaluationConseiller.objects
                .filter(statut=StatutEvaluation.SOUMISE)
                .count()
            )
            try:
                from apps.orientation.models import QuestionProposee, StatutQuestionProposee
                ctx["nb_questions_en_attente"] = QuestionProposee.objects.filter(
                    statut=StatutQuestionProposee.EN_ATTENTE
                ).count()
            except Exception:
                pass
            try:
                from apps.payments.models import RistourneConseiller
                ctx["nb_ristournes_en_attente"] = RistourneConseiller.objects.filter(statut="EN_ATTENTE").count()
            except Exception:
                pass

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


# ──────────────────────────────────────────────────────────
# PHASE 3 — VOEUX
# ──────────────────────────────────────────────────────────

class MesVoeuxView(LoginRequiredMixin, ListView):
    template_name = "dashboard/mes_voeux.html"
    context_object_name = "voeux"

    def get_queryset(self):
        return Voeu.objects.filter(
            etudiant=self.request.user
        ).select_related("formation__etablissement", "formation__domaine").order_by("priorite")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuts"] = StatutVoeu.choices
        ctx["nb_actifs"] = Voeu.objects.filter(
            etudiant=self.request.user,
            statut__in=[StatutVoeu.BROUILLON, StatutVoeu.SOUMIS, StatutVoeu.EN_ATTENTE],
        ).count()
        return ctx


class VoeuCreateView(LoginRequiredMixin, CreateView):
    model = Voeu
    form_class = VoeuForm
    template_name = "dashboard/voeu_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        # Pre-fill formation from URL param
        formation_id = request.GET.get("formation") or kwargs.get("formation_pk")
        self._formation = None
        if formation_id:
            from apps.catalog.models import Formation
            try:
                self._formation = Formation.objects.get(pk=formation_id)
                # Check unique constraint
                if Voeu.objects.filter(etudiant=request.user, formation=self._formation).exists():
                    messages.info(request, "Cette formation est déjà dans vos vœux.")
                    return redirect("dashboard:mes-voeux")
            except Formation.DoesNotExist:
                pass
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formation"] = self._formation
        if not self._formation:
            from apps.catalog.models import Formation
            ctx["formations"] = Formation.objects.select_related("etablissement").order_by("nom")[:100]
        ctx["mode"] = "create"
        return ctx

    def form_valid(self, form):
        voeu = form.save(commit=False)
        voeu.etudiant = self.request.user
        if self._formation:
            voeu.formation = self._formation
        else:
            formation_id = self.request.POST.get("formation_id")
            if not formation_id:
                form.add_error(None, "Veuillez sélectionner une formation.")
                return self.form_invalid(form)
            from apps.catalog.models import Formation
            try:
                voeu.formation = Formation.objects.get(pk=formation_id)
            except Formation.DoesNotExist:
                form.add_error(None, "Formation introuvable.")
                return self.form_invalid(form)
        voeu.save()
        messages.success(self.request, f"« {voeu.formation.nom} » ajouté à vos vœux.")
        return redirect("dashboard:mes-voeux")


class VoeuUpdateView(LoginRequiredMixin, UpdateView):
    model = Voeu
    form_class = VoeuForm
    template_name = "dashboard/voeu_form.html"

    def get_object(self):
        return get_object_or_404(Voeu, pk=self.kwargs["pk"], etudiant=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formation"] = self.object.formation
        ctx["mode"] = "edit"
        ctx["statut_form"] = VoeuStatutForm(instance=self.object)
        return ctx

    def form_valid(self, form):
        voeu = form.save()
        messages.success(self.request, "Vœu mis à jour.")
        return redirect("dashboard:mes-voeux")


class VoeuUpdateStatutView(LoginRequiredMixin, View):
    def post(self, request, pk):
        voeu = get_object_or_404(Voeu, pk=pk, etudiant=request.user)
        form = VoeuStatutForm(request.POST, instance=voeu)
        if form.is_valid():
            form.save()
            messages.success(request, "Statut du vœu mis à jour.")
        return redirect("dashboard:mes-voeux")

    def get(self, request, pk):
        return redirect("dashboard:mes-voeux")


class VoeuDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        voeu = get_object_or_404(Voeu, pk=pk, etudiant=request.user)
        if voeu.statut != StatutVoeu.BROUILLON:
            messages.error(request, "Seuls les vœux en brouillon peuvent être supprimés.")
            return redirect("dashboard:mes-voeux")
        nom = voeu.formation.nom
        voeu.delete()
        messages.success(request, f"Vœu pour « {nom} » supprimé.")
        return redirect("dashboard:mes-voeux")

    def get(self, request, pk):
        return redirect("dashboard:mes-voeux")


# ──────────────────────────────────────────────────────────
# PHASE 3 — DEMARCHES
# ──────────────────────────────────────────────────────────

class MesDemarchesView(LoginRequiredMixin, ListView):
    template_name = "dashboard/mes_demarches.html"
    context_object_name = "demarches"
    paginate_by = 20

    def get_queryset(self):
        qs = DemarcheInscription.objects.filter(
            etudiant=self.request.user
        ).select_related("voeu__formation", "formation")
        statut = self.request.GET.get("statut")
        if statut:
            qs = qs.filter(statut=statut)
        return qs.order_by("date_echeance", "-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuts"] = StatutDemarche.choices
        ctx["statut_filtre"] = self.request.GET.get("statut", "")
        ctx["nb_retard"] = DemarcheInscription.objects.filter(
            etudiant=self.request.user,
            statut__in=[StatutDemarche.A_FAIRE, StatutDemarche.EN_COURS],
            date_echeance__lt=timezone.now(),
        ).count()
        return ctx


class DemarcheCreateView(LoginRequiredMixin, CreateView):
    model = DemarcheInscription
    form_class = DemarcheForm
    template_name = "dashboard/demarche_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        voeu_pk = self.request.GET.get("voeu") or self.kwargs.get("voeu_pk")
        ctx["voeu"] = get_object_or_404(Voeu, pk=voeu_pk, etudiant=self.request.user) if voeu_pk else None
        ctx["mode"] = "create"
        return ctx

    def form_valid(self, form):
        demarche = form.save(commit=False)
        demarche.etudiant = self.request.user
        voeu_pk = self.request.POST.get("voeu_pk")
        if voeu_pk:
            try:
                demarche.voeu = Voeu.objects.get(pk=voeu_pk, etudiant=self.request.user)
                demarche.formation = demarche.voeu.formation
            except Voeu.DoesNotExist:
                pass
        demarche.save()
        messages.success(self.request, "Démarche créée.")
        return redirect("dashboard:mes-demarches")


class DemarcheUpdateView(LoginRequiredMixin, UpdateView):
    model = DemarcheInscription
    form_class = DemarcheForm
    template_name = "dashboard/demarche_form.html"

    def get_object(self):
        return get_object_or_404(DemarcheInscription, pk=self.kwargs["pk"], etudiant=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "edit"
        return ctx

    def form_valid(self, form):
        demarche = form.save()
        if demarche.statut == StatutDemarche.COMPLETEE and not demarche.date_realisation:
            demarche.date_realisation = timezone.now()
            demarche.save(update_fields=["date_realisation"])
        messages.success(self.request, "Démarche mise à jour.")
        return redirect("dashboard:mes-demarches")


# ──────────────────────────────────────────────────────────
# PHASE 3 — FAVORIS
# ──────────────────────────────────────────────────────────

class MesFavorisView(LoginRequiredMixin, ListView):
    template_name = "dashboard/mes_favoris.html"
    context_object_name = "favoris"

    def get_queryset(self):
        qs = Favori.objects.filter(utilisateur=self.request.user).select_related(
            "formation__etablissement", "metier", "etablissement", "evenement"
        )
        type_filtre = self.request.GET.get("type")
        if type_filtre:
            qs = qs.filter(type_entite=type_filtre)
        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["type_filtre"] = self.request.GET.get("type", "")
        ctx["types"] = TypeFavori.choices
        ctx["counts"] = {
            t: Favori.objects.filter(utilisateur=self.request.user, type_entite=t).count()
            for t, _ in TypeFavori.choices
        }
        return ctx


class ToggleFavoriView(LoginRequiredMixin, View):
    """Ajoute ou retire un élément des favoris (POST idempotent)."""

    def post(self, request, type_entite, pk):
        user = request.user
        field_map = {
            "FORMATION": ("formation", "catalog.Formation"),
            "METIER": ("metier", "catalog.Metier"),
            "ETABLISSEMENT": ("etablissement", "catalog.Etablissement"),
        }
        if type_entite not in field_map:
            messages.error(request, "Type de favori non reconnu.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        field_name, model_path = field_map[type_entite]
        app_label, model_name = model_path.split(".")
        from django.apps import apps
        try:
            Model = apps.get_model(app_label, model_name)
            entity = get_object_or_404(Model, pk=pk)
        except Exception:
            messages.error(request, "Élément introuvable.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        existing = Favori.objects.filter(utilisateur=user, type_entite=type_entite, **{field_name: entity}).first()
        if existing:
            existing.delete()
            messages.info(request, "Retiré de vos favoris.")
        else:
            Favori.objects.create(utilisateur=user, type_entite=type_entite, **{field_name: entity})
            messages.success(request, "Ajouté à vos favoris.")

        return redirect(request.META.get("HTTP_REFERER", "/"))

    def get(self, request, type_entite, pk):
        return redirect("dashboard:mes-favoris")
