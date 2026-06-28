"""
URLs de l'API events.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "events-api"

router = DefaultRouter()
router.register(r"evenements", views.EvenementViewSet, basename="evenements")
router.register(
    r"inscriptions",
    views.InscriptionEvenementViewSet,
    basename="inscriptions",
)

urlpatterns = [
    # Confirmation email
    path(
        "confirm/<str:token>/",
        views.ConfirmationInscriptionView.as_view(),
        name="confirm-inscription",
    ),

    # Check-in QR code
    path(
        "checkin/",
        views.CheckinView.as_view(),
        name="checkin",
    ),

    # Router
    path("", include(router.urls)),
]
