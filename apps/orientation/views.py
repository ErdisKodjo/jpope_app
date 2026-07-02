"""
Vues web pour l'application orientation.
"""
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView

from apps.accounts.mixins import VerifiedAccountMixin, CounselorOrAdminMixin, CounselorRequiredMixin, AdminRequiredMixin
from .models import (
    TestOrientation, ResultatTest, Recommandation, StatutTest,
    ReponseUtilisateur, DetailReponse, Question, Choice,
    DemandeAccompagnement, MessageAccompagnement, QuestionProposee,
    StatutDemande, StatutQuestionProposee,
)
from .forms import (
    DemandeAccompagnementForm, MessageAccompagnementForm,
    AccepterDemandeForm, RefuserDemandeForm, EvaluerConseillerForm,
    QuestionProposeeForm, RejeterQuestionForm,
)
from .services.scoring_service import ScoringService

logger = logging.getLogger(__name__)


def _notify(user, titre, message, type_notif="INFO", action_url=""):
    """Wrapper silencieux pour les notifications in-app."""
    try:
        from apps.notifications.utils import notify
        notify(user=user, titre=titre, message=message, type_notif=type_notif, action_url=action_url)
    except Exception:
        pass


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


# ─────────────────────────────────────────────────────────────────
# PHASE 2 — ACCOMPAGNEMENT CONSEILLER
# ─────────────────────────────────────────────────────────────────

