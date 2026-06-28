"""
Filtres DRF pour l'API accounts.
"""
import django_filters
from django.contrib.auth import get_user_model

from apps.accounts.models.enums import UserRole, StatutCompte

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    """Filtres pour la liste des utilisateurs (admin)."""
    email = django_filters.CharFilter(lookup_expr="icontains")
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    role = django_filters.ChoiceFilter(choices=UserRole.choices)
    statut_compte = django_filters.ChoiceFilter(choices=StatutCompte.choices)
    is_active = django_filters.BooleanFilter()
    is_email_verified = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
            "statut_compte",
            "is_active",
            "is_email_verified",
        ]
