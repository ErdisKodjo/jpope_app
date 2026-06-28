"""
Vues web pour l'app accounts.
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView

from .forms import (
    LoginForm,
    RegisterForm,
    UserProfileForm,
    StudentProfileForm,
    PasswordResetRequestForm,
)
from .services.auth_service import AuthService

User = get_user_model()


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
    """Vue d'inscription."""
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()

        # Envoyer email de vérification de manière asynchrone
        try:
            AuthService.send_verification_email(user.id)
        except Exception:
            pass  # Ne pas bloquer l'inscription si l'email échoue

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
            pass  # Ne pas révéler si l'email existe

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