class DemandeAccompagnementCreateView(VerifiedAccountMixin, FormView):
    """Étudiant crée une demande d'accompagnement."""
    template_name = "orientation/accompagnement_create.html"
    form_class = DemandeAccompagnementForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_student:
            messages.error(request, _("Seuls les étudiants peuvent demander un accompagnement."))
            return redirect("orientation:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        resultat_pk = self.kwargs.get("resultat_pk")
        if resultat_pk:
            ctx["resultat"] = get_object_or_404(
                ResultatTest,
                pk=resultat_pk,
                reponse_utilisateur__etudiant=self.request.user,
            )
        # Conseillers disponibles
        from django.contrib.auth import get_user_model
        User = get_user_model()
        ctx["conseillers_disponibles"] = User.objects.filter(
            role="COUNSELOR",
            counselor_profile__is_available=True,
        ).select_related("counselor_profile").order_by("-counselor_profile__note_moyenne")[:10]
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        demande = form.save(commit=False)
        demande.etudiant = self.request.user

        # Conseiller choisi (optionnel via POST)
        conseiller_id = self.request.POST.get("conseiller_id")
        if conseiller_id:
            try:
                demande.conseiller = User.objects.get(pk=conseiller_id, role="COUNSELOR")
            except User.DoesNotExist:
                pass

        # Résultat associé (si depuis un résultat)
        resultat_pk = self.kwargs.get("resultat_pk")
        if resultat_pk:
            try:
                demande.resultat_test = ResultatTest.objects.get(
                    pk=resultat_pk,
                    reponse_utilisateur__etudiant=self.request.user,
                )
            except ResultatTest.DoesNotExist:
                pass

        demande.save()
        messages.success(self.request, _("Votre demande d'accompagnement a été envoyée. Un conseiller vous répondra bientôt."))
        return redirect("orientation:mes-demandes")


class MesDemandesEtudiantView(VerifiedAccountMixin, ListView):
    """Liste des demandes d'accompagnement de l'étudiant."""
    template_name = "orientation/mes_demandes_etudiant.html"
    context_object_name = "demandes"

    def get_queryset(self):
        return DemandeAccompagnement.objects.filter(
            etudiant=self.request.user,
        ).select_related("conseiller", "resultat_test").order_by("-date_demande")


class DemandeDetailView(VerifiedAccountMixin, DetailView):
    """Détail d'une demande d'accompagnement avec fil de messagerie."""
    template_name = "orientation/demande_detail.html"
    context_object_name = "demande"

    def get_object(self):
        demande = get_object_or_404(DemandeAccompagnement, pk=self.kwargs["pk"])
        user = self.request.user
        if demande.etudiant != user and demande.conseiller != user and not user.is_staff:
            raise PermissionDenied
        return demande

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["messages_fil"] = self.object.messages.select_related("auteur").order_by("created_at")
        ctx["form_message"] = MessageAccompagnementForm()
        ctx["form_evaluer"] = EvaluerConseillerForm()
        from .models.rdv import RendezVous
        ctx["rendez_vous_actifs"] = (
            self.object.rendez_vous.exclude(statut="ANNULE").order_by("date_rdv")
            if hasattr(self.object, "rendez_vous") else []
        )
        # Marquer les messages non lus comme lus
        self.object.messages.exclude(auteur=self.request.user).filter(est_lu=False).update(est_lu=True)
        return ctx


class EnvoyerMessageView(VerifiedAccountMixin, View):
    """Envoie un message dans une session d'accompagnement."""

    def post(self, request, pk):
        demande = get_object_or_404(DemandeAccompagnement, pk=pk)
        user = request.user
        if demande.etudiant != user and demande.conseiller != user:
            raise PermissionDenied
        if demande.statut not in (StatutDemande.ACCEPTEE, StatutDemande.EN_COURS):
            messages.error(request, _("La session n'est pas active."))
            return redirect("orientation:demande-detail", pk=pk)

        form = MessageAccompagnementForm(request.POST)
        if form.is_valid():
            MessageAccompagnement.objects.create(
                demande=demande,
                auteur=user,
                contenu=form.cleaned_data["contenu"],
            )
            if demande.statut == StatutDemande.ACCEPTEE:
                demande.statut = StatutDemande.EN_COURS
                demande.date_debut = timezone.now()
                demande.save(update_fields=["statut", "date_debut"])
            recipient = demande.conseiller if user == demande.etudiant else demande.etudiant
            if recipient:
                _notify(
                    recipient,
                    titre="Nouveau message",
                    message=f"{user.get_full_name()} vous a envoyé un message.",
                    type_notif="NOUV_MESSAGE",
                    action_url=f"/orientation/accompagnement/{pk}/",
                )
        return redirect("orientation:demande-detail", pk=pk)

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


class EvaluerConseillerView(VerifiedAccountMixin, View):
    """L'étudiant évalue le conseiller et clôture la demande."""

    def post(self, request, pk):
        demande = get_object_or_404(DemandeAccompagnement, pk=pk, etudiant=request.user)
        if demande.statut not in (StatutDemande.EN_COURS, StatutDemande.ACCEPTEE):
            messages.error(request, _("Cette demande ne peut pas être évaluée."))
            return redirect("orientation:demande-detail", pk=pk)

        form = EvaluerConseillerForm(request.POST)
        if not form.is_valid():
            messages.error(request, _("Données invalides."))
            return redirect("orientation:demande-detail", pk=pk)

        note = form.cleaned_data["note"]
        commentaire = form.cleaned_data.get("commentaire", "")

        demande.note_conseiller = note
        demande.commentaire_note = commentaire
        demande.statut = StatutDemande.TERMINEE
        demande.date_fin = timezone.now()
        demande.save(update_fields=["note_conseiller", "commentaire_note", "statut", "date_fin"])

        # Mettre à jour la note du conseiller
        self._mettre_a_jour_note_conseiller(demande.conseiller, note)

        # Générer la ristourne
        self._generer_ristourne(demande, note)

        if demande.conseiller:
            _notify(
                demande.conseiller,
                titre="Évaluation reçue",
                message=f"{request.user.get_full_name()} vous a évalué {note}/5.",
                type_notif="SUCCESS",
                action_url="/orientation/conseiller/demandes/",
            )
        messages.success(request, _("Merci pour votre évaluation ! La session est maintenant clôturée."))
        return redirect("orientation:mes-demandes")

    def _mettre_a_jour_note_conseiller(self, conseiller, nouvelle_note):
        try:
            profile = conseiller.counselor_profile
            n = profile.nombre_evaluations
            # Moyenne glissante
            profile.note_moyenne = round(((profile.note_moyenne * n) + nouvelle_note) / (n + 1), 2)
            profile.nombre_evaluations = n + 1
            profile.nombre_accompagnements_total += 1
            if profile.nombre_accompagnements_actifs > 0:
                profile.nombre_accompagnements_actifs -= 1
            profile.save(update_fields=["note_moyenne", "nombre_evaluations", "nombre_accompagnements_total", "nombre_accompagnements_actifs"])
        except Exception:
            pass

    def _generer_ristourne(self, demande, note):
        if not demande.conseiller or demande.ristourne_generee:
            return
        try:
            from payments.models import RistourneConseiller
        except ImportError:
            try:
                from apps.payments.models import RistourneConseiller
            except ImportError:
                return
        try:
            profile = demande.conseiller.counselor_profile
            tarif = float(profile.tarif_consultation or 0)
            taux = profile.taux_ristourne / 100
            montant = round(tarif * taux)
            if montant <= 0:
                return
            RistourneConseiller.objects.create(
                conseiller=demande.conseiller,
                demande_accompagnement=demande,
                montant=montant,
                taux_applique=profile.taux_ristourne,
                note_etudiant=note,
            )
            profile.solde_ristournes = float(profile.solde_ristournes or 0) + montant
            profile.save(update_fields=["solde_ristournes"])
            demande.ristourne_generee = True
            demande.save(update_fields=["ristourne_generee"])
        except Exception as exc:
            logger.warning("Erreur génération ristourne: %s", exc)

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


# ─────────────────────────────────────────────────────────────────
# PHASE 2 — VUES CONSEILLERS
# ─────────────────────────────────────────────────────────────────

class DemandesConseillerView(CounselorRequiredMixin, ListView):
    """Tableau de bord des demandes d'accompagnement du conseiller."""
    template_name = "orientation/conseiller_demandes.html"
    context_object_name = "demandes"

    def get_queryset(self):
        statut = self.request.GET.get("statut", "")
        qs = DemandeAccompagnement.objects.filter(
            conseiller=self.request.user,
        ).select_related("etudiant", "resultat_test").order_by("-date_demande")
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["en_attente"] = DemandeAccompagnement.objects.filter(
            conseiller__isnull=True, statut=StatutDemande.EN_ATTENTE
        ).select_related("etudiant").order_by("-date_demande")[:5]
        ctx["statut_filtre"] = self.request.GET.get("statut", "")
        ctx["statuts"] = StatutDemande.choices
        ctx["form_accepter"] = AccepterDemandeForm()
        ctx["form_refuser"] = RefuserDemandeForm()
        return ctx


class AccepterDemandeView(CounselorRequiredMixin, View):
    """Le conseiller accepte une demande d'accompagnement."""

    def post(self, request, pk):
        demande = get_object_or_404(DemandeAccompagnement, pk=pk, statut=StatutDemande.EN_ATTENTE)
        form = AccepterDemandeForm(request.POST)
        if form.is_valid():
            demande.conseiller = request.user
            demande.statut = StatutDemande.ACCEPTEE
            demande.message_reponse = form.cleaned_data.get("message_reponse", "")
            demande.date_reponse = timezone.now()
            demande.save(update_fields=["conseiller", "statut", "message_reponse", "date_reponse"])

            try:
                profile = request.user.counselor_profile
                profile.nombre_accompagnements_actifs += 1
                profile.save(update_fields=["nombre_accompagnements_actifs"])
            except Exception:
                pass

            _notify(
                demande.etudiant,
                titre="Votre demande a été acceptée",
                message=f"{request.user.get_full_name()} a accepté votre demande d'accompagnement.",
                type_notif="SUCCESS",
                action_url=f"/orientation/accompagnement/{pk}/",
            )
            messages.success(request, _("Demande acceptée. Vous pouvez maintenant échanger avec l'étudiant."))
        return redirect("orientation:demande-detail", pk=pk)

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


class RefuserDemandeView(CounselorRequiredMixin, View):
    """Le conseiller refuse une demande d'accompagnement."""

    def post(self, request, pk):
        demande = get_object_or_404(DemandeAccompagnement, pk=pk, statut=StatutDemande.EN_ATTENTE)
        form = RefuserDemandeForm(request.POST)
        if form.is_valid():
            demande.conseiller = request.user
            demande.statut = StatutDemande.REFUSEE
            demande.message_reponse = form.cleaned_data["message_reponse"]
            demande.date_reponse = timezone.now()
            demande.save(update_fields=["conseiller", "statut", "message_reponse", "date_reponse"])
            _notify(
                demande.etudiant,
                titre="Demande d'accompagnement refusée",
                message="Votre demande n'a pas pu être prise en charge. Vous pouvez en soumettre une nouvelle.",
                type_notif="WARNING",
                action_url="/orientation/accompagnement/mes-demandes/",
            )
            messages.info(request, _("Demande refusée."))
        return redirect("orientation:conseiller-demandes")

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


class QuestionProposerView(CounselorRequiredMixin, FormView):
    """Le conseiller propose une nouvelle question pour un test."""
    template_name = "orientation/question_proposer.html"
    form_class = QuestionProposeeForm

    def form_valid(self, form):
        question = form.save(commit=False)
        question.conseiller = self.request.user
        question.save()
        messages.success(self.request, _("Votre question a été soumise et sera examinée par l'équipe."))
        return redirect("orientation:mes-questions-proposees")

    def get_success_url(self):
        return ""


class MesQuestionsProposees(CounselorRequiredMixin, ListView):
    """Liste des questions proposées par le conseiller connecté."""
    template_name = "orientation/mes_questions.html"
    context_object_name = "questions"

    def get_queryset(self):
        return QuestionProposee.objects.filter(
            conseiller=self.request.user,
        ).select_related("test_cible", "question_creee").order_by("-date_soumission")


# ─────────────────────────────────────────────────────────────────
# PHASE 2 — VUES ADMIN
# ─────────────────────────────────────────────────────────────────

class AdminQuestionsProposees(AdminRequiredMixin, ListView):
    """Admin : liste toutes les questions proposées avec filtrage par statut."""
    template_name = "orientation/admin_questions.html"
    context_object_name = "questions"
    paginate_by = 20

    def get_queryset(self):
        statut = self.request.GET.get("statut", StatutQuestionProposee.EN_ATTENTE)
        qs = QuestionProposee.objects.select_related(
            "conseiller", "test_cible", "traite_par"
        ).order_by("-date_soumission")
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statut_filtre"] = self.request.GET.get("statut", StatutQuestionProposee.EN_ATTENTE)
        ctx["statuts"] = StatutQuestionProposee.choices
        ctx["total_en_attente"] = QuestionProposee.objects.filter(statut=StatutQuestionProposee.EN_ATTENTE).count()
        ctx["form_rejeter"] = RejeterQuestionForm()
        return ctx


class AdminApprouverQuestion(AdminRequiredMixin, View):
    """Admin approuve une question proposée et la crée dans le test cible."""

    def post(self, request, pk):
        proposition = get_object_or_404(QuestionProposee, pk=pk, statut=StatutQuestionProposee.EN_ATTENTE)

        test_cible = proposition.test_cible
        if not test_cible:
            test_cible = TestOrientation.objects.filter(is_active=True).first()

        if not test_cible:
            messages.error(request, _("Aucun test disponible pour intégrer la question."))
            return redirect("orientation:admin-questions-proposees")

        # Créer la Question réelle
        ordre_max = test_cible.questions.aggregate(m=models_max("ordre"))["m"] or 0
        nouvelle_question = Question.objects.create(
            test=test_cible,
            texte=proposition.texte,
            explication=proposition.explication,
            type=proposition.type,
            dimensions=proposition.dimensions,
            poids=proposition.poids,
            contexte=proposition.contexte_situation,
            ordre=ordre_max + 1,
        )

        proposition.statut = StatutQuestionProposee.APPROUVEE
        proposition.question_creee = nouvelle_question
        proposition.traite_par = request.user
        proposition.date_traitement = timezone.now()
        proposition.save(update_fields=["statut", "question_creee", "traite_par", "date_traitement"])

        _notify(
            proposition.conseiller,
            titre="Votre question a été approuvée",
            message=f"Votre question a été intégrée dans le test « {test_cible.nom} ».",
            type_notif="SUCCESS",
            action_url="/orientation/conseiller/questions/",
        )
        messages.success(request, _(
            f"Question approuvée et ajoutée au test « {test_cible.nom} » (ordre {ordre_max + 1})."
        ))
        return redirect("orientation:admin-questions-proposees")

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


class AdminRejeterQuestion(AdminRequiredMixin, View):
    """Admin rejette une question proposée."""

    def post(self, request, pk):
        proposition = get_object_or_404(QuestionProposee, pk=pk, statut=StatutQuestionProposee.EN_ATTENTE)
        form = RejeterQuestionForm(request.POST)
        if form.is_valid():
            proposition.statut = StatutQuestionProposee.REJETEE
            proposition.motif_rejet = form.cleaned_data["motif_rejet"]
            proposition.traite_par = request.user
            proposition.date_traitement = timezone.now()
            proposition.save(update_fields=["statut", "motif_rejet", "traite_par", "date_traitement"])
            _notify(
                proposition.conseiller,
                titre="Votre question a été rejetée",
                message="Votre proposition de question n'a pas été retenue.",
                type_notif="WARNING",
                action_url="/orientation/conseiller/questions/",
            )
            messages.info(request, _("Question rejetée."))
        return redirect("orientation:admin-questions-proposees")

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


class AdminRistournesView(AdminRequiredMixin, ListView):
    """Admin : liste et gestion des ristournes des conseillers."""
    template_name = "orientation/admin_ristournes.html"
    context_object_name = "ristournes"
    paginate_by = 30

    def get_queryset(self):
        try:
            from apps.payments.models import RistourneConseiller
        except ImportError:
            from payments.models import RistourneConseiller
        statut = self.request.GET.get("statut", "EN_ATTENTE")
        qs = RistourneConseiller.objects.select_related(
            "conseiller", "demande_accompagnement__etudiant"
        ).order_by("-date_creation")
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            from apps.payments.models import RistourneConseiller, StatutRistourne
        except ImportError:
            from payments.models import RistourneConseiller, StatutRistourne
        ctx["statut_filtre"] = self.request.GET.get("statut", "EN_ATTENTE")
        ctx["total_en_attente"] = RistourneConseiller.objects.filter(statut="EN_ATTENTE").count()
        from django.db.models import Sum
        ctx["montant_en_attente"] = RistourneConseiller.objects.filter(statut="EN_ATTENTE").aggregate(
            total=Sum("montant")
        )["total"] or 0
        return ctx


class AdminPayerRistourneView(AdminRequiredMixin, View):
    """Admin marque une ristourne comme payée."""

    def post(self, request, pk):
        try:
            from apps.payments.models import RistourneConseiller
        except ImportError:
            from payments.models import RistourneConseiller

        ristourne = get_object_or_404(RistourneConseiller, pk=pk, statut="EN_ATTENTE")
        ristourne.statut = "PAYEE"
        ristourne.date_paiement = timezone.now()
        ristourne.save(update_fields=["statut", "date_paiement"])

        # Déduire du solde du conseiller
        try:
            profile = ristourne.conseiller.counselor_profile
            profile.solde_ristournes = max(0, float(profile.solde_ristournes) - float(ristourne.montant))
            profile.save(update_fields=["solde_ristournes"])
        except Exception:
            pass

        _notify(
            ristourne.conseiller,
            titre="Ristourne payée",
            message=f"Votre ristourne {ristourne.reference} de {ristourne.montant:,.0f} FCFA a été payée.",
            type_notif="SUCCESS",
            action_url="/orientation/conseiller/demandes/",
        )
        messages.success(request, _(f"Ristourne {ristourne.reference} marquée comme payée."))
        return redirect("orientation:admin-ristournes")

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


def models_max(field):
    from django.db.models import Max
    return Max(field)


# ─────────────────────────────────────────────────────────────────
# PERSPECTIVES COURT TERME — CONSEILLERS & RENDEZ-VOUS
# ─────────────────────────────────────────────────────────────────

from django.shortcuts import render
from django.db.models import Q


class ListeConseillersView(View):
    """Page publique listant les conseillers disponibles."""
    template_name = "orientation/conseillers.html"

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        qs = User.objects.filter(
            role="COUNSELOR",
            statut_compte="VERIFIE",
            counselor_profile__is_available=True,
        ).select_related("counselor_profile").order_by("-counselor_profile__note_moyenne")

        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(counselor_profile__qualifications__icontains=q)
            )

        return render(request, self.template_name, {"conseillers": qs, "q": q})


