"""Vues API Marketing & CRM pour les Établissements."""
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.accounts.api.permissions import IsSchoolRep
from apps.catalog.models import Etablissement, Formation
from apps.marketing.models import (
    SegmentCandidats, CampagneMarketing, LeadQualifie,
    CandidatureCRM, LogInteractionCRM, TypeInteraction,
    StatutCandidatureCRM, StatutLead, StatutCampagne,
)
from apps.marketing.services import MarketingService, CRMService


# ─── Serializers ───

class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SegmentCandidats
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CampagneSerializer(serializers.ModelSerializer):
    etablissement_nom = serializers.CharField(source="etablissement.nom", read_only=True)
    is_active_now = serializers.BooleanField(read_only=True)

    class Meta:
        model = CampagneMarketing
        fields = "__all__"
        read_only_fields = ("id", "vues", "clics", "leads_generes", "conversions",
                            "created_at", "updated_at")


class LeadSerializer(serializers.ModelSerializer):
    candidat_email = serializers.CharField(source="candidat.email", read_only=True)
    candidat_nom = serializers.SerializerMethodField()
    campagne_nom = serializers.CharField(source="campagne.nom", read_only=True)

    class Meta:
        model = LeadQualifie
        fields = "__all__"

    def get_candidat_nom(self, obj):
        return f"{obj.candidat.first_name} {obj.candidat.last_name}"


class CandidatureCRMSerializer(serializers.ModelSerializer):
    candidat_email = serializers.CharField(source="candidat.email", read_only=True)
    candidat_nom = serializers.SerializerMethodField()
    formation_nom = serializers.CharField(source="formation.nom", read_only=True, default="")
    etablissement_nom = serializers.CharField(source="etablissement.nom", read_only=True)

    class Meta:
        model = CandidatureCRM
        fields = "__all__"
        read_only_fields = ("id", "date_reception", "date_decision", "date_inscription",
                            "is_synced_external", "last_sync_at", "external_application_id")

    def get_candidat_nom(self, obj):
        return f"{obj.candidat.first_name} {obj.candidat.last_name}"


# ─── Vues Segments ───

class SegmentListCreateView(generics.ListCreateAPIView):
    """Liste et crée des segments de ciblage."""
    serializer_class = SegmentSerializer
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def get_queryset(self):
        return SegmentCandidats.objects.all().order_by("-created_at")


class SegmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SegmentSerializer
    permission_classes = [IsAuthenticated, IsSchoolRep]
    queryset = SegmentCandidats.objects.all()


# ─── Vues Campagnes ───

class CampagneListCreateView(generics.ListCreateAPIView):
    """Liste et crée des campagnes marketing."""
    serializer_class = CampagneSerializer
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def get_queryset(self):
        qs = CampagneMarketing.objects.all()
        etablissement_id = self.request.query_params.get("etablissement")
        if etablissement_id:
            qs = qs.filter(etablissement_id=etablissement_id)
        return qs.order_by("-date_debut")


class CampagneDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CampagneSerializer
    permission_classes = [IsAuthenticated, IsSchoolRep]
    queryset = CampagneMarketing.objects.all()


class CampagneActiverView(APIView):
    """Active une campagne et génère les leads qualifiés."""
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def post(self, request, pk):
        campagne = get_object_or_404(CampagneMarketing, pk=pk)
        leads_count = MarketingService.activer_campagne(campagne)
        return Response({
            "message": f"Campagne activée. {leads_count} leads qualifiés générés.",
            "leads_generes": leads_count,
        }, status=status.HTTP_200_OK)


class CampagneStatsView(APIView):
    """Statistiques d'une campagne."""
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def get(self, request, pk):
        campagne = get_object_or_404(CampagneMarketing, pk=pk)
        return Response(CRMService.statistiques_campagne(campagne))


# ─── Vues Leads ───

class LeadListView(generics.ListAPIView):
    """Liste les leads d'une campagne."""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def get_queryset(self):
        campagne_id = self.request.query_params.get("campagne")
        qs = LeadQualifie.objects.all()
        if campagne_id:
            qs = qs.filter(campagne_id=campagne_id)
        return qs.order_by("-date_generation")


class LeadFacturerView(APIView):
    """Facture un lead (l'établissement initie un contact)."""
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def post(self, request, pk):
        lead = get_object_or_404(LeadQualifie, pk=pk)
        facture = MarketingService.facturer_lead_si_contact_initie(lead)
        if not facture:
            return Response({"message": "Lead déjà facturé."}, status=status.HTTP_200_OK)
        return Response({
            "message": "Lead facturé avec succès.",
            "montant": int(lead.montant_facture),
            "date_facturation": lead.date_facturation.isoformat(),
        }, status=status.HTTP_200_OK)


# ─── Vues CRM Candidatures ───

class CandidatureCRMListView(generics.ListCreateAPIView):
    """Liste et crée des candidatures dans le CRM établissement."""
    serializer_class = CandidatureCRMSerializer
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def get_queryset(self):
        qs = CandidatureCRM.objects.all()
        etablissement_id = self.request.query_params.get("etablissement")
        statut = self.request.query_params.get("statut")
        if etablissement_id:
            qs = qs.filter(etablissement_id=etablissement_id)
        if statut:
            qs = qs.filter(statut=statut)
        return qs.order_by("-date_reception")


class CandidatureCRMDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CandidatureCRMSerializer
    permission_classes = [IsAuthenticated, IsSchoolRep]
    queryset = CandidatureCRM.objects.all()


class CandidatureCRMActionView(APIView):
    """Actions sur une candidature : accepter / refuser / attendente / inscrire."""
    permission_classes = [IsAuthenticated, IsSchoolRep]

    ACTIONS_VALIDES = {
        "accepter": StatutCandidatureCRM.ACCEPTEE,
        "refuser": StatutCandidatureCRM.REFUSEE,
        "attente": StatutCandidatureCRM.EN_ATTENTE,
        "inscrire": StatutCandidatureCRM.INSCRIT,
        "revue": StatutCandidatureCRM.EN_REVUE,
    }

    def post(self, request, pk, action):
        if action not in self.ACTIONS_VALIDES:
            return Response({"error": "Action invalide."}, status=status.HTTP_400_BAD_REQUEST)
        candidature = get_object_or_404(CandidatureCRM, pk=pk)
        nouveau_statut = self.ACTIONS_VALIDES[action]
        commentaire = request.data.get("commentaire", "")
        motif_refus = request.data.get("motif_refus", "")
        CRMService.changer_statut_candidature(
            candidature, nouveau_statut, request.user,
            commentaire=commentaire, motif_refus=motif_refus,
        )
        return Response(CandidatureCRMSerializer(candidature).data)


class PipelineStatsView(APIView):
    """Statistiques du pipeline de candidatures d'un établissement."""
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def get(self, request):
        etablissement_id = request.query_params.get("etablissement")
        if not etablissement_id:
            return Response({"error": "Paramètre 'etablissement' requis."}, status=400)
        etablissement = get_object_or_404(Etablissement, pk=etablissement_id)
        return Response(CRMService.statistiques_pipeline(etablissement))


class SyncExterneView(APIView):
    """Synchronise une candidature avec le système externe de l'établissement."""
    permission_classes = [IsAuthenticated, IsSchoolRep]

    def post(self, request, pk):
        candidature = get_object_or_404(CandidatureCRM, pk=pk)
        success = CRMService.synchroniser_externe(candidature)
        return Response({"synced": success, "last_sync_at": candidature.last_sync_at.isoformat()})
