"""
Vues web pour l'app accounts.
"""
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.utils.timezone import now
from django.views.generic import FormView, TemplateView, UpdateView, ListView

from .forms import (
    LoginForm,
    RegisterForm,
    UserProfileForm,
    StudentProfileForm,
    PasswordResetRequestForm,
    RejectVerificationForm,
    NotesEtudiantForm,
)
from .mixins import AdminRequiredMixin
from .models.enums import StatutCompte, UserRole
from .models.verification import DocumentVerification
from .services.auth_service import AuthService

logger = logging.getLogger(__name__)

User = get_user_model()

# Rôles nécessitant vérification de document
_ROLES_VERIFICATION = {UserRole.PARENT, UserRole.COUNSELOR, UserRole.SCHOOL_REP}


class HomeView(TemplateView):
    """Page d'accueil avec formations et événements dynamiques."""
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.catalog.models import Formation
        from apps.events.models import Evenement

        context["formations_populaires"] = (
            Formation.objects.filter(is_active=True)
            .select_related("etablissement", "domaine")
            .order_by("-is_featured", "-score_qualite")[:3]
        )
        context["evenements_a_venir"] = (
            Evenement.objects.filter(statut="PUBLIE", date_debut__gte=now())
            .order_by("date_debut")[:2]
        )
        return context


