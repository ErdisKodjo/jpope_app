"""
URLs de l'API accounts.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

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
