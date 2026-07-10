"""
Vues API pour la bibliothèque numérique.

Endpoints :
- GET  /api/v1/bibliotheque/                       → liste paginée des ressources
- GET  /api/v1/bibliotheque/<slug>/                → détail d'une ressource
- GET  /api/v1/bibliotheque/<slug>/download/       → téléchargement (avec check premium)
- POST /api/v1/bibliotheque/<slug>/vote/           → voter (note 1-5)
- POST /api/v1/bibliotheque/<slug>/favori/         → ajouter aux favoris
- DELETE /api/v1/bibliotheque/<slug>/favori/       → retirer des favoris
- GET  /api/v1/bibliotheque/recommandations/       → recommandations personnalisées
- GET  /api/v1/bibliotheque/categories/            → arbre des catégories
- GET  /api/v1/bibliotheque/stats/                 → statistiques globales
"""
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.library.models import (
    RessourcePedagogique, CategorieBibliotheque, VoteRessource,
    TypeRessource, NiveauScolaire,
)
from apps.library.services import BibliothequeService


# ─── Serializers ───

class RessourceSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True, default="")
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    est_accessible = serializers.SerializerMethodField()

    class Meta:
        model = RessourcePedagogique
        fields = [
            "id", "titre", "slug", "description_courte", "type", "type_display",
            "matiere", "niveaux", "auteur", "editeur", "annee_publication",
            "fichier_taille_mo", "nombre_pages", "duree_minutes",
            "is_premium", "is_free", "note_moyenne", "nombre_votes",
            "nombre_telechargements", "nombre_vues", "is_verified",
            "categorie_nom", "est_accessible", "apercu",
        ]
        read_only_fields = ["id", "slug", "note_moyenne", "nombre_votes",
                            "nombre_telechargements", "nombre_vues", "is_verified"]

    def get_est_accessible(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return obj.is_free
        return BibliothequeService.verifier_acces(request.user, obj)


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieBibliotheque
        fields = ["id", "nom", "slug", "parent", "description", "icone", "ordre"]


class VoteSerializer(serializers.Serializer):
    note = serializers.IntegerField(min_value=1, max_value=5)
    commentaire = serializers.CharField(required=False, allow_blank=True)


# ─── Vues ───

class RessourceListView(generics.ListAPIView):
    """Liste paginée des ressources avec filtres."""
    serializer_class = RessourceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = RessourcePedagogique.objects.filter(is_active=True)
        # Filtres
        type_ = self.request.query_params.get("type")
        matiere = self.request.query_params.get("matiere")
        niveau = self.request.query_params.get("niveau")
        premium = self.request.query_params.get("premium")
        search = self.request.query_params.get("q")
        ordering = self.request.query_params.get("ordering", "-created_at")

        if type_:
            qs = qs.filter(type=type_)
        if matiere:
            qs = qs.filter(matiere__iexact=matiere)
        if niveau:
            qs = qs.filter(niveaux__contains=[niveau])
        if premium == "true":
            qs = qs.filter(is_premium=True)
        elif premium == "false":
            qs = qs.filter(is_free=True)
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(titre__icontains=search)
                | Q(description__icontains=search)
                | Q(auteur__icontains=search)
            )
        return qs.order_by(ordering)


class RessourceDetailView(generics.RetrieveAPIView):
    """Détail d'une ressource."""
    serializer_class = RessourceSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    queryset = RessourcePedagogique.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrémente le compteur de vues
        BibliothequeService.enregistrer_vue(instance)
        return super().retrieve(request, *args, **kwargs)


class RessourceDownloadView(APIView):
    """Téléchargement d'une ressource (vérifie l'accès premium)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        ressource = get_object_or_404(RessourcePedagogique, slug=slug, is_active=True)
        if not BibliothequeService.verifier_acces(request.user, ressource):
            return Response(
                {
                    "error": "ACCES_PREMIUM_REQUIS",
                    "message": "Cette ressource est réservée aux abonnés Premium.",
                    "upgrade_url": "/api/v1/payments/plans/",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if not ressource.fichier:
            if ressource.url_externe:
                return Response({"url_externe": ressource.url_externe})
            raise Http404("Fichier introuvable")
        BibliothequeService.enregistrer_telechargement(
            request.user, ressource,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        response = FileResponse(ressource.fichier.open("rb"))
        response["Content-Disposition"] = f'attachment; filename="{ressource.titre}.pdf"'
        return response


class RessourceVoteView(APIView):
    """Vote sur une ressource."""
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        ressource = get_object_or_404(RessourcePedagogique, slug=slug, is_active=True)
        ser = VoteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        vote = BibliothequeService.voter(
            request.user, ressource,
            note=ser.validated_data["note"],
            commentaire=ser.validated_data.get("commentaire", ""),
        )
        return Response(
            {
                "message": "Vote enregistré.",
                "note_moyenne": ressource.refresh_from_db() or ressource.note_moyenne,
            },
            status=status.HTTP_201_CREATED,
        )


class FavoriToggleView(APIView):
    """Ajoute ou retire une ressource des favoris."""
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        ressource = get_object_or_404(RessourcePedagogique, slug=slug, is_active=True)
        note = request.data.get("note_personnelle", "")
        BibliothequeService.ajouter_favori(request.user, ressource, note)
        return Response({"message": "Ajouté aux favoris."}, status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        ressource = get_object_or_404(RessourcePedagogique, slug=slug)
        BibliothequeService.retirer_favori(request.user, ressource)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecommandationsView(APIView):
    """Recommandations personnalisées pour l'utilisateur courant."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recommandations = BibliothequeService.recommander_pour_etudiant(request.user, limit=10)
        ser = RessourceSerializer(recommandations, many=True, context={"request": request})
        return Response({"recommandations": ser.data})


class CategoriesListView(generics.ListAPIView):
    """Liste des catégories (arbre plat avec parent)."""
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]
    queryset = CategorieBibliotheque.objects.filter(is_active=True)


class StatsBibliothequeView(APIView):
    """Statistiques globales de la bibliothèque."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(BibliothequeService.statistiques_globales())
