"""
URLs de l'app payments.
"""
from django.urls import path, include

app_name = "payments"

urlpatterns = [
    path("api/", include("apps.payments.api.urls", namespace="payments-api")),
]
