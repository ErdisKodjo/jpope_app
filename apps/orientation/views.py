"""
Vues web pour l'application orientation.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView

from apps.accounts.mixins import VerifiedAccountMixin, CounselorOrAdminMixin
from .models import (
    TestOrientation, ResultatTest, Recommandation, StatutTest,
    ReponseUtilisateur, DetailReponse, Question, Choice,
)
from .services.scoring_service import ScoringService

logger = logging.getLogger(__name__)


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


class TestListView(VerifiedAccountMixin, ListView):
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


class ResultatListView(VerifiedAccountMixin, ListView):
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


class ResultatDetailView(VerifiedAccountMixin, DetailView):
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


class RecommandationListView(VerifiedAccountMixin, ListView):
    """Liste des recommandations de l'utilisateur."""
    model = Recommandation
    template_name = "orientation/recommandation_list.html"
    context_object_name = "recommandations"

    def get_queryset(self):
        qs = Recommandation.objects.filter(
            etudiant=self.request.user,
        ).select_related("formation", "metier", "etablissement")

        plan = self.request.GET.get("plan")
        if plan:
            qs = qs.filter(plan=plan)

        return qs.order_by("plan", "ordre", "-taux_compatibilite")


class ResultatsConseillerView(CounselorOrAdminMixin, ListView):
    """Vue réservée aux conseillers et admins : tous les résultats étudiants."""
    model = ResultatTest
    template_name = "orientation/resultats_conseiller.html"
    context_object_name = "resultats"
    paginate_by = 25

    def get_queryset(self):
        qs = ResultatTest.objects.select_related(
            "reponse_utilisateur__etudiant",
            "reponse_utilisateur__test",
        ).order_by("-date_calcul")

        q = self.request.GET.get("q", "").strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(reponse_utilisateur__etudiant__email__icontains=q)
                | Q(reponse_utilisateur__etudiant__first_name__icontains=q)
                | Q(reponse_utilisateur__etudiant__last_name__icontains=q)
            )

        test_id = self.request.GET.get("test", "").strip()
        if test_id:
            qs = qs.filter(reponse_utilisateur__test__id=test_id)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tests"] = TestOrientation.objects.filter(is_active=True).order_by("nom")
        context["total_passations"] = ResultatTest.objects.count()
        context["q"] = self.request.GET.get("q", "")
        context["test_selectionne"] = self.request.GET.get("test", "")
        return context


class TakeTestView(VerifiedAccountMixin, DetailView):
    """Affiche les questions d'un test pour le faire passer."""
    model = TestOrientation
    template_name = "orientation/take_test.html"
    context_object_name = "test"
    slug_field = "slug"

    def get_queryset(self):
        return TestOrientation.objects.filter(is_active=True, is_public=True)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        test = self.object

        if not test.peut_etre_passe:
            messages.warning(request, "Ce test n'est pas disponible pour le moment.")
            return redirect("orientation:test-detail", slug=test.slug)

        # Créer ou reprendre une session EN_COURS
        session, created = ReponseUtilisateur.objects.get_or_create(
            etudiant=request.user,
            test=test,
            statut=StatutTest.EN_COURS,
            defaults={"nombre_questions_total": test.questions_actives.count()},
        )

        questions = test.questions_actives.prefetch_related("choices")
        ctx = self.get_context_data(
            object=self.object,
            session=session,
            questions=questions,
        )
        return self.render_to_response(ctx)


class SubmitTestView(VerifiedAccountMixin, View):
    """Traite la soumission des réponses d'un test."""

    def post(self, request, slug):
        test = get_object_or_404(TestOrientation, slug=slug, is_active=True, is_public=True)

        # Récupérer la session EN_COURS de cet utilisateur
        try:
            session = ReponseUtilisateur.objects.get(
                etudiant=request.user,
                test=test,
                statut=StatutTest.EN_COURS,
            )
        except ReponseUtilisateur.DoesNotExist:
            messages.error(request, "Aucune session de test active trouvée.")
            return redirect("orientation:test-detail", slug=slug)

        questions = test.questions_actives.prefetch_related("choices")
        nb_repondues = 0

        for question in questions:
            key = f"answer_{question.id}"
            raw = request.POST.get(key, "").strip()
            if not raw:
                continue

            detail_defaults = {}

            if question.type == "ECHELLE_LIKERT":
                try:
                    valeur = int(raw)
                    if question.echelle_min <= valeur <= question.echelle_max:
                        detail_defaults["valeur_echelle"] = valeur
                    else:
                        continue
                except ValueError:
                    continue

            elif question.type in ("CHOIX_UNIQUE", "SITUATIONNELLE"):
                try:
                    choice = question.choices.get(id=raw, is_active=True)
                    detail_defaults["choice_selectionne"] = choice
                except Choice.DoesNotExist:
                    continue

            elif question.type == "CHOIX_MULTIPLE":
                ids = request.POST.getlist(key)
                detail_defaults["choices_selectionnes"] = ids

            else:
                detail_defaults["reponse_ouverte"] = raw

            DetailReponse.objects.update_or_create(
                reponse_utilisateur=session,
                question=question,
                defaults=detail_defaults,
            )
            nb_repondues += 1

        # Marquer la session comme terminée
        session.statut = StatutTest.TERMINE
        session.date_fin = timezone.now()
        session.nombre_questions_repondues = nb_repondues
        session.progression = 100.0
        session.save(update_fields=[
            "statut", "date_fin", "nombre_questions_repondues", "progression"
        ])

        # Calculer le résultat
        try:
            resultat = ScoringService.calculer_resultat(str(session.id))
            messages.success(request, "Test terminé ! Voici vos résultats.")
            return redirect("orientation:resultat-detail", pk=resultat.pk)
        except Exception as exc:
            logger.exception("Erreur de scoring pour session %s", session.id)
            messages.error(request, "Une erreur est survenue lors du calcul. Réessayez.")
            return redirect("orientation:test-detail", slug=slug)

    def get(self, request, slug):
        return HttpResponseNotAllowed(["POST"])
