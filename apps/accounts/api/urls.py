"""
URLs de l'API accounts.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .two_factor_views import (
    TwoFASetupView,
    TwoFAConfirmView,
    TwoFADisableView,
    TwoFABackupRegenerateView,
    TwoFAChallengeView,
    TwoFAVerifyView,
    TwoFAStatusView,
)

app_name = "accounts-api"

router = DefaultRouter()
router.register(r"admin/users", views.UserAdminViewSet, basename="admin-users")

urlpatterns = [
    # Authentification
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/password/reset/", views.PasswordResetRequestView.as_view(), name="password_reset"),
    path("auth/email/verify/", views.EmailVerificationView.as_view(), name="email_verify"),
    path("auth/password/reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # 2FA (authentification à deux facteurs)
    path("auth/2fa/setup/", TwoFASetupView.as_view(), name="two_fa_setup"),
    path("auth/2fa/confirm/", TwoFAConfirmView.as_view(), name="two_fa_confirm"),
    path("auth/2fa/disable/", TwoFADisableView.as_view(), name="two_fa_disable"),
    path("auth/2fa/backup/regenerate/", TwoFABackupRegenerateView.as_view(), name="two_fa_backup_regenerate"),
    path("auth/2fa/challenge/", TwoFAChallengeView.as_view(), name="two_fa_challenge"),
    path("auth/2fa/verify/", TwoFAVerifyView.as_view(), name="two_fa_verify"),
    path("auth/2fa/status/", TwoFAStatusView.as_view(), name="two_fa_status"),

    # Utilisateur courant
    path("me/", views.CurrentUserView.as_view(), name="current_user"),
    path("me/password/", views.ChangePasswordView.as_view(), name="change_password"),

    # Profils
    path("me/profile/student/", views.StudentProfileView.as_view(), name="student_profile"),
    path("me/profile/counselor/", views.CounselorProfileView.as_view(), name="counselor_profile"),
    path("me/profile/school-rep/", views.SchoolRepProfileView.as_view(), name="school_rep_profile"),
    path("me/profile/parent/", views.ParentProfileView.as_view(), name="parent_profile"),

    # Router (admin)
    path("", include(router.urls)),
]
