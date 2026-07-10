"""
Vues API pour le test Ikigai et le rapport combiné RIASEC + Ikigai.

Cahier des charges (section 2.1 — Candidat, Module Tests d'Orientation Combinés) :
"Détails du Test Ikigai : Croisement des quatre piliers fondamentaux"
"Restitution : Génération automatique d'un rapport psychologique et d'orientation complet"
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orientation.models import ResultatTest, TestOrientation, TypeTest
from apps.orientation.services.ikigai_service import (
    IkigaiScoringService,
    CombinedScoringService,
)


class ListeTestsIkigaiView(generics.ListAPIView):
    """Liste les tests Ikigai disponibles (actifs et publics)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tests = TestOrientation.objects.filter(
            is_active=True, is_public=True, type=TypeTest.IKIGAI
        ).values("id", "nom", "slug", "description_courte", "duree_estimee_minutes", "nombre_questions")
        return Response({"tests": list(tests)})


class IkigaiResultatView(APIView):
    """
    Récupère le dernier résultat Ikigai de l'utilisateur courant.
    Si l'utilisateur n'a pas encore passé le test, retourne un 404 avec un message.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dernier = (
            ResultatTest.objects
            .filter(
                reponse_utilisateur__etudiant=request.user,
                reponse_utilisateur__test__type=TypeTest.IKIGAI,
            )
            .order_by("-date_calcul")
            .first()
        )
        if not dernier:
            return Response(
                {
                    "error": "AUCUN_RESULTAT_IKIGAI",
                    "message": "Vous n'avez pas encore passé le test Ikigai.",
                    "tests_disponibles": "/api/v1/orientation/ikigai/tests/",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "id": str(dernier.id),
                "score_global": dernier.score_global,
                "scores_par_dimension": dernier.scores_par_dimension,
                "profil_dominant": dernier.profil_dominant,
                "interpretation": dernier.interpretation,
                "forces": dernier.forces,
                "axes_amelioration": dernier.axes_amelioration,
                "date_calcul": dernier.date_calcul.isoformat() if hasattr(dernier, "date_calcul") else None,
            },
            status=status.HTTP_200_OK,
        )


class RapportCombineView(APIView):
    """
    Génère un rapport d'orientation combiné RIASEC + Ikigai pour l'utilisateur courant.
    Conformément au cahier des charges : "Fusion intelligente et dynamique de plusieurs
    méthodologies d'évaluation pour garantir une pertinence maximale."
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rapport = CombinedScoringService.combiner_resultats(request.user)
        return Response(rapport, status=status.HTTP_200_OK)
