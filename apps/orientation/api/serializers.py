"""
Serializers DRF pour l'API orientation.
"""
from rest_framework import serializers

from apps.orientation.models import (
    TestOrientation,
    Question,
    Choice,
    ReponseUtilisateur,
    DetailReponse,
    ResultatTest,
    Recommandation,
)
from apps.catalog.api.serializers import (
    FormationListSerializer,
    MetierListSerializer,
    EtablissementListSerializer,
)

# ──────────────────────────────────────────────
# Test d'orientation
# ──────────────────────────────────────────────

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "texte", "ordre"]

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    dimension_principale = serializers.CharField(read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "texte",
            "texte_court",
            "explication",
            "image",
            "type",
            "ordre",
            "obligatoire",
            "dimensions",
            "echelle_min",
            "echelle_max",
            "label_min",
            "label_max",
            "contexte",
            "choices",
            "dimension_principale",
        ]

class TestOrientationListSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = TestOrientation
        fields = [
            "id",
            "nom",
            "slug",
            "description_courte",
            "type",
            "type_display",
            "duree_estimee_minutes",
            "nombre_questions",
            "is_featured",
        ]

class TestOrientationDetailSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = TestOrientation
        fields = [
            "id",
            "nom",
            "slug",
            "description",
            "type",
            "type_display",
            "duree_estimee_minutes",
            "nombre_questions",
            "dimensions_evaluees",
            "source_scientifique",
            "is_featured",
            "questions",
        ]

# ──────────────────────────────────────────────
# Passation de test
# ──────────────────────────────────────────────

class DetailReponseSerializer(serializers.Serializer):
    """Serializer pour une réponse individuelle."""
    question_id = serializers.UUIDField()
    choice_id = serializers.UUIDField(required=False, allow_null=True)
    choices_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )
    valeur_echelle = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=5,
    )
    classement = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )
    reponse_ouverte = serializers.CharField(required=False, allow_blank=True)
    temps_reponse_secondes = serializers.IntegerField(default=0)

class SoumettreTestSerializer(serializers.Serializer):
    """Serializer pour soumettre un test complet."""
    test_id = serializers.UUIDField()
    reponses = DetailReponseSerializer(many=True)
    duree_totale_secondes = serializers.IntegerField()
    appareil = serializers.CharField(max_length=50, required=False, default="unknown")

class ReponseUtilisateurSerializer(serializers.ModelSerializer):
    test_nom = serializers.CharField(source="test.nom", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    progression_formatee = serializers.CharField(read_only=True)

    class Meta:
        model = ReponseUtilisateur
        fields = [
            "id",
            "test",
            "test_nom",
            "statut",
            "statut_display",
            "date_debut",
            "date_fin",
            "duree_reelle_secondes",
            "nombre_questions_repondues",
            "nombre_questions_total",
            "progression",
            "progression_formatee",
            "score_global",
            "code_holland",
        ]
        read_only_fields = fields

# ──────────────────────────────────────────────
# Résultats
# ──────────────────────────────────────────────

class ResultatTestSerializer(serializers.ModelSerializer):
    test_nom = serializers.CharField(
        source="reponse_utilisateur.test.nom",
        read_only=True,
    )
    dimension_dominante_nom = serializers.CharField(read_only=True)
    top_3_dimensions = serializers.ListField(read_only=True)

    class Meta:
        model = ResultatTest
        fields = [
            "id",
            "reponse_utilisateur",
            "test_nom",
            "score_global",
            "scores_par_dimension",
            "code_holland",
            "profil_dominant",
            "profil_secondaire",
            "dimension_dominante_nom",
            "interpretation",
            "forces",
            "axes_amelioration",
            "evolution_vs_precedent",
            "top_3_dimensions",
            "date_calcul",
        ]

# ──────────────────────────────────────────────
# Recommandations
# ──────────────────────────────────────────────

class RecommandationSerializer(serializers.ModelSerializer):
    formation_detail = FormationListSerializer(source="formation", read_only=True)
    metier_detail = MetierListSerializer(source="metier", read_only=True)
    etablissement_detail = EtablissementListSerializer(
        source="etablissement", read_only=True
    )
    plan_display = serializers.CharField(source="get_plan_display", read_only=True)
    confiance_display = serializers.CharField(
        source="get_niveau_confiance_display", read_only=True
    )
    entite_nom = serializers.CharField(read_only=True)

    class Meta:
        model = Recommandation
        fields = [
            "id",
            "type_entite",
            "formation",
            "metier",
            "etablissement",
            "formation_detail",
            "metier_detail",
            "etablissement_detail",
            "taux_compatibilite",
            "niveau_confiance",
            "confiance_display",
            "plan",
            "plan_display",
            "ordre",
            "justification",
            "points_forts_match",
            "points_attention",
            "entite_nom",
            "a_ete_vue",
            "a_ete_favorisee",
            "created_at",
        ]

class RecommandationEngagementSerializer(serializers.Serializer):
    """Serializer pour enregistrer l'engagement sur une recommandation."""
    action = serializers.ChoiceField(
        choices=["vue", "favorisee", "cliquee"],
    )
