"""
Vues API pour l'app community.
"""
from django.db.models import F
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import (
    Forum, Thread, MessageForum, AbonnementForum,
    ProfilMentor, RelationMentorat, SeanceMentorat,
    ConversationPrivee, MessagePrive,
    Signalement,
)

from .serializers import (
    ForumSerializer, ThreadListSerializer, ThreadDetailSerializer,
    MessageForumSerializer, ThreadCreateSerializer, MessageForumCreateSerializer,
    ProfilMentorSerializer, RelationMentoratSerializer,
    DemandeMentoratSerializer, SeanceMentoratSerializer,
    ConversationPriveeSerializer, MessagePriveSerializer,
    MessagePriveCreateSerializer,
    SignalementSerializer, SignalementCreateSerializer,
)


# ──────────────────────────────────────────────
# Forums
# ──────────────────────────────────────────────

class ForumViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste et détail des forums."""
    serializer_class = ForumSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Forum.objects.filter(is_active=True)

        type_forum = self.request.query_params.get("type")
        if type_forum:
            qs = qs.filter(type=type_forum)

        return qs

    @action(detail=False, methods=["get"])
    def featured(self, request):
        forums = Forum.objects.filter(is_active=True, is_featured=True)
        return Response(ForumSerializer(forums, many=True, context={"request": request}).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def subscribe(self, request, slug=None):
        forum = self.get_object()
        AbonnementForum.objects.get_or_create(
            utilisateur=request.user, forum=forum
        )
        return Response({"message": "Abonnement enregistré."})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unsubscribe(self, request, slug=None):
        forum = self.get_object()
        AbonnementForum.objects.filter(
            utilisateur=request.user, forum=forum
        ).delete()
        return Response({"message": "Désabonnement enregistré."})


class ThreadViewSet(viewsets.ModelViewSet):
    """CRUD des threads (discussions)."""
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Thread.objects.exclude(
            statut__in=["SUPPRIME", "VERROUILLE"]
        ).select_related("auteur", "forum")

        forum_slug = self.request.query_params.get("forum")
        if forum_slug:
            qs = qs.filter(forum__slug=forum_slug)

        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__contains=[tag])

        resolu = self.request.query_params.get("resolu")
        if resolu == "true":
            qs = qs.filter(reponse_solution__isnull=False)
        elif resolu == "false":
            qs = qs.filter(reponse_solution__isnull=True)

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ThreadDetailSerializer
        return ThreadListSerializer

    def create(self, request, *args, **kwargs):
        serializer = ThreadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            forum = Forum.objects.get(id=data["forum_id"])
        except Forum.DoesNotExist:
            return Response(
                {"error": "Forum introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from django.utils.text import slugify
        thread = Thread.objects.create(
            forum=forum,
            auteur=request.user,
            titre=data["titre"],
            contenu=data["contenu"],
            tags=data.get("tags", []),
        )

        return Response(
            ThreadDetailSerializer(thread).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        """Incrémenter le compteur de vues."""
        instance = self.get_object()
        Thread.objects.filter(pk=instance.pk).update(
            nombre_vues=F("nombre_vues") + 1
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reply(self, request, slug=None):
        """Répondre à un thread."""
        thread = self.get_object()

        if thread.is_ferme:
            return Response(
                {"error": "Ce thread est fermé aux nouvelles réponses."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MessageForumCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        reponse_a = None
        if data.get("reponse_a_id"):
            try:
                reponse_a = MessageForum.objects.get(id=data["reponse_a_id"])
            except MessageForum.DoesNotExist:
                pass

        message = MessageForum.objects.create(
            thread=thread,
            auteur=request.user,
            contenu=data["contenu"],
            reponse_a=reponse_a,
        )

        # Mettre à jour le thread
        Thread.objects.filter(pk=thread.pk).update(
            nombre_reponses=F("nombre_reponses") + 1,
            dernier_message=message,
            dernier_message_at=message.created_at,
        )

        return Response(
            MessageForumSerializer(message, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def messages(self, request, slug=None):
        """Liste des messages d'un thread."""
        thread = self.get_object()
        messages = MessageForum.objects.filter(
            thread=thread, is_supprime=False
        ).select_related("auteur")
        return Response(
            MessageForumSerializer(messages, many=True, context={"request": request}).data
        )


