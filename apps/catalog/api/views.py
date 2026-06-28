"""
Vues API pour le catalog.
"""
from django.db.models import Count, Q
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Domaine, Etablissement, Formation, Metier
from apps.catalog.services import CatalogService, RankingService

from .filters import EtablissementFilter, FormationFilter, MetierFilter
from .permissions import IsAdminOrSchoolRepForWrite
from .serializers import (
    DomaineDetailSerializer,
    DomaineSerializer,
    EtablissementClassementSerializer,
    EtablissementDetailSerializer,
    EtablissementListSerializer,
    FormationDetailSerializer,
    FormationListSerializer,
    MetierDetailSerializer,
    MetierListSerializer,
)

# ──────────────────────────────────────────────
# Domaines
# ──────────────────────────────────────────────

class DomaineViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste et détail des domaines."""
    queryset = Domaine.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DomaineDetailSerializer
        return DomaineSerializer

    @action(detail=False, methods=["get"])
    def populaires(self, request):
        """Top 10 domaines par nombre de formations."""
        limit = int(request.query_params.get("limit", 10))
        domaines = CatalogService.get_domaines_populaires(limit)
        return Response(DomaineSerializer(domaines, many=True).data)


# ──────────────────────────────────────────────
# Métiers
# ──────────────────────────────────────────────

class MetierViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste et détail des métiers."""
    queryset = Metier.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filterset_class = MetierFilter
    search_fields = ["nom", "description", "domaine__nom"]
    ordering_fields = [
        "nom",
        "revenu_moyen",
        "taux_emploi",
        "score_attractivite",
    ]
    ordering = ["-score_attractivite"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MetierDetailSerializer
        return MetierListSerializer

    @action(detail=False, methods=["get"])
    def porteurs(self, request):
        """Métiers avec forte demande."""
        limit = int(request.query_params.get("limit", 15))
        metiers = CatalogService.get_metiers_porteurs(limit)
        return Response(MetierListSerializer(metiers, many=True).data)

    @action(detail=False, methods=["get"])
    def top_revenus(self, request):
        """Métiers avec les meilleurs revenus."""
        limit = int(request.query_params.get("limit", 20))
        metiers = Metier.objects.filter(is_active=True).order_by("-revenu_moyen")[:limit]
        return Response(MetierListSerializer(metiers, many=True).data)


# ──────────────────────────────────────────────
# Établissements
# ──────────────────────────────────────────────

class EtablissementViewSet(viewsets.ModelViewSet):
    """CRUD des établissements."""
    queryset = Etablissement.objects.filter(is_active=True)
    permission_classes = [IsAdminOrSchoolRepForWrite]
    filterset_class = EtablissementFilter
    search_fields = ["nom", "sigle", "ville", "description"]
    ordering_fields = [
        "nom",
        "note_globale",
        "score_qualite_global",
        "classement_national",
        "frais_scolarite_annuel_max",
        "date_creation",
    ]
    ordering = ["-score_qualite_global"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EtablissementDetailSerializer
        return EtablissementListSerializer

    @action(detail=False, methods=["get"])
    def top(self, request):
        """Top établissements par note."""
        limit = int(request.query_params.get("limit", 10))
        etablissements = Etablissement.objects.top_notes(limit)
        return Response(EtablissementListSerializer(etablissements, many=True).data)

    @action(detail=False, methods=["get"])
    def villes(self, request):
        """Liste des villes avec établissements."""
        villes = (
            Etablissement.objects.filter(is_active=True)
            .values_list("ville", flat=True)
            .distinct()
            .order_by("ville")
        )
        return Response(list(villes))

    @action(detail=True, methods=["get"])
    def classement_detail(self, request, slug=None):
        """Détail du classement d'un établissement."""
        etab = self.get_object()
        detail = RankingService.get_detail_classement(etab)
        return Response(detail)

    @action(detail=True, methods=["get"])
    def formations(self, request, slug=None):
        """Liste des formations de l'établissement."""
        etab = self.get_object()
        formations = etab.formations.filter(is_active=True)

        # Filtres optionnels
        niveau = request.query_params.get("niveau")
        if niveau:
            formations = formations.filter(niveau=niveau)

        domaine = request.query_params.get("domaine")
        if domaine:
            formations = formations.filter(domaine__slug=domaine)

        return Response(FormationListSerializer(formations, many=True).data)


# ──────────────────────────────────────────────
# Formations
# ──────────────────────────────────────────────

class FormationViewSet(viewsets.ModelViewSet):
    """CRUD des formations."""
    queryset = Formation.objects.filter(is_active=True).select_related(
        "etablissement", "domaine"
    )
    permission_classes = [IsAdminOrSchoolRepForWrite]
    filterset_class = FormationFilter
    search_fields = ["nom", "description", "domaine__nom", "etablissement__nom"]
    ordering_fields = [
        "nom",
        "cout_annuel",
        "score_qualite",
        "taux_reussite",
        "taux_insertion_12mois",
        "date_limite_inscription",
    ]
    ordering = ["-score_qualite"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FormationDetailSerializer
        return FormationListSerializer

    @action(detail=False, methods=["get"])
    def top_qualite(self, request):
        """Top formations par score qualité."""
        limit = int(request.query_params.get("limit", 20))
        formations = Formation.objects.top_qualite(limit)
        return Response(FormationListSerializer(formations, many=True).data)

    @action(detail=False, methods=["get"])
    def strategiques(self, request):
        """Formations d'importance stratégique."""
        formations = Formation.objects.strategiques()
        return Response(FormationListSerializer(formations, many=True).data)

    @action(detail=False, methods=["get"])
    def meilleur_rapport(self, request):
        """Meilleur rapport qualité/prix."""
        limit = int(request.query_params.get("limit", 20))
        formations = CatalogService.get_formations_meilleur_rapport_qualite_prix(limit)
        return Response(FormationListSerializer(formations, many=True).data)

    @action(detail=False, methods=["get"])
    def inscriptions_ouvertes(self, request):
        """Formations avec inscriptions encore ouvertes."""
        formations = Formation.objects.inscriptions_ouvertes()
        return Response(FormationListSerializer(formations, many=True).data)


# ──────────────────────────────────────────────
# Classements
# ──────────────────────────────────────────────

class ClassementEtablissementView(generics.ListAPIView):
    """Classement national des établissements."""
    serializer_class = EtablissementClassementSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Etablissement.objects.filter(
            is_active=True,
            is_verified=True,
            classement_national__isnull=False,
        ).order_by("classement_national")

        # Filtre par ville optionnel
        ville = self.request.query_params.get("ville")
        if ville:
            qs = qs.filter(ville__iexact=ville)

        # Limite
        limit = int(self.request.query_params.get("limit", 50))
        return qs[:limit]


class ClassementFormationView(generics.ListAPIView):
    """Classement des formations par domaine."""
    serializer_class = FormationListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Formation.objects.filter(is_active=True)

        domaine = self.request.query_params.get("domaine")
        if domaine:
            qs = qs.filter(domaine__slug=domaine)

        ville = self.request.query_params.get("ville")
        if ville:
            qs = qs.filter(etablissement__ville__iexact=ville)

        niveau = self.request.query_params.get("niveau")
        if niveau:
            qs = qs.filter(niveau=niveau)

        return qs.order_by("-score_qualite")[:100]


class MethodologieClassementView(APIView):
    """Retourne la méthodologie officielle de classement (transparence)."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "titre": "Méthodologie de classement AvenSU-Orienta",
            "description": (
                "Notre classement est basé sur 6 critères pondérés, "
                "calculés à partir de données publiques et vérifiées."
            ),
            "criteres": RankingService.get_methodologie(),
            "mise_a_jour": "Annuelle (janvier)",
            "source": "Données établissements + avis étudiants",
        })


# ──────────────────────────────────────────────
# Comparateur & Simulateur
# ──────────────────────────────────────────────

class ComparateurView(APIView):
    """Compare jusqu'à 3 établissements ou 3 formations."""
    permission_classes = [AllowAny]

    def post(self, request, type_comparaison):
        ids = request.data.get("ids", [])

        if not ids or not isinstance(ids, list):
            return Response(
                {"error": "Liste d'IDs requise."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if type_comparaison == "etablissements":
                result = CatalogService.comparer_etablissements(ids)
            elif type_comparaison == "formations":
                result = CatalogService.comparer_formations(ids)
            else:
                return Response(
                    {"error": "Type de comparaison invalide."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(result)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SimulateurCoutView(APIView):
    """Simule le coût total d'une formation."""
    permission_classes = [AllowAny]

    def post(self, request):
        formation_id = request.data.get("formation_id")
        annees = request.data.get("annees")
        mode_vie = int(request.data.get("mode_vie_mensuel", 50000))
        bourse = int(request.data.get("bourse_montant", 0))

        if not formation_id:
            return Response(
                {"error": "formation_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = CatalogService.simuler_cout_formation(
                formation_id=formation_id,
                annees=annees,
                mode_vie_mensuel=mode_vie,
                bourse_montant=bourse,
            )
            return Response(result)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )


# ──────────────────────────────────────────────
# Statistiques
# ──────────────────────────────────────────────

class CatalogStatsView(APIView):
    """Statistiques globales du catalogue."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(CatalogService.get_stats_globales())
