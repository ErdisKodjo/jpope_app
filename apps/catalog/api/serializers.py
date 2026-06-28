"""
Serializers DRF pour l'API catalog.
"""
from rest_framework import serializers

from apps.catalog.models import Domaine, Metier, Etablissement, Formation

# ──────────────────────────────────────────────
# Domaine
# ──────────────────────────────────────────────

class DomaineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domaine
        fields = [
            "id",
            "nom",
            "slug",
            "description",
            "icon",
            "couleur",
            "nombre_formations",
            "nombre_metiers",
        ]


class DomaineDetailSerializer(serializers.ModelSerializer):
    metiers_populaires = serializers.SerializerMethodField()

    class Meta:
        model = Domaine
        fields = [
            "id",
            "nom",
            "slug",
            "description",
            "icon",
            "couleur",
            "nombre_formations",
            "nombre_metiers",
            "metiers_populaires",
        ]

    def get_metiers_populaires(self, obj):
        top_metiers = obj.metiers.filter(is_active=True).order_by(
            "-score_attractivite"
        )[:5]
        return MetierListSerializer(top_metiers, many=True).data


# ──────────────────────────────────────────────
# Métier
# ──────────────────────────────────────────────

class MetierListSerializer(serializers.ModelSerializer):
    domaine_nom = serializers.CharField(source="domaine.nom", read_only=True)
    revenu_moyen_formate = serializers.CharField(read_only=True)
    fourchette_revenu = serializers.CharField(read_only=True)
    demande_display = serializers.CharField(
        source="get_demande_marche_display",
        read_only=True,
    )

    class Meta:
        model = Metier
        fields = [
            "id",
            "nom",
            "slug",
            "description_courte",
            "domaine_nom",
            "revenu_moyen",
            "revenu_moyen_formate",
            "fourchette_revenu",
            "taux_emploi",
            "demande_marche",
            "demande_display",
            "niveau_etude_requis",
            "score_attractivite",
        ]


class MetierDetailSerializer(serializers.ModelSerializer):
    domaine = DomaineSerializer(read_only=True)
    revenu_moyen_formate = serializers.CharField(read_only=True)
    fourchette_revenu = serializers.CharField(read_only=True)
    demande_display = serializers.CharField(
        source="get_demande_marche_display",
        read_only=True,
    )
    niveau_display = serializers.CharField(
        source="get_niveau_etude_requis_display",
        read_only=True,
    )
    formations_acces_count = serializers.SerializerMethodField()

    class Meta:
        model = Metier
        fields = [
            "id",
            "nom",
            "slug",
            "description",
            "description_courte",
            "domaine",
            "revenu_min",
            "revenu_max",
            "revenu_moyen",
            "revenu_moyen_formate",
            "fourchette_revenu",
            "taux_emploi",
            "demande_marche",
            "demande_display",
            "niveau_etude_requis",
            "niveau_display",
            "duree_formation_typique_annees",
            "competences_cles",
            "taches_principales",
            "perspectives_evolution",
            "pays_concernes",
            "villes_principales",
            "score_attractivite",
            "source_donnees",
            "date_mise_a_jour",
            "formations_acces_count",
        ]

    def get_formations_acces_count(self, obj):
        return obj.formations_acces.filter(is_active=True).count()


# ──────────────────────────────────────────────
# Établissement
# ──────────────────────────────────────────────

class EtablissementListSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source="get_type_display",
        read_only=True,
    )
    statut_display = serializers.CharField(
        source="get_statut_display",
        read_only=True,
    )
    fourchette_frais = serializers.CharField(read_only=True)
    nombre_formations = serializers.SerializerMethodField()

    class Meta:
        model = Etablissement
        fields = [
            "id",
            "nom",
            "slug",
            "sigle",
            "description_courte",
            "logo",
            "type",
            "type_display",
            "statut",
            "statut_display",
            "ville",
            "pays",
            "note_globale",
            "nombre_avis",
            "classement_national",
            "score_qualite_global",
            "frais_scolarite_annuel_min",
            "frais_scolarite_annuel_max",
            "fourchette_frais",
            "propose_bourses",
            "is_verified",
            "is_featured",
            "nombre_formations",
        ]

    def get_nombre_formations(self, obj):
        return obj.formations.filter(is_active=True).count()


class EtablissementDetailSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    fourchette_frais = serializers.CharField(read_only=True)
    ratio_enseignant_formate = serializers.CharField(read_only=True)
    domaines_enseignes = DomaineSerializer(many=True, read_only=True)
    nombre_formations = serializers.SerializerMethodField()

    class Meta:
        model = Etablissement
        fields = [
            "id",
            "nom",
            "slug",
            "sigle",
            "description",
            "description_courte",
            "logo",
            "banniere",
            "type",
            "type_display",
            "statut",
            "statut_display",
            "date_creation",
            "adresse",
            "ville",
            "pays",
            "latitude",
            "longitude",
            "site_web",
            "email",
            "telephone",
            "facebook",
            "linkedin",
            "frais_inscription_min",
            "frais_inscription_max",
            "frais_scolarite_annuel_min",
            "frais_scolarite_annuel_max",
            "fourchette_frais",
            "nombre_etudiants",
            "nombre_enseignants",
            "taux_encadrement",
            "ratio_enseignant_formate",
            "taux_reussite",
            "taux_insertion_professionnelle",
            "note_globale",
            "nombre_avis",
            "classement_national",
            "classement_regional",
            "score_qualite_global",
            "equipements",
            "labels_qualite",
            "domaines_enseignes",
            "propose_bourses",
            "montant_bourse_max",
            "criteres_bourses",
            "residences_universitaires",
            "clubs_et_associations",
            "sports_proposes",
            "is_verified",
            "is_featured",
            "nombre_formations",
        ]

    def get_nombre_formations(self, obj):
        return obj.formations.filter(is_active=True).count()


class EtablissementClassementSerializer(serializers.ModelSerializer):
    """Serializer spécifique pour le classement."""
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Etablissement
        fields = [
            "id",
            "nom",
            "sigle",
            "ville",
            "type",
            "type_display",
            "classement_national",
            "score_qualite_global",
            "note_globale",
            "logo",
        ]


# ──────────────────────────────────────────────
# Formation
# ──────────────────────────────────────────────

class FormationListSerializer(serializers.ModelSerializer):
    etablissement_nom = serializers.CharField(
        source="etablissement.nom",
        read_only=True,
    )
    etablissement_sigle = serializers.CharField(
        source="etablissement.sigle",
        read_only=True,
    )
    domaine_nom = serializers.CharField(source="domaine.nom", read_only=True)
    niveau_display = serializers.CharField(
        source="get_niveau_display",
        read_only=True,
    )
    cout_total_formate = serializers.CharField(read_only=True)
    importance_display = serializers.CharField(
        source="get_importance_strategique_display",
        read_only=True,
    )

    class Meta:
        model = Formation
        fields = [
            "id",
            "nom",
            "slug",
            "description_courte",
            "etablissement_nom",
            "etablissement_sigle",
            "domaine_nom",
            "niveau",
            "niveau_display",
            "duree_annees",
            "modalite",
            "cout_annuel",
            "cout_total_formate",
            "importance_strategique",
            "importance_display",
            "score_qualite",
            "taux_reussite",
            "taux_insertion_12mois",
            "bourses_disponibles",
            "date_limite_inscription",
            "is_featured",
        ]


class FormationDetailSerializer(serializers.ModelSerializer):
    etablissement = EtablissementListSerializer(read_only=True)
    domaine = DomaineSerializer(read_only=True)
    debouches = MetierListSerializer(many=True, read_only=True)
    niveau_display = serializers.CharField(
        source="get_niveau_display",
        read_only=True,
    )
    importance_display = serializers.CharField(
        source="get_importance_strategique_display",
        read_only=True,
    )
    modalite_display = serializers.CharField(
        source="get_modalite_display",
        read_only=True,
    )
    cout_total = serializers.IntegerField(read_only=True)
    cout_total_formate = serializers.CharField(read_only=True)
    retour_sur_investissement_annees = serializers.FloatField(read_only=True)

    class Meta:
        model = Formation
        fields = [
            "id",
            "nom",
            "slug",
            "description",
            "description_courte",
            "etablissement",
            "domaine",
            "niveau",
            "niveau_display",
            "duree_annees",
            "modalite",
            "modalite_display",
            "cout_annuel",
            "frais_inscription",
            "frais_dossier",
            "cout_total",
            "cout_total_formate",
            "bourses_disponibles",
            "montant_bourse_max",
            "facilites_paiement",
            "importance_strategique",
            "importance_display",
            "taux_reussite",
            "taux_insertion_6mois",
            "taux_insertion_12mois",
            "salaire_sortie_moyen",
            "score_qualite",
            "prerequis",
            "serie_bac_admises",
            "programmes",
            "dates_rentree",
            "date_limite_inscription",
            "places_disponibles",
            "debouches",
            "is_featured",
            "retour_sur_investissement_annees",
        ]