class ConseillerDetailPublicView(View):
    """Profil public d'un conseiller avec ses évaluations et le formulaire de demande."""
    template_name = "orientation/conseiller_detail.html"

    def get(self, request, pk):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        conseiller = get_object_or_404(User, pk=pk, role="COUNSELOR")
        evaluations = DemandeAccompagnement.objects.filter(
            conseiller=conseiller,
            statut="TERMINEE",
            note_conseiller__isnull=False,
        ).select_related("etudiant").order_by("-date_fin")[:6]

        return render(request, self.template_name, {
            "conseiller": conseiller,
            "evaluations": evaluations,
            "peut_demander": request.user.is_authenticated and getattr(request.user, "is_student", False),
        })


class MesRendezVousView(VerifiedAccountMixin, View):
    """Liste de tous les RDV de l'utilisateur connecté (à venir + passés)."""
    template_name = "orientation/mes_rdv.html"

    def get(self, request):
        from .models.rdv import RendezVous
        user = request.user
        rdvs = RendezVous.objects.filter(
            Q(demande__etudiant=user) | Q(demande__conseiller=user)
        ).exclude(statut="ANNULE").select_related(
            "demande__etudiant", "demande__conseiller", "propose_par"
        ).order_by("date_rdv")

        now = timezone.now()
        return render(request, self.template_name, {
            "rdvs_a_venir": [r for r in rdvs if r.date_rdv >= now],
            "rdvs_passes":  [r for r in rdvs if r.date_rdv < now],
        })


