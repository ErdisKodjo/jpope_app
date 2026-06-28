"""
Service catalogue — logique métier transversale.
"""
from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.catalog.models import Domaine, Etablissement, Formation, Metier


class CatalogService:
    """Service pour les opérations catalogue."""

    @staticmethod
    def get_stats_globales() -> dict:
        """Statistiques globales du catalogue."""
        return {
            "nombre_etablissements": Etablissement.objects.filter(is_active=True).count(),
            "nombre_formations": Formation.objects.filter(is_active=True).count(),
            "nombre_metiers": Metier.objects.filter(is_active=True).count(),
            "nombre_domaines": Domaine.objects.filter(is_active=True).count(),
            "etablissements_verifies": Etablissement.objects.filter(
                is_verified=True, is_active=True
            ).count(),
            "formations_inscriptions_ouvertes": Formation.objects.filter(
                is_active=True,
                date_limite_inscription__gte=timezone.now().date(),
            ).count(),
        }

    @staticmethod
    def get_domaines_populaires(limit: int = 10) -> list:
        """Retourne les domaines les plus populaires (par nombre de formations)."""
        return list(
            Domaine.objects.filter(is_active=True)
            .annotate(
                nb_formations=Count("formations", filter=Q(formations__is_active=True)),
                nb_metiers=Count("metiers", filter=Q(metiers__is_active=True)),
            )
            .order_by("-nb_formations")[:limit]
        )

    @staticmethod
    def get_metiers_porteurs(limit: int = 15) -> list:
        """Retourne les métiers les plus porteurs (forte demande + bon revenu)."""
        return list(
            Metier.objects.filter(is_active=True)
            .filter(demande_marche__in=["TRES_FORTE", "FORTE"])
            .order_by("-score_attractivite")[:limit]
        )

    @staticmethod
    def get_formations_meilleur_rapport_qualite_prix(limit: int = 20) -> list:
        """
        Formations avec le meilleur rapport qualité/prix.
        Score = score_qualite / log(cout_annuel + 1)
        """
        formations = Formation.objects.filter(is_active=True, cout_annuel__gt=0)

        def ratio(f):
            import math
            return f.score_qualite / math.log(float(f.cout_annuel) + 1)

        formations_list = list(formations)
        formations_list.sort(key=ratio, reverse=True)
        return formations_list[:limit]

    @staticmethod
    def comparer_etablissements(etab_ids: list) -> dict:
        """
        Compare jusqu'à 3 établissements sur les critères clés.
        """
        if len(etab_ids) > 3:
            raise ValueError("Maximum 3 établissements à comparer")

        etablissements = Etablissement.objects.filter(id__in=etab_ids, is_active=True)

        if len(etablissements) != len(etab_ids):
            raise ValueError("Un ou plusieurs établissements introuvables")

        comparaison = {
            "criteres": [
                "Note globale",
                "Score qualité",
                "Taux de réussite",
                "Taux d'insertion",
                "Frais annuels (max)",
                "Nombre d'étudiants",
                "Ratio encadrement",
                "Bourses disponibles",
                "Classement national",
            ],
            "etablissements": [],
        }

        for etab in etablissements:
            comparaison["etablissements"].append({
                "id": str(etab.id),
                "nom": str(etab),
                "ville": etab.ville,
                "type": etab.get_type_display(),
                "valeurs": [
                    float(etab.note_globale),
                    etab.score_qualite_global,
                    etab.taux_reussite,
                    etab.taux_insertion_professionnelle,
                    int(etab.frais_scolarite_annuel_max),
                    etab.nombre_etudiants,
                    etab.taux_encadrement,
                    etab.propose_bourses,
                    etab.classement_national,
                ],
            })

        return comparaison

    @staticmethod
    def comparer_formations(formation_ids: list) -> dict:
        """Compare jusqu'à 3 formations."""
        if len(formation_ids) > 3:
            raise ValueError("Maximum 3 formations à comparer")

        formations = Formation.objects.filter(
            id__in=formation_ids, is_active=True
        ).select_related("etablissement", "domaine")

        comparaison = {
            "criteres": [
                "Établissement",
                "Domaine",
                "Niveau",
                "Durée (années)",
                "Coût annuel (FCFA)",
                "Coût total (FCFA)",
                "Taux de réussite",
                "Taux d'insertion 12 mois",
                "Salaire sortie moyen",
                "Score qualité",
                "Importance stratégique",
                "Bourses disponibles",
                "Retour sur investissement (années)",
            ],
            "formations": [],
        }

        for f in formations:
            comparaison["formations"].append({
                "id": str(f.id),
                "nom": f.nom,
                "valeurs": [
                    str(f.etablissement),
                    f.domaine.nom,
                    f.get_niveau_display(),
                    f.duree_annees,
                    int(f.cout_annuel),
                    f.cout_total,
                    f.taux_reussite,
                    f.taux_insertion_12mois,
                    int(f.salaire_sortie_moyen),
                    f.score_qualite,
                    f.get_importance_strategique_display(),
                    f.bourses_disponibles,
                    f.retour_sur_investissement_annees,
                ],
            })

        return comparaison

    @staticmethod
    def simuler_cout_formation(
        formation_id: str,
        annees: int = None,
        mode_vie_mensuel: int = 50000,
        bourse_montant: int = 0,
    ) -> dict:
        """
        Simule le coût total d'une formation sur sa durée.

        Args:
            formation_id: UUID de la formation
            annees: nombre d'années (par défaut = durée de la formation)
            mode_vie_mensuel: budget vie (logement, nourriture, transport)
            bourse_montant: montant annuel de bourse
        """
        try:
            formation = Formation.objects.get(id=formation_id, is_active=True)
        except Formation.DoesNotExist:
            raise ValueError("Formation introuvable")

        duree = annees or formation.duree_annees

        # Calculs
        frais_inscription = int(formation.frais_inscription)
        frais_dossier = int(formation.frais_dossier)
        scolarite_totale = int(formation.cout_annuel * duree)
        vie_totale = mode_vie_mensuel * 12 * duree
        bourse_totale = bourse_montant * duree

        cout_total = (
            frais_inscription +
            frais_dossier +
            scolarite_totale +
            vie_totale -
            bourse_totale
        )

        return {
            "formation": formation.nom,
            "etablissement": str(formation.etablissement),
            "duree_annees": duree,
            "detail": {
                "frais_inscription": frais_inscription,
                "frais_dossier": frais_dossier,
                "scolarite_totale": scolarite_totale,
                "scolarite_annuelle": int(formation.cout_annuel),
                "vie_etudiante_totale": vie_totale,
                "vie_etudiante_mensuelle": mode_vie_mensuel,
                "bourse_totale": bourse_totale,
                "bourse_annuelle": bourse_montant,
            },
            "cout_total": cout_total,
            "cout_total_formate": f"{cout_total:,} FCFA".replace(",", " "),
            "cout_mensuel_moyen": round(cout_total / (duree * 12)),
            "cout_mensuel_formate": (
                f"{round(cout_total / (duree * 12)):,} FCFA/mois"
            ).replace(",", " "),
        }
