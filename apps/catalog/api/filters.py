"""
Filtres DRF pour le catalog.
"""
import django_filters

from apps.catalog.models import Etablissement, Formation, Metier, Domaine


class EtablissementFilter(django_filters.FilterSet):
    """Filtres pour les établissements."""
    ville = django_filters.CharFilter(lookup_expr="iexact")
    pays = django_filters.CharFilter(lookup_expr="iexact")
    type = django_filters.CharFilter()
    statut = django_filters.CharFilter()
    note_min = django_filters.NumberFilter(field_name="note_globale", lookup_expr="gte")
    budget_max = django_filters.NumberFilter(
        field_name="frais_scolarite_annuel_max",
        lookup_expr="lte",
    )
    avec_bourses = django_filters.BooleanFilter(
        field_name="propose_bourses",
    )
    domaine = django_filters.UUIDFilter(field_name="domaines_enseignes__id")
    verified = django_filters.BooleanFilter(field_name="is_verified")

    class Meta:
        model = Etablissement
        fields = [
            "ville",
            "pays",
            "type",
            "statut",
            "note_min",
            "budget_max",
            "avec_bourses",
            "domaine",
            "verified",
        ]


class FormationFilter(django_filters.FilterSet):
    """Filtres pour les formations."""
    domaine = django_filters.UUIDFilter()
    etablissement = django_filters.UUIDFilter()
    niveau = django_filters.CharFilter()
    modalite = django_filters.CharFilter()
    cout_max = django_filters.NumberFilter(field_name="cout_annuel", lookup_expr="lte")
    cout_min = django_filters.NumberFilter(field_name="cout_annuel", lookup_expr="gte")
    importance = django_filters.CharFilter(field_name="importance_strategique")
    avec_bourses = django_filters.BooleanFilter(field_name="bourses_disponibles")
    inscriptions_ouvertes = django_filters.BooleanFilter(
        method="filter_inscriptions_ouvertes"
    )
    ville = django_filters.CharFilter(field_name="etablissement__ville", lookup_expr="iexact")

    class Meta:
        model = Formation
        fields = [
            "domaine",
            "etablissement",
            "niveau",
            "modalite",
            "cout_max",
            "cout_min",
            "importance",
            "avec_bourses",
            "inscriptions_ouvertes",
            "ville",
        ]

    def filter_inscriptions_ouvertes(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(
                date_limite_inscription__gte=timezone.now().date()
            )
        return queryset


class MetierFilter(django_filters.FilterSet):
    """Filtres pour les métiers."""
    domaine = django_filters.UUIDFilter()
    demande = django_filters.CharFilter(field_name="demande_marche")
    niveau_requis = django_filters.CharFilter(field_name="niveau_etude_requis")
    revenu_min = django_filters.NumberFilter(field_name="revenu_moyen", lookup_expr="gte")
    pays = django_filters.CharFilter(
        field_name="pays_concernes",
        lookup_expr="contains",
    )

    class Meta:
        model = Metier
        fields = [
            "domaine",
            "demande",
            "niveau_requis",
            "revenu_min",
            "pays",
        ]
