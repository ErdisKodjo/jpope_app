"""
Vues API pour l'app events.
"""
from django.db.models import F
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.models import Evenement, InscriptionEvenement
from apps.events.services import EventService

from .serializers import (
    EvenementListSerializer,
    EvenementDetailSerializer,
    InscriptionEvenementSerializer,
    InscriptionCreateSerializer,
    FeedbackSerializer,
)


class EvenementViewSet(viewsets.ModelViewSet):
    """CRUD des événements."""
    queryset = Evenement.objects.select_related("etablissement").prefetch_related(
        "domaines_concernes"
    )
    permission_classes = [AllowAny]
    search_fields = ["titre", "description", "ville", "tags"]
    ordering_fields = [
        "date_debut", "nombre_inscrits", "nombre_vues", "created_at",
    ]
    ordering = ["-date_debut"]
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()

        # Par défaut, ne montrer que les événements publiés (sauf pour admin)
        if not (
            self.request.user.is_authenticated
            and self.request.user.role in ["ADMIN", "SCHOOL_REP"]
        ):
            qs = qs.filter(statut="PUBLIE")

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvenementDetailSerializer
        return EvenementListSerializer

    def perform_create(self, serializer):
        from apps.events.models import StatutEvenement
        from django.utils import timezone

        evenement = serializer.save(createur=self.request.user)

        # Publier automatiquement si admin
        if self.request.user.role == "ADMIN":
            evenement.statut = StatutEvenement.PUBLIE
            evenement.published_at = timezone.now()
            evenement.save(update_fields=["statut", "published_at"])

    def retrieve(self, request, *args, **kwargs):
        """Incrémenter le compteur de vues."""
        instance = self.get_object()
        EventService.incrementer_vues(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def a_venir(self, request):
        """Événements à venir."""
        limit = int(request.query_params.get("limit", 20))
        evenements = Evenement.objects.a_venir()[:limit]
        return Response(
            EvenementListSerializer(evenements, many=True).data
        )

    @action(detail=False, methods=["get"])
    def cette_semaine(self, request):
        """Événements de la semaine."""
        evenements = Evenement.objects.cette_semaine()
        return Response(
            EvenementListSerializer(evenements, many=True).data
        )

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Événements mis en avant."""
        evenements = Evenement.objects.featured()[:10]
        return Response(
            EvenementListSerializer(evenements, many=True).data
        )

    @action(detail=False, methods=["get"])
    def avec_inscriptions(self, request):
        """Événements avec inscriptions ouvertes."""
        limit = int(request.query_params.get("limit", 20))
        evenements = Evenement.objects.avec_inscriptions_ouvertes()[:limit]
        return Response(
            EvenementListSerializer(evenements, many=True).data
        )

    @action(detail=False, methods=["get"])
    def par_type(self, request):
        """Événements filtrés par type."""
        type_evt = request.query_params.get("type")
        if not type_evt:
            return Response(
                {"error": "Paramètre 'type' requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        evenements = Evenement.objects.par_type(type_evt)[:50]
        return Response(
            EvenementListSerializer(evenements, many=True).data
        )

    @action(detail=False, methods=["get"])
    def villes(self, request):
        """Liste des villes avec événements."""
        villes = (
            Evenement.objects.publies()
            .values_list("ville", flat=True)
            .distinct()
            .order_by("ville")
        )
        return Response(list(villes))

    @action(detail=True, methods=["get"])
    def stats(self, request, slug=None):
        """Statistiques d'un événement (admin/organisateur)."""
        evenement = self.get_object()
        stats = EventService.get_stats_evenement(evenement)
        return Response(stats)


class InscriptionEvenementViewSet(viewsets.ModelViewSet):
    """CRUD des inscriptions aux événements."""
    serializer_class = InscriptionEvenementSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        qs = InscriptionEvenement.objects.filter(
            utilisateur=self.request.user
        ).select_related("evenement")

        statut = self.request.query_params.get("statut")
        if statut:
            qs = qs.filter(statut=statut)

        return qs

    def create(self, request, *args, **kwargs):
        """Inscrire l'utilisateur à un événement."""
        serializer = InscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            evenement = Evenement.objects.get(
                id=data["evenement_id"],
                statut="PUBLIE",
            )
        except Evenement.DoesNotExist:
            return Response(
                {"error": "Événement introuvable ou non publié."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            inscription = EventService.inscrire_utilisateur(
                utilisateur=request.user,
                evenement=evenement,
                nombre_accompagnants=data.get("nombre_accompagnants", 0),
                besoins_speciaux=data.get("besoins_speciaux", ""),
                source=data.get("source", "api"),
            )

            return Response(
                {
                    "message": "Inscription réussie !",
                    "inscription": InscriptionEvenementSerializer(inscription).data,
                    "statut": inscription.get_statut_display(),
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        """Annuler une inscription."""
        inscription = self.get_object()

        try:
            EventService.annuler_inscription(request.user, inscription.evenement)
            return Response(
                {"message": "Inscription annulée avec succès."},
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def mes_inscriptions(self, request):
        """Liste des inscriptions de l'utilisateur avec détails événements."""
        inscriptions = self.get_queryset().filter(
            statut__in=["INSCRIT", "CONFIRME", "LISTE_ATTENTE"]
        )
        data = []
        for inscription in inscriptions:
            data.append({
                "inscription": InscriptionEvenementSerializer(inscription).data,
                "evenement": EvenementListSerializer(inscription.evenement).data,
            })
        return Response(data)

    @action(detail=False, methods=["get"])
    def historique(self, request):
        """Historique des événements passés auxquels l'utilisateur a participé."""
        inscriptions = InscriptionEvenement.objects.filter(
            utilisateur=request.user,
            a_participe=True,
        ).select_related("evenement")

        data = []
        for inscription in inscriptions:
            data.append({
                "inscription": InscriptionEvenementSerializer(inscription).data,
                "evenement": EvenementListSerializer(inscription.evenement).data,
            })
        return Response(data)

    @action(detail=True, methods=["post"])
    def feedback(self, request, pk=None):
        """Soumettre un feedback après participation."""
        inscription = self.get_object()

        if not inscription.a_participe:
            return Response(
                {"error": "Vous n'avez pas participé à cet événement."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inscription.feedback = serializer.validated_data["feedback"]
        inscription.note_satisfaction = serializer.validated_data["note_satisfaction"]
        inscription.save(update_fields=["feedback", "note_satisfaction", "updated_at"])

        return Response(
            {"message": "Merci pour votre retour !"},
            status=status.HTTP_200_OK,
        )


class ConfirmationInscriptionView(APIView):
    """Confirmation d'inscription via token (lien email)."""
    permission_classes = [AllowAny]

    def get(self, request, token):
        inscription = EventService.confirmer_inscription(token)

        if inscription:
            return Response({
                "message": "Inscription confirmée avec succès !",
                "evenement": EvenementListSerializer(inscription.evenement).data,
            })

        return Response(
            {"error": "Token invalide ou déjà utilisé."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CheckinView(APIView):
    """Check-in via QR code (pour les organisateurs)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        qr_token = request.data.get("qr_token")

        if not qr_token:
            return Response(
                {"error": "QR code token requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        inscription = EventService.checkin_inscription(qr_token)

        if inscription:
            return Response({
                "message": f"Bienvenue {inscription.utilisateur.get_full_name()} !",
                "utilisateur": {
                    "nom": inscription.utilisateur.get_full_name(),
                    "email": inscription.utilisateur.email,
                },
                "evenement": inscription.evenement.titre,
            })

        return Response(
            {"error": "QR code invalide ou inscription introuvable."},
            status=status.HTTP_400_BAD_REQUEST,
        )