class MessageForumLikeView(APIView):
    """Liker / unliker un message de forum."""
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        try:
            message = MessageForum.objects.get(id=message_id)
        except MessageForum.DoesNotExist:
            return Response(
                {"error": "Message introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from apps.community.models import LikeMessageForum
        like, created = LikeMessageForum.objects.get_or_create(
            utilisateur=request.user,
            message=message,
        )

        if created:
            MessageForum.objects.filter(pk=message.pk).update(
                nombre_likes=F("nombre_likes") + 1
            )
            return Response({"liked": True, "nombre_likes": message.nombre_likes + 1})
        else:
            like.delete()
            MessageForum.objects.filter(pk=message.pk).update(
                nombre_likes=F("nombre_likes") - 1
            )
            return Response({"liked": False, "nombre_likes": max(0, message.nombre_likes - 1)})


# ──────────────────────────────────────────────
# Mentorat
# ──────────────────────────────────────────────

class MentorViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste et détail des profils mentors."""
    serializer_class = ProfilMentorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = ProfilMentor.objects.filter(is_disponible=True)

        type_mentor = self.request.query_params.get("type")
        if type_mentor:
            qs = qs.filter(type_mentor=type_mentor)

        domaine = self.request.query_params.get("domaine")
        if domaine:
            qs = qs.filter(domaines_expertise__contains=[domaine])

        return qs

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def demande(self, request, pk=None):
        """Faire une demande de mentorat."""
        mentor = self.get_object()

        if not mentor.peut_accepter_mentore:
            return Response(
                {"error": "Ce mentor n'accepte pas de nouveaux mentorés."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DemandeMentoratSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Vérifier si une relation existe déjà
        if RelationMentorat.objects.filter(
            mentor=mentor,
            mentoré=request.user,
            statut__in=["EN_ATTENTE", "ACCEPTE"],
        ).exists():
            return Response(
                {"error": "Une demande de mentorat existe déjà avec ce mentor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        relation = RelationMentorat.objects.create(
            mentor=mentor,
            mentoré=request.user,
            motif_demande=data.get("motif", ""),
            objectifs=data.get("objectifs", []),
        )

        return Response(
            RelationMentoratSerializer(relation).data,
            status=status.HTTP_201_CREATED,
        )


class MentoratViewSet(viewsets.ModelViewSet):
    """Gestion des relations de mentorat."""
    serializer_class = RelationMentoratSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        user = self.request.user
        return RelationMentorat.objects.filter(
            models.Q(mentor__utilisateur=user) | models.Q(mentoré=user)
        ) if hasattr(self, 'request') else RelationMentorat.objects.none()

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        return RelationMentorat.objects.filter(
            Q(mentor__utilisateur=user) | Q(mentoré=user)
        )


# ──────────────────────────────────────────────
# Messagerie Privée
# ──────────────────────────────────────────────

class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste des conversations privées."""
    serializer_class = ConversationPriveeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConversationPrivee.objects.filter(
            participants=self.request.user
        ).order_by("-dernier_message_at")


class ConversationCreateView(APIView):
    """Créer une conversation privée."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        destinataire_id = request.data.get("destinataire_id")
        if not destinataire_id:
            return Response(
                {"error": "destinataire_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            destinataire = User.objects.get(id=destinataire_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Vérifier si une conversation à 2 existe déjà
        from apps.community.models import ParticipantConversation
        conversations_communes = ConversationPrivee.objects.filter(
            participants=request.user,
            is_groupe=False,
        ).filter(participants=destinataire)

        if conversations_communes.exists():
            conv = conversations_communes.first()
        else:
            conv = ConversationPrivee.objects.create(is_groupe=False)
            conv.participants.add(request.user, destinataire)

        return Response(
            ConversationPriveeSerializer(conv, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class MessagePriveViewSet(viewsets.ModelViewSet):
    """CRUD des messages privés."""
    serializer_class = MessagePriveSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        conversation_id = self.request.query_params.get("conversation_id")
        if conversation_id:
            return MessagePrive.objects.filter(
                conversation_id=conversation_id,
                conversation__participants=self.request.user,
                is_supprime=False,
            ).order_by("created_at")
        return MessagePrive.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = MessagePriveCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            conversation = ConversationPrivee.objects.get(
                id=data["conversation_id"],
                participants=request.user,
            )
        except ConversationPrivee.DoesNotExist:
            return Response(
                {"error": "Conversation introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from django.utils import timezone
        message = MessagePrive.objects.create(
            conversation=conversation,
            auteur=request.user,
            contenu=data["contenu"],
            type_contenu=data.get("type_contenu", "TEXTE"),
        )

        # Mettre à jour la conversation
        ConversationPrivee.objects.filter(pk=conversation.pk).update(
            dernier_message=message,
            dernier_message_at=message.created_at,
        )

        return Response(
            MessagePriveSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )


# ──────────────────────────────────────────────
# Signalements
# ──────────────────────────────────────────────

class SignalementViewSet(viewsets.ModelViewSet):
    """Gestion des signalements."""
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return Signalement.objects.filter(auteur=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return SignalementCreateSerializer
        return SignalementSerializer

    def create(self, request, *args, **kwargs):
        serializer = SignalementCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        signalement = Signalement.objects.create(
            auteur=request.user,
            type_contenu=data["type_contenu"],
            contenu_id=data["contenu_id"],
            type=data["type"],
            description=data.get("description", ""),
        )

        return Response(
            SignalementSerializer(signalement).data,
            status=status.HTTP_201_CREATED,
        )


class BlocageView(APIView):
    """Gérer les blocages d'utilisateurs."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Bloquer un utilisateur."""
        from apps.community.models import BlocageUtilisateur, NiveauBlocage
        from django.contrib.auth import get_user_model
        User = get_user_model()

        bloque_id = request.data.get("user_id")
        if not bloque_id:
            return Response(
                {"error": "user_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            bloque = User.objects.get(id=bloque_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        blocage, created = BlocageUtilisateur.objects.get_or_create(
            bloqueur=request.user,
            bloque=bloque,
            defaults={"niveau": NiveauBlocage.BLOQUER_CONTACT},
        )

        if created:
            return Response(
                {"message": f"{bloque.get_full_name()} a été bloqué."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "Cet utilisateur est déjà bloqué."},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        """Débloquer un utilisateur."""
        from apps.community.models import BlocageUtilisateur
        bloque_id = request.data.get("user_id")
        if not bloque_id:
            return Response(
                {"error": "user_id requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        BlocageUtilisateur.objects.filter(
            bloqueur=request.user,
            bloque_id=bloque_id,
        ).delete()

        return Response({"message": "Utilisateur débloqué."})