class ProposerRendezVousView(VerifiedAccountMixin, View):
    """Propose un nouveau créneau RDV dans une session d'accompagnement active."""

    def post(self, request, pk):
        from .models.rdv import RendezVous
        from .forms import RendezVousForm
        demande = get_object_or_404(DemandeAccompagnement, pk=pk)
        user = request.user

        if demande.etudiant != user and demande.conseiller != user:
            raise PermissionDenied
        if demande.statut not in (StatutDemande.ACCEPTEE, StatutDemande.EN_COURS):
            messages.error(request, _("La session doit être active pour proposer un rendez-vous."))
            return redirect("orientation:demande-detail", pk=pk)

        form = RendezVousForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.demande = demande
            rdv.propose_par = user
            rdv.save()
            autre = rdv.autre_participant
            if autre:
                _notify(
                    autre,
                    titre="Nouveau rendez-vous proposé",
                    message=f"{user.get_full_name()} vous propose un RDV le {rdv.date_rdv:%d/%m à %H:%M}.",
                    type_notif="INFO",
                    action_url=f"/orientation/accompagnement/{pk}/",
                )
            messages.success(request, _("Rendez-vous proposé — en attente de confirmation."))
        else:
            messages.error(request, _("Date ou format invalide."))

        return redirect("orientation:demande-detail", pk=pk)

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


