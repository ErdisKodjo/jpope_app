"""
Vues API pour l'app orientation.
"""
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orientation.models import (
    TestOrientation,
    ReponseUtilisateur,
    ResultatTest,
    Recommandation,
    DetailReponse,
    Question,
    StatutTest,
)
from apps.orientation.services import (
    ScoringService,
    RecommendationEngine,
    OrientationAnalyticsService,
)
from apps.orientation.tasks import calculer_resultat_et_recommandations

from .serializers import (
    TestOrientationListSerializer,
    TestOrientationDetailSerializer,
    QuestionSerializer,
    SoumettreTestSerializer,
    ReponseUtilisateurSerializer,
    ResultatTestSerializer,
    RecommandationSerializer,
    RecommandationEngagementSerializer,
)

# ──────────────────────────────────────────────
# Tests d'orientation (catalogue)
# ──────────────────────────────────────────────

class TestOrientationViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste et détail des tests d'orientation disponibles."""
    queryset = TestOrientation.objects.filter(is_active=True, is_public=True)
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TestOrientationDetailSerializer
        return TestOrientationListSerializer

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Tests mis en avant."""
        tests = self.queryset.filter(is_featured=True)
        return Response(TestOrientationListSerializer(tests, many=True).data)

# ──────────────────────────────────────────────
# Passation de test
# ──────────────────────────────────────────────

class CommencerTestView(APIView):
    """Commencer un nouveau test (crée une session)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        test_id = request.data.get("test_id")

        if not test_id:
            return Response(
                {"error": "test_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            test = TestOrientation.objects.get(id=test_id, is_active=True)
        except TestOrientation.DoesNotExist:
            return Response(
                {"error": "Test introuvable ou inactif."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not test.peut_etre_passe:
            return Response(
                {"error": "Ce test ne peut pas être passé actuellement."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Créer la session
        session = ReponseUtilisateur.objects.create(
            etudiant=request.user,
            test=test,
            statut=StatutTest.EN_COURS,
            nombre_questions_total=test.nombre_questions,
        )

        return Response(
            {
                "session_id": str(session.id),
                "test": TestOrientationDetailSerializer(test).data,
                "message": "Test commencé. Soumettez vos réponses à /orientation/test/submit/",
            },
            status=status.HTTP_201_CREATED,
        )

class SauvegarderReponseView(APIView):
    """Sauvegarder une réponse individuelle (progression en temps réel)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        question_id = request.data.get("question_id")

        if not session_id or not question_id:
            return Response(
                {"error": "session_id et question_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = ReponseUtilisateur.objects.get(
                id=session_id,
                etudiant=request.user,
                statut=StatutTest.EN_COURS,
            )
            question = Question.objects.get(id=question_id, test=session.test)
        except (ReponseUtilisateur.DoesNotExist, Question.DoesNotExist):
            return Response(
                {"error": "Session ou question introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate that choice_id belongs to this question
        choice_id = request.data.get("choice_id")
        if choice_id:
            try:
                choice_obj = question.choices.get(id=choice_id, is_active=True)
            except question.choices.model.DoesNotExist:
                return Response(
                    {"error": "Choix invalide pour cette question."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Créer ou mettre à jour le détail de réponse
        detail, _ = DetailReponse.objects.update_or_create(
            reponse_utilisateur=session,
            question=question,
            defaults={
                "choice_selectionne_id": request.data.get("choice_id"),
                "choices_selectionnes": request.data.get("choices_ids", []),
                "valeur_echelle": request.data.get("valeur_echelle"),
                "classement": request.data.get("classement", []),
                "reponse_ouverte": request.data.get("reponse_ouverte", ""),
                "temps_reponse_secondes": request.data.get("temps_reponse", 0),
            },
        )

        # Mettre à jour la progression
        session.nombre_questions_repondues = session.details.count()
        if session.nombre_questions_total > 0:
            session.progression = round(
                (session.nombre_questions_repondues / session.nombre_questions_total) * 100,
                1,
            )
        session.save(update_fields=["nombre_questions_repondues", "progression"])

        return Response(
            {
                "progression": session.progression,
                "questions_repondues": session.nombre_questions_repondues,
            },
            status=status.HTTP_200_OK,
        )

class SoumettreTestView(APIView):
    """Soumettre un test complet pour scoring et recommandations."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SoumettreTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            test = TestOrientation.objects.get(id=data["test_id"], is_active=True)
        except TestOrientation.DoesNotExist:
            return Response(
                {"error": "Test introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            # Créer la session
            session = ReponseUtilisateur.objects.create(
                etudiant=request.user,
                test=test,
                statut=StatutTest.TERMINE,
                date_fin=timezone.now(),
                duree_reelle_secondes=data["duree_totale_secondes"],
                nombre_questions_total=test.nombre_questions,
                appareil=data.get("appareil", "unknown"),
            )

            # Créer les détails de réponse
            details_a_creer = []
            for resp in data["reponses"]:
                details_a_creer.append(DetailReponse(
                    reponse_utilisateur=session,
                    question_id=resp["question_id"],
                    choice_selectionne_id=resp.get("choice_id"),
                    choices_selectionnes=resp.get("choices_ids", []),
                    valeur_echelle=resp.get("valeur_echelle"),
                    classement=resp.get("classement", []),
                    reponse_ouverte=resp.get("reponse_ouverte", ""),
                    temps_reponse_secondes=resp.get("temps_reponse_secondes", 0),
                ))

            DetailReponse.objects.bulk_create(details_a_creer)

            # Mettre à jour la progression
            session.nombre_questions_repondues = len(data["reponses"])
            session.progression = 100
            session.save(update_fields=["nombre_questions_repondues", "progression"])

        # Lancer le scoring et les recommandations en async
        calculer_resultat_et_recommandations.delay(str(session.id))

        return Response(
            {
                "session_id": str(session.id),
                "message": "Test soumis avec succès. Le scoring est en cours de traitement.",
                "resultat_url": f"/api/v1/orientation/resultats/?session={session.id}",
            },
            status=status.HTTP_202_ACCEPTED,
        )

# ──────────────────────────────────────────────
# Résultats
# ──────────────────────────────────────────────

class ResultatTestListView(generics.ListAPIView):
    """Liste des résultats de l'utilisateur connecté."""
    serializer_class = ResultatTestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ResultatTest.objects.filter(
            reponse_utilisateur__etudiant=self.request.user,
        ).select_related("reponse_utilisateur__test")

        # Filtre par session spécifique
        session_id = self.request.query_params.get("session")
        if session_id:
            qs = qs.filter(reponse_utilisateur_id=session_id)

        return qs.order_by("-date_calcul")

class ResultatTestDetailView(generics.RetrieveAPIView):
    """Détail d'un résultat."""
    serializer_class = ResultatTestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ResultatTest.objects.filter(
            reponse_utilisateur__etudiant=self.request.user,
        )

# ──────────────────────────────────────────────
# Recommandations
# ──────────────────────────────────────────────

class RecommandationListView(generics.ListAPIView):
    """Liste des recommandations de l'utilisateur."""
    serializer_class = RecommandationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Recommandation.objects.filter(
            etudiant=self.request.user,
        ).select_related("formation", "metier", "etablissement")

        # Filtres
        plan = self.request.query_params.get("plan")
        if plan:
            qs = qs.filter(plan=plan)

        type_entite = self.request.query_params.get("type")
        if type_entite:
            qs = qs.filter(type_entite=type_entite)

        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Marquer comme vues
        ids = [r["id"] for r in response.data.get("results", response.data) if isinstance(r, dict)]
        Recommandation.objects.filter(id__in=ids).update(a_ete_vue=True)
        return response

class RecommandationEngagementView(APIView):
    """Enregistrer une action de l'utilisateur sur une recommandation."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            rec = Recommandation.objects.get(id=pk, etudiant=request.user)
        except Recommandation.DoesNotExist:
            return Response(
                {"error": "Recommandation introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RecommandationEngagementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data["action"]

        if action_type == "vue":
            rec.a_ete_vue = True
        elif action_type == "favorisee":
            rec.a_ete_favorisee = not rec.a_ete_favorisee  # Toggle
        elif action_type == "cliquee":
            rec.a_ete_cliquee = True

        rec.save()

        return Response(RecommandationSerializer(rec).data)

# ──────────────────────────────────────────────
# Historique & Analytics
# ──────────────────────────────────────────────

class HistoriqueTestsView(generics.ListAPIView):
    """Historique des tests passés par l'utilisateur."""
    serializer_class = ReponseUtilisateurSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReponseUtilisateur.objects.filter(
            etudiant=self.request.user,
            statut=StatutTest.TERMINE,
        ).select_related("test")

class EvolutionProfilView(APIView):
    """Évolution du profil RIASEC de l'utilisateur dans le temps."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = OrientationAnalyticsService.stats_etudiant(request.user)
        return Response(stats)

class OrientationStatsView(APIView):
    """Statistiques globales de l'orientation (admin/conseiller)."""
    from rest_framework.permissions import IsAdminUser

    def check_permissions(self, request):
        # Allow admins and counselors (is_staff or has counselor profile)
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return
        profile = getattr(request.user, 'counselor_profile', None)
        if profile:
            return
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied()

    def get(self, request):
        return Response(OrientationAnalyticsService.stats_globales())
