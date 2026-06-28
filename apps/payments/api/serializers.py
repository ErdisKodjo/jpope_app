"""
Serializers DRF pour l'API payments.
"""
from rest_framework import serializers

from apps.payments.models import (
    Paiement, PlanAbonnement, Abonnement, Transaction, Facture,
)


class PlanAbonnementSerializer(serializers.ModelSerializer):
    prix_actuel = serializers.IntegerField(read_only=True)
    frequence_display = serializers.CharField(
        source="get_frequence_display", read_only=True
    )
    niveau_display = serializers.CharField(
        source="get_niveau_display", read_only=True
    )

    class Meta:
        model = PlanAbonnement
        fields = [
            "id", "code", "nom", "description", "description_courte",
            "type_abonnement", "niveau", "niveau_display",
            "frequence", "frequence_display",
            "prix_fcfa", "prix_promo_fcfa", "prix_actuel",
            "periode_essai_jours", "duree_mois",
            "fonctionnalites", "limites", "avantages",
            "icone", "couleur",
            "is_featured",
        ]


class AbonnementSerializer(serializers.ModelSerializer):
    plan_detail = PlanAbonnementSerializer(source="plan", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    est_actif = serializers.BooleanField(read_only=True)
    jours_restants = serializers.IntegerField(read_only=True)

    class Meta:
        model = Abonnement
        fields = [
            "id", "plan", "plan_detail",
            "statut", "statut_display",
            "date_debut", "date_fin", "jours_restants",
            "est_actif",
            "renouvellement_auto",
            "consommation_courante",
            "nombre_renouvellements",
            "created_at",
        ]
        read_only_fields = fields


class PaiementSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    montant_formate = serializers.CharField(read_only=True)
    est_reussi = serializers.BooleanField(read_only=True)

    class Meta:
        model = Paiement
        fields = [
            "id", "reference",
            "montant", "montant_formate", "devise",
            "statut", "statut_display",
            "provider",
            "transaction_id",
            "description",
            "est_reussi",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    montant_formate = serializers.CharField(read_only=True)
    est_reussie = serializers.BooleanField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id", "reference",
            "type", "methode_paiement",
            "montant", "montant_formate",
            "frais_transaction", "montant_net",
            "statut", "statut_display",
            "telephone_payeur", "reference_externe",
            "date_initiation", "date_confirmation",
            "est_reussie",
        ]
        read_only_fields = fields


class FactureSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    montant_ttc_formate = serializers.CharField(read_only=True)
    est_payee = serializers.BooleanField(read_only=True)

    class Meta:
        model = Facture
        fields = [
            "id", "numero",
            "montant_ht", "taux_tva", "montant_tva", "montant_ttc",
            "montant_ttc_formate", "remise",
            "lignes",
            "date_emission", "date_echeance", "date_paiement",
            "statut", "statut_display",
            "est_payee",
            "fichier_pdf",
            "created_at",
        ]
        read_only_fields = fields


class InitierPaiementSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField()
    methode_paiement = serializers.ChoiceField(
        choices=["FLOOZ", "TMONEY", "MOOV_MONEY", "CARTE", "VIREMENT"]
    )
    telephone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Requis pour Mobile Money",
    )
    payment_method_id = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Requis pour carte (Stripe)",
    )

    def validate(self, attrs):
        methode = attrs.get("methode_paiement")
        if methode in ["FLOOZ", "TMONEY", "MOOV_MONEY"]:
            if not attrs.get("telephone"):
                raise serializers.ValidationError(
                    {"telephone": "Le téléphone est requis pour Mobile Money."}
                )
        if methode == "CARTE":
            if not attrs.get("payment_method_id"):
                raise serializers.ValidationError(
                    {"payment_method_id": "payment_method_id requis pour carte."}
                )
        return attrs


class VerifierStatutSerializer(serializers.Serializer):
    reference = serializers.CharField()