class ConfirmerRendezVousView(VerifiedAccountMixin, View):
    """L'autre partie confirme un RDV proposé."""

    def post(self, request, pk):
        from .models.rdv import RendezVous, StatutRendezVous
        rdv = get_object_or_404(RendezVous, pk=pk)
        user = request.user
        demande = rdv.demande

        if demande.etudiant != user and demande.conseiller != user:
            raise PermissionDenied
        if rdv.propose_par == user:
            messages.error(request, _("Vous ne pouvez pas confirmer votre propre proposition."))
            return redirect("orientation:demande-detail", pk=demande.pk)

        rdv.statut = StatutRendezVous.CONFIRME
        rdv.save(update_fields=["statut", "updated_at"])

        _notify(
            rdv.propose_par,
            titre="Rendez-vous confirmé",
            message=f"Votre RDV du {rdv.date_rdv:%d/%m à %H:%M} a été confirmé.",
            type_notif="SUCCESS",
            action_url=f"/orientation/accompagnement/{demande.pk}/",
        )
        messages.success(request, _("Rendez-vous confirmé !"))
        return redirect("orientation:demande-detail", pk=demande.pk)

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])


class AnnulerRendezVousView(VerifiedAccountMixin, View):
    """Annuler un RDV (l'un ou l'autre des participants)."""

    def post(self, request, pk):
        from .models.rdv import RendezVous, StatutRendezVous
        rdv = get_object_or_404(RendezVous, pk=pk)
        user = request.user
        demande = rdv.demande

        if demande.etudiant != user and demande.conseiller != user:
            raise PermissionDenied
        if rdv.statut == StatutRendezVous.ANNULE:
            messages.info(request, _("Ce rendez-vous est déjà annulé."))
            return redirect("orientation:demande-detail", pk=demande.pk)

        rdv.statut = StatutRendezVous.ANNULE
        rdv.motif_annulation = request.POST.get("motif_annulation", "").strip()
        rdv.save(update_fields=["statut", "motif_annulation", "updated_at"])

        autre = rdv.autre_participant
        if autre:
            _notify(
                autre,
                titre="Rendez-vous annulé",
                message=f"Le RDV du {rdv.date_rdv:%d/%m à %H:%M} a été annulé par {user.get_full_name()}.",
                type_notif="WARNING",
                action_url=f"/orientation/accompagnement/{demande.pk}/",
            )
        messages.info(request, _("Rendez-vous annulé."))
        return redirect("orientation:demande-detail", pk=demande.pk)

    def get(self, request, pk):
        return HttpResponseNotAllowed(["POST"])
