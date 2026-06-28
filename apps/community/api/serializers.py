"""
Serializers DRF pour l'API community.
"""
from rest_framework import serializers

from apps.community.models import (
    Forum, Thread, MessageForum, AbonnementForum,
    ProfilMentor, RelationMentorat, SeanceMentorat,
    ConversationPrivee, MessagePrive,
    Signalement, BlocageUtilisateur,
    ParticipantConversation,
)


# ──────────────────────────────────────────────
# Forums
# ──────────────────────────────────────────────

class ForumSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    is_abonne = serializers.SerializerMethodField()

    class Meta:
        model = Forum
        fields = [
            "id", "nom", "slug", "description", "icone", "couleur",
            "type", "type_display", "regles", "acces_restreint",
            "nombre_threads", "nombre_messages", "nombre_abonnes",
            "dernier_message_at", "is_featured", "is_abonne",
        ]

    def get_is_abonne(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return AbonnementForum.objects.filter(
            utilisateur=request.user, forum=obj
        ).exists()


class ThreadListSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    est_resolu = serializers.BooleanField(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "id", "titre", "slug", "forum",
            "auteur",
            "tags", "statut", "statut_display",
            "is_epingle", "is_ferme", "est_resolu",
            "nombre_reponses", "nombre_vues",
            "dernier_message_at",
            "created_at",
        ]


class ThreadDetailSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    est_resolu = serializers.BooleanField(read_only=True)
    forum_nom = serializers.CharField(source="forum.nom", read_only=True)
    solution_detail = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            "id", "titre", "slug", "contenu",
            "forum", "forum_nom",
            "auteur",
            "tags", "statut", "statut_display",
            "is_epingle", "is_ferme", "est_resolu",
            "nombre_reponses", "nombre_vues", "nombre_signalements",
            "dernier_message_at", "solution_detail",
            "created_at", "updated_at",
        ]

    def get_solution_detail(self, obj):
        if obj.reponse_solution:
            return {
                "id": str(obj.reponse_solution.id),
                "contenu": obj.reponse_solution.contenu[:200],
            }
        return None


class MessageForumSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = MessageForum
        fields = [
            "id", "thread", "auteur",
            "contenu", "type", "type_display",
            "reponse_a",
            "pieces_jointes",
            "nombre_likes", "nombre_signalements",
            "is_solution", "is_edite", "is_supprime",
            "is_liked", "created_at", "edited_at",
        ]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(utilisateur=request.user).exists()


class ThreadCreateSerializer(serializers.Serializer):
    forum_id = serializers.UUIDField()
    titre = serializers.CharField(max_length=255)
    contenu = serializers.CharField()
    tags = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )


class MessageForumCreateSerializer(serializers.Serializer):
    contenu = serializers.CharField()
    reponse_a_id = serializers.UUIDField(required=False, allow_null=True)


# ──────────────────────────────────────────────
# Mentorat
# ──────────────────────────────────────────────

class ProfilMentorSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_mentor_display", read_only=True)
    places_disponibles = serializers.IntegerField(read_only=True)
    peut_accepter = serializers.BooleanField(source="peut_accepter_mentore", read_only=True)

    class Meta:
        model = ProfilMentor
        fields = [
            "id", "utilisateur",
            "type_mentor", "type_display",
            "bio", "domaines_expertise", "competences",
            "annees_experience", "diplomes",
            "is_disponible", "places_disponibles", "peut_accepter",
            "creneaux_disponibles", "formats_proposes", "langues_parlees",
            "nombre_mentores_actuels", "nombre_mentores_total",
            "note_moyenne", "nombre_evaluations",
            "is_verifie",
        ]


class RelationMentoratSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    duree_jours = serializers.IntegerField(read_only=True)

    class Meta:
        model = RelationMentorat
        fields = [
            "id", "mentor",
            "mentoré",
            "statut", "statut_display",
            "motif_demande", "objectifs",
            "date_demande", "date_reponse", "date_debut", "date_fin",
            "nombre_seances", "derniere_seance",
            "duree_jours",
            "evaluation_mentore", "evaluation_mentor",
        ]


class DemandeMentoratSerializer(serializers.Serializer):
    mentor_id = serializers.UUIDField()
    motif = serializers.CharField(required=False, allow_blank=True)
    objectifs = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )


class SeanceMentoratSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeanceMentorat
        fields = [
            "id", "relation", "titre", "description",
            "date_prevue", "duree_minutes", "format",
            "lien_visio", "statut",
            "compte_rendu", "prochaines_etapes",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Messagerie
# ──────────────────────────────────────────────

class MessagePriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagePrive
        fields = [
            "id", "conversation", "auteur",
            "contenu", "type_contenu", "fichier_joint",
            "statut", "is_edite", "is_supprime",
            "reponse_a", "created_at", "edited_at", "lu_at",
        ]


class ConversationPriveeSerializer(serializers.ModelSerializer):
    dernier_message_detail = MessagePriveSerializer(
        source="dernier_message", read_only=True, default=None
    )
    nombre_non_lus = serializers.SerializerMethodField()

    class Meta:
        model = ConversationPrivee
        fields = [
            "id", "titre", "is_groupe",
            "dernier_message", "dernier_message_detail",
            "dernier_message_at",
            "nombre_non_lus",
            "created_at",
        ]

    def get_nombre_non_lus(self, obj):
        request = self.context.get("request")
        if not request:
            return 0
        try:
            participant = ParticipantConversation.objects.get(
                conversation=obj, utilisateur=request.user
            )
            return participant.nombre_non_lus
        except ParticipantConversation.DoesNotExist:
            return 0


class MessagePriveCreateSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField()
    contenu = serializers.CharField()
    type_contenu = serializers.ChoiceField(
        choices=["TEXTE", "IMAGE", "FICHIER"],
        default="TEXTE",
    )


# ──────────────────────────────────────────────
# Modération
# ──────────────────────────────────────────────

class SignalementSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)

    class Meta:
        model = Signalement
        fields = [
            "id", "auteur",
            "type_contenu", "contenu_id", "contenu_resume",
            "type", "type_display", "description",
            "statut", "statut_display",
            "traite_par", "date_traitement", "decision", "action_prise",
            "created_at",
        ]


class SignalementCreateSerializer(serializers.Serializer):
    type_contenu = serializers.ChoiceField(
        choices=["MESSAGE_FORUM", "THREAD", "MESSAGE_PRIVE", "UTILISATEUR", "MENTOR"]
    )
    contenu_id = serializers.UUIDField()
    type = serializers.ChoiceField(
        choices=["SPAM", "HARCELEMENT", "INAPPROPRIE", "DESINFORMATION", "USURPATION", "AUTRE"]
    )
    description = serializers.CharField(required=False, allow_blank=True)
