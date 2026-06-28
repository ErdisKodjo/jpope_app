"""
URLs de l'API ranking.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "ranking-api"

router = DefaultRouter()
router.register(r"classements", views.ClassementViewSet, basename="classements")

urlpatterns = [
    path("", include(router.urls)),
]
