"""
URLs web pour l'app accounts.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views

app_name = "accounts"

urlpatterns = [
    # Page d'accueil
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    # Authentification
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),

    # Vérification email
    path("verify-email/", views.EmailVerificationView.as_view(), name="verify_email"),

    # Réinitialisation mot de passe
    path(
        "password-reset/",
        views.PasswordResetRequestView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    # Profil utilisateur
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/student/", views.StudentProfileEditView.as_view(), name="student_profile_edit"),
]
