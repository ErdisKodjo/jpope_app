"""
URLs web pour l'app accounts.
"""
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Page d'accueil
    path("", views.HomeView.as_view(), name="home"),

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
    path("profile/notes/", views.NotesEtudiantView.as_view(), name="notes_etudiant"),

    # Vérification de compte (comptes non-étudiants en attente)
    path("verification-pending/", views.VerificationPendingView.as_view(), name="verification_pending"),

    # Administration des vérifications (ADMIN uniquement)
    path("admin/verify/", views.AdminVerifyListView.as_view(), name="admin_verify_list"),
    path("admin/verify/<int:pk>/approve/", views.AdminVerifyApproveView.as_view(), name="admin_verify_approve"),
    path("admin/verify/<int:pk>/reject/", views.AdminVerifyRejectView.as_view(), name="admin_verify_reject"),
]