class LoginView(FormView):
    """Vue de connexion."""
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("accounts:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        user.update_last_activity()
        messages.success(self.request, _("Bienvenue, %(name)s !") % {"name": user.get_short_name()})

        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Identifiants invalides. Veuillez réessayer."))
        return super().form_invalid(form)


class LogoutView(LoginRequiredMixin, View):
    """Vue de déconnexion."""

    def post(self, request):
        logout(request)
        messages.info(request, _("Vous avez été déconnecté."))
        return redirect("accounts:login")

    def get(self, request):
        return self.post(request)


class RegisterView(FormView):
    """
    Vue d'inscription.
    - Étudiants : compte activé immédiatement.
    - Autres rôles : compte EN_ATTENTE_VERIFICATION + document enregistré.
    """
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:home")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            kwargs["files"] = self.request.FILES
        return kwargs

    def form_valid(self, form):
        role = form.cleaned_data.get("role")
        needs_verification = role in _ROLES_VERIFICATION

        # Créer l'utilisateur sans sauvegarder encore
        user = form.save(commit=False)
        if needs_verification:
            user.statut_compte = StatutCompte.EN_ATTENTE_VERIFICATION
        user.save()

        # Sauvegarder le document de vérification si applicable
        if needs_verification:
            document_file = form.cleaned_data.get("document")
            type_doc = form.cleaned_data.get("type_document", "CNI")
            if document_file:
                DocumentVerification.objects.create(
                    user=user,
                    document=document_file,
                    type_document=type_doc,
                )

        # Envoyer email de vérification
        try:
            AuthService.send_verification_email(user.id)
        except Exception:
            logger.exception(
                "Échec d'envoi de l'email de vérification à l'utilisateur %s",
                user.id,
            )

        if needs_verification:
            messages.success(
                self.request,
                _(
                    "Compte créé ! Votre dossier est en cours de vérification par notre équipe. "
                    "Vous serez notifié(e) par email dès que votre compte sera activé."
                ),
            )
        else:
            messages.success(
                self.request,
                _("Compte créé avec succès ! Vérifiez votre email pour activer votre compte."),
            )
        return super().form_valid(form)


class EmailVerificationView(View):
    """Vue de vérification de l'email via token."""

    def get(self, request):
        token = request.GET.get("token")
        if not token:
            messages.error(request, _("Token de vérification manquant."))
            return redirect("accounts:login")

        success = AuthService.verify_email_token(token)
        if success:
            messages.success(request, _("Votre email a été vérifié avec succès !"))
        else:
            messages.error(request, _("Le token est invalide ou a expiré."))

        return redirect("accounts:login")


class PasswordResetRequestView(FormView):
    """Vue de demande de réinitialisation de mot de passe."""
    template_name = "accounts/password_reset_request.html"
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            AuthService.send_password_reset_email(email)
        except Exception:
            logger.exception(
                "Échec d'envoi de l'email de réinitialisation de mot de passe"
            )

        messages.info(
            self.request,
            _("Si cet email existe, un lien de réinitialisation a été envoyé."),
        )
        return super().form_valid(form)


class PasswordResetConfirmView(View):
    """Vue de confirmation de réinitialisation de mot de passe."""
    template_name = "accounts/password_reset_confirm.html"

    def get(self, request):
        from django.shortcuts import render
        token = request.GET.get("token", "")
        return render(request, self.template_name, {"token": token})

    def post(self, request):
        token = request.POST.get("token")
        new_password = request.POST.get("new_password")
        new_password_confirm = request.POST.get("new_password_confirm")

        if new_password != new_password_confirm:
            messages.error(request, _("Les mots de passe ne correspondent pas."))
            return redirect(f"{request.path}?token={token}")

        success = AuthService.reset_password_with_token(token, new_password)
        if success:
            messages.success(request, _("Mot de passe réinitialisé avec succès."))
            return redirect("accounts:login")
        else:
            messages.error(request, _("Token invalide ou expiré."))
            return redirect("accounts:password_reset")


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vue du profil utilisateur."""
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["profile"] = self.request.user.profile
        return context


class ProfileEditView(LoginRequiredMixin, FormView):
    """Vue de modification du profil utilisateur."""
    template_name = "accounts/profile_edit.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("accounts:profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Profil mis à jour avec succès."))
        return super().form_valid(form)


class StudentProfileEditView(LoginRequiredMixin, FormView):
    """Vue de modification du profil étudiant."""
    template_name = "accounts/student_profile_edit.html"
    form_class = StudentProfileForm
    success_url = reverse_lazy("accounts:profile")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_student:
            messages.error(request, _("Accès réservé aux étudiants."))
            return redirect("accounts:profile")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        profile = getattr(self.request.user, "student_profile", None)
        if profile:
            return {
                "serie_bac": profile.serie_bac,
                "annee_bac": profile.annee_bac,
                "moyenne_generale": profile.moyenne_generale,
                "etablissement_scolaire": profile.etablissement_scolaire,
                "projet_professionnel": profile.projet_professionnel,
            }
        return {}

    def form_valid(self, form):
        profile = getattr(self.request.user, "student_profile", None)
        if profile:
            for field, value in form.cleaned_data.items():
                setattr(profile, field, value)
            profile.save()

            if profile.is_complete:
                self.request.user.profile_complete = True
                self.request.user.save(update_fields=["profile_complete"])

        messages.success(self.request, _("Profil étudiant mis à jour avec succès."))
        return super().form_valid(form)


class NotesEtudiantView(LoginRequiredMixin, FormView):
    """Vue de saisie des notes académiques (étudiants uniquement)."""
    template_name = "accounts/notes_etudiant.html"
    form_class = NotesEtudiantForm
    success_url = reverse_lazy("accounts:notes_etudiant")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_student:
            messages.error(request, _("Accès réservé aux étudiants."))
            return redirect("accounts:profile")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        from .models.notes import NotesEtudiant
        notes, _ = NotesEtudiant.objects.get_or_create(etudiant=self.request.user)
        kwargs["instance"] = notes
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models.notes import NotesEtudiant
        notes, _ = NotesEtudiant.objects.get_or_create(etudiant=self.request.user)
        context["notes"] = notes
        return context

    def form_valid(self, form):
        notes = form.save(commit=False)
        notes.etudiant = self.request.user
        notes.save()

        # Régénérer les recommandations si l'étudiant a déjà passé un test
        self._regenerer_recommandations()

        messages.success(self.request, _("Notes enregistrées ! Vos recommandations ont été mises à jour."))
        return super().form_valid(form)

    def _regenerer_recommandations(self):
        """Relance le moteur de recommandation avec le nouveau profil académique."""
        try:
            from apps.orientation.models import ReponseUtilisateur
            from apps.orientation.services.recommendation_engine import RecommendationEngine

            dernier_resultat = (
                ReponseUtilisateur.objects
                .filter(etudiant=self.request.user, resultat__isnull=False)
                .select_related("resultat")
                .order_by("-date_soumission")
                .first()
            )
            if dernier_resultat and hasattr(dernier_resultat, "resultat"):
                profile = getattr(self.request.user, "student_profile", None)
                RecommendationEngine.generer_recommandations(
                    resultat=dernier_resultat.resultat,
                    budget_max=profile.budget_max_annuel if profile else None,
                    villes_preferees=profile.villes_preferees if profile else None,
                )
        except Exception:
            logger.exception(
                "Échec de régénération des recommandations pour l'utilisateur %s",
                self.request.user.pk,
            )


# ─────────────────────────────────────────────────────
# Vérification de compte
# ─────────────────────────────────────────────────────

class VerificationPendingView(LoginRequiredMixin, TemplateView):
    """
    Page informative pour les comptes EN_ATTENTE_VERIFICATION.
    Affiche le statut du document soumis.
    """
    template_name = "accounts/verification_pending.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["verification"] = getattr(self.request.user, "verification_document", None)
        return context


# ─────────────────────────────────────────────────────
# Vues d'administration des vérifications
# ─────────────────────────────────────────────────────

class AdminVerifyListView(AdminRequiredMixin, ListView):
    """Liste des comptes en attente de vérification (admin uniquement)."""
    model = DocumentVerification
    template_name = "accounts/admin_verify_list.html"
    context_object_name = "verifications"
    paginate_by = 20

    def get_queryset(self):
        from .models.verification import StatutVerification
        statut = self.request.GET.get("statut", "SOUMIS")
        qs = DocumentVerification.objects.select_related(
            "user", "traite_par"
        ).order_by("-date_soumission")
        if statut in StatutVerification.values:
            qs = qs.filter(statut=statut)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models.verification import StatutVerification
        context["statut_filtre"] = self.request.GET.get("statut", "SOUMIS")
        context["statut_choices"] = StatutVerification.choices
        context["reject_form"] = RejectVerificationForm()
        return context


class AdminVerifyApproveView(AdminRequiredMixin, View):
    """Approbation d'un document de vérification (POST uniquement)."""

    def post(self, request, pk):
        verification = get_object_or_404(DocumentVerification, pk=pk)
        verification.approuver(request.user)
        messages.success(
            request,
            _(f"Le compte de {verification.user.get_full_name()} a été activé."),
        )
        return redirect("accounts:admin_verify_list")


class AdminVerifyRejectView(AdminRequiredMixin, View):
    """Rejet d'un document de vérification avec motif (POST uniquement)."""

    def post(self, request, pk):
        verification = get_object_or_404(DocumentVerification, pk=pk)
        form = RejectVerificationForm(request.POST)
        if form.is_valid():
            verification.rejeter(request.user, motif=form.cleaned_data["motif"])
            messages.warning(
                request,
                _(f"Le compte de {verification.user.get_full_name()} a été rejeté."),
            )
        else:
            messages.error(request, _("Veuillez saisir un motif de rejet valide."))
        return redirect("accounts:admin_verify_list")
