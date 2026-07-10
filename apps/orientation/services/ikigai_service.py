"""
Service Ikigai — implémente le calcul des 4 piliers de l'Ikigai japonais.

L'Ikigai (生き甲斐) est une philosophie japonaise qui vise à trouver sa "raison d'être"
au croisement de 4 cercles :
1. CE QUE J'AIME (Passion) — intérêts, activités qui procurent de la joie
2. CE DONT LE MONDE A BESOIN (Mission) — contribution à la société, valeurs
3. CE POUR QUOI JE PEUX ÊTRE PAYÉ (Vocation) — opportunités économiques, métiers rémunérateurs
4. CE EN QUOI JE SUIS DOUÉ (Profession) — compétences naturelles, talents

Les intersections produisent 4 zones intermédiaires :
- Passion + Profession = Ce qui me passionne ET où j'excelle → SATISFACTION
- Passion + Mission = Ce que j'aime ET dont le monde a besoin → EXCITATION
- Mission + Vocation = Ce dont le monde a besoin ET qui est rémunéré → CONFORT
- Vocation + Profession = Ce qui paye ET où j'excelle → SECURITE

Le centre des 4 = IKIGAI (raison d'être).

Conformément au cahier des charges (section 2.1 — Candidat) :
"Test Ikigai : Croisement des quatre piliers fondamentaux"
"""
import logging
from typing import Dict, List, Tuple
from django.db import transaction
from django.utils import timezone

from apps.orientation.models import (
    ReponseUtilisateur, DetailReponse, ResultatTest,
    StatutTest, TypeQuestion, TypeTest,
)
from apps.orientation.models.enums import PilierIkigai

logger = logging.getLogger(__name__)


# ─── Mots-clés par pilier (matching naïf sur questions ouvertes / choix) ───

MOTS_CLES_PILIERS = {
    PilierIkigai.PASSION: [
        "aime", "passion", "plaisir", "joie", "enthousiasme", "rêve", "loisir",
        "hobby", "kiff", "adorer", "fascination", "engouement",
        # Activités typiquement "passion"
        "musique", "dessin", "sport", "lecture", "écriture", "danse", "cuisine",
        "jeux", "voyage", "photographie", "cinéma", "théâtre",
    ],
    PilierIkigai.MISSION: [
        "aider", "utile", "société", "monde", "contribuer", "impact", "sens",
        "valeur", "engagement", "bénévolat", "humanitaire", "solidarité",
        "écologie", "justice", "égalité", "éducation", "santé", "paix",
        "changements", "transformer", "améliorer", "différence",
    ],
    PilierIkigai.VOCATION: [
        "salaire", "argent", "payé", "rémunération", "carrière", "emploi",
        "travail", "profession", "métier", "business", "entreprise", "gagner",
        "business", "client", "marché", "demande", "secteur", "industrie",
        "opportunité", "stage", "alternance", "recrutement",
    ],
    PilierIkigai.PROFESSION: [
        "doué", "talent", "capacité", "compétence", "fort", "facile",
        "habileté", "expertise", "savoir-faire", "exceller", "performant",
        "naturel", "inné", "don", "aptitude", "maîtrise", "efficace",
        # Compétences typiquement reconnues
        "calcul", "écriture", "oral", "analyse", "organisation", "leadership",
        "créativité", "mémoire", "logique", "résoudre",
    ],
}


class IkigaiScoringService:
    """
    Calcule les scores Ikigai à partir d'un test de type TypeTest.IKIGAI ou TypeTest.MIXTE.

    Deux modes de calcul :
    1. Mode STRUCTURÉ — questions avec dimensions explicitement taggées "PASSION/MISSION/..."
       (utilise la même mécanique que RIASEC : poids × coef × valeur)
    2. Mode TEXTUEL — questions ouvertes analysées par matching de mots-clés
       (méthode de repli, moins précise mais flexible)
    """

    @classmethod
    @transaction.atomic
    def calculer_resultat_ikigai(cls, reponse_id: str) -> ResultatTest:
        """Point d'entrée — calcule le résultat Ikigai pour une session de test terminée."""
        reponse = ReponseUtilisateur.objects.select_related("test", "etudiant").get(id=reponse_id)
        if reponse.statut != StatutTest.TERMINE:
            raise ValueError(f"Le test n'est pas terminé (statut: {reponse.statut})")

        details = (
            DetailReponse.objects
            .filter(reponse_utilisateur=reponse)
            .select_related("question", "choice_selectionne")
        )
        if not details.exists():
            raise ValueError("Aucune réponse trouvée pour cette session")

        # 1. Calcule les scores bruts par pilier
        scores_bruts = cls._calculer_scores_piliers(details)

        # 2. Normalise (0-100)
        scores_normalises = cls._normaliser_piliers(scores_bruts, details)

        # 3. Identifie les intersections (zones intermédiaires)
        intersections = cls._calculer_intersections(scores_normalises)

        # 4. Score global Ikigai — moyenne des 4 piliers + bonus d'équilibre
        score_global = cls._score_global_ikigai(scores_normalises)

        # 5. Détermine le pilier dominant et la zone d'équilibre
        pilier_dominant = max(scores_normalises.items(), key=lambda x: x[1])[0] if scores_normalises else ""

        # 6. Génère l'interprétation
        interpretation = cls._generer_interpretation_ikigai(
            scores_normalises, intersections, reponse.etudiant
        )

        # 7. Identifie les familles de métiers recommandées (intersection au centre = Ikigai)
        metiers_recommandes = cls._recommander_metiers_ikigai(scores_normalises, intersections)

        # 8. Crée ou met à jour le résultat
        resultat, _created = ResultatTest.objects.update_or_create(
            reponse_utilisateur=reponse,
            defaults={
                "score_global": score_global,
                "scores_par_dimension": scores_normalises,
                "code_holland": "",  # Pas de code Holland pour Ikigai
                "profil_dominant": pilier_dominant,
                "profil_secondaire": intersections.get("zone_equilibre", ""),
                "interpretation": interpretation,
                "forces": metiers_recommandes,
                "axes_amelioration": cls._identifier_piliers_faibles(scores_normalises),
                "evolution_vs_precedent": {},
            },
        )

        reponse.score_global = score_global
        reponse.profil_dominant = pilier_dominant
        reponse.scores_par_dimension = scores_normalises
        reponse.save(update_fields=["score_global", "profil_dominant", "scores_par_dimension"])

        logger.info(
            f"Résultat Ikigai calculé pour {reponse.etudiant.email} : "
            f"score={score_global}, pilier_dominant={pilier_dominant}"
        )
        return resultat

    # ──────────────────────────────────────────────
    # Étape 1 — Scores bruts par pilier
    # ──────────────────────────────────────────────

    @classmethod
    def _calculer_scores_piliers(cls, details) -> Dict[str, float]:
        """
        Pour chaque détail de réponse :
        - Si la question a des dimensions taggées (PASSION/MISSION/...), utilise la formule
          poids × coef × valeur (Likert ou choix).
        - Sinon, si la question est ouverte, fait un matching de mots-clés.
        """
        scores: Dict[str, float] = {p: 0.0 for p in PilierIkigai.values}

        for detail in details:
            question = detail.question
            poids = question.poids or 1
            dimensions = question.dimensions or {}

            if dimensions and any(d in PilierIkigai.values for d in dimensions):
                # Mode structuré
                if question.type == TypeQuestion.ECHELLE_LIKERT:
                    valeur = detail.valeur_echelle or 0
                    for dim, coef in dimensions.items():
                        if dim in PilierIkigai.values:
                            scores[dim] += valeur * poids * coef
                elif detail.choice_selectionne:
                    for dim, points in (detail.choice_selectionne.scores or {}).items():
                        if dim in PilierIkigai.values:
                            scores[dim] += points * poids
            elif question.type == TypeQuestion.OUVERTE and detail.texte_reponse:
                # Mode textuel — matching de mots-clés
                text_scores = cls._analyser_texte_ouvert(detail.texte_reponse)
                for dim, score in text_scores.items():
                    scores[dim] += score * poids

        return scores

    @classmethod
    def _analyser_texte_ouvert(cls, texte: str) -> Dict[str, float]:
        """
        Analyse un texte libre et retourne un score par pilier basé sur la fréquence
        de mots-clés. Score normalisé entre 0 et 5 (échelle Likert équivalente).
        """
        texte_lower = texte.lower()
        mots = texte_lower.split()
        if not mots:
            return {p: 0.0 for p in PilierIkigai.values}

        scores = {}
        for pilier, mots_cles in MOTS_CLES_PILIERS.items():
            occurrences = sum(1 for m in mots if any(mc in m for mc in mots_cles))
            # Normalise : 0 mot = 0, 1-2 mots = 2.5, 3-5 mots = 4, 6+ = 5
            if occurrences == 0:
                scores[pilier] = 0.0
            elif occurrences <= 2:
                scores[pilier] = 2.5
            elif occurrences <= 5:
                scores[pilier] = 4.0
            else:
                scores[pilier] = 5.0
        return scores

    # ──────────────────────────────────────────────
    # Étape 2 — Normalisation 0-100
    # ──────────────────────────────────────────────

    @classmethod
    def _normaliser_piliers(cls, scores_bruts: Dict[str, float], details) -> Dict[str, float]:
        if not scores_bruts:
            return {}
        # Maximum théorique : 5 (Likert max) × somme des poids × coef=1
        max_par_pilier = {p: 0.0 for p in PilierIkigai.values}
        for detail in details:
            question = detail.question
            poids = question.poids or 1
            for dim, coef in (question.dimensions or {}).items():
                if dim in PilierIkigai.values:
                    if question.type == TypeQuestion.ECHELLE_LIKERT:
                        max_val = getattr(question, "echelle_max", 5) or 5
                    else:
                        max_val = 5
                    max_par_pilier[dim] += max_val * poids * coef
            # Mode texte : max théorique = 5 × poids
            if question.type == TypeQuestion.OUVERTE:
                for pilier in PilierIkigai.values:
                    max_par_pilier[pilier] += 5 * poids

        return {
            pilier: min(round((score / max(max_par_pilier.get(pilier, 1), 1)) * 100, 1), 100)
            for pilier, score in scores_bruts.items()
            if score > 0 or max_par_pilier.get(pilier, 0) > 0
        }

    # ──────────────────────────────────────────────
    # Étape 3 — Intersections (zones intermédiaires)
    # ──────────────────────────────────────────────

    @classmethod
    def _calculer_intersections(cls, scores: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule les 4 intersections de l'Ikigai + la zone d'équilibre centrale.
        """
        p = scores.get
        return {
            "satisfaction": round((p(PilierIkigai.PASSION, 0) + p(PilierIkigai.PROFESSION, 0)) / 2, 1),
            "excitation": round((p(PilierIkigai.PASSION, 0) + p(PilierIkigai.MISSION, 0)) / 2, 1),
            "confort": round((p(PilierIkigai.MISSION, 0) + p(PilierIkigai.VOCATION, 0)) / 2, 1),
            "securite": round((p(PilierIkigai.VOCATION, 0) + p(PilierIkigai.PROFESSION, 0)) / 2, 1),
            # Zone centrale = moyenne des 4 piliers
            "zone_equilibre": round(
                (p(PilierIkigai.PASSION, 0) + p(PilierIkigai.MISSION, 0)
                 + p(PilierIkigai.VOCATION, 0) + p(PilierIkigai.PROFESSION, 0)) / 4,
                1
            ),
        }

    # ──────────────────────────────────────────────
    # Étape 4 — Score global
    # ──────────────────────────────────────────────

    @classmethod
    def _score_global_ikigai(cls, scores: Dict[str, float]) -> float:
        """
        Le score global Ikigai = moyenne des 4 piliers × facteur d'équilibre.
        Le facteur d'équilibre pénalise les profils déséquilibrés
        (un seul pilier fort, les autres faibles = moins pertinent).
        """
        if not scores:
            return 0.0
        piliers = [scores.get(p, 0) for p in PilierIkigai.values]
        moyenne = sum(piliers) / len(piliers)
        # Écart-type = mesure de déséquilibre
        ecart_type = (sum((p - moyenne) ** 2 for p in piliers) / len(piliers)) ** 0.5
        # Facteur d'équilibre : 1.0 si écart = 0, ~0.5 si écart = 50
        facteur_equilibre = max(0.5, 1.0 - (ecart_type / 100))
        return round(moyenne * facteur_equilibre, 1)

    # ──────────────────────────────────────────────
    # Étape 5 — Interprétation
    # ──────────────────────────────────────────────

    @classmethod
    def _generer_interpretation_ikigai(
        cls, scores: Dict[str, float], intersections: Dict[str, float], etudiant
    ) -> str:
        """Génère un rapport textuel du profil Ikigai."""
        lignes = [f"Rapport Ikigai — {etudiant.get_full_name()}\n"]
        lignes.append("═" * 50 + "\n")

        lignes.append("VOS 4 PILIERS :")
        noms = {
            PilierIkigai.PASSION: "Ce que vous aimez",
            PilierIkigai.MISSION: "Ce dont le monde a besoin",
            PilierIkigai.VOCATION: "Ce pour quoi vous pouvez être payé",
            PilierIkigai.PROFESSION: "Ce en quoi vous êtes doué",
        }
        for pilier in PilierIkigai.values:
            score = scores.get(pilier, 0)
            barre = "█" * int(score / 5) + "░" * (20 - int(score / 5))
            lignes.append(f"  {noms[pilier]:35s} {barre} {score:>5.1f}/100")

        lignes.append("\nZONES D'INTERSECTION :")
        zones = {
            "satisfaction": "Satisfaction (Passion ∩ Profession)",
            "excitation": "Excitation (Passion ∩ Mission)",
            "confort": "Confort (Mission ∩ Vocation)",
            "securite": "Sécurité (Vocation ∩ Profession)",
            "zone_equilibre": "★ IKIGAI — Zone d'équilibre centrale",
        }
        for key, label in zones.items():
            score = intersections.get(key, 0)
            lignes.append(f"  {label:50s} {score:>5.1f}/100")

        # Recommandation
        equilibre = intersections.get("zone_equilibre", 0)
        if equilibre >= 70:
            lignes.append(
                "\n✓ Vous avez un Ikigai clairement identifié ! Vous êtes aligné avec vos passions, "
                "vos talents, les besoins du monde et vos perspectives de carrière. "
                "Poursuivez dans cette direction."
            )
        elif equilibre >= 50:
            lignes.append(
                "\n≈ Votre Ikigai est en émergence. Vous avez des bases solides mais certains "
                "piliers demandent à être renforcés. Identifiez le pilier le plus faible "
                "et explorez des activités pour le développer."
            )
        else:
            pilier_faible = min(scores.items(), key=lambda x: x[1])[0] if scores else None
            if pilier_faible:
                lignes.append(
                    f"\n! Votre Ikigai est encore flou. Le pilier le plus faible est "
                    f"« {noms.get(pilier_faible, pilier_faible)} ». "
                    "Consacrez du temps à l'explorer via des activités, des rencontres "
                    "professionnelles ou des tests pratiques."
                )

        return "\n".join(lignes)

    # ──────────────────────────────────────────────
    # Étape 6 — Recommandation de métiers basée sur l'Ikigai
    # ──────────────────────────────────────────────

    @classmethod
    def _recommander_metiers_ikigai(
        cls, scores: Dict[str, float], intersections: Dict[str, float]
    ) -> List[str]:
        """
        Recommande des familles de métiers en fonction du profil Ikigai.
        Logique simplifiée basée sur le pilier dominant et la zone d'équilibre.
        """
        if not scores:
            return []

        pilier_dominant = max(scores.items(), key=lambda x: x[1])[0]
        recommandations = {
            PilierIkigai.PASSION: [
                "Métiers artistiques et créatifs",
                "Médiation culturelle et animation",
                "Écriture, journalisme, communication",
            ],
            PilierIkigai.MISSION: [
                "Métiers du soin et de l'accompagnement",
                "Éducation et formation",
                "ONG, humanitaire, développement durable",
                "Travail social et psychologie",
            ],
            PilierIkigai.VOCATION: [
                "Commerce et gestion d'entreprise",
                "Finance et consulting",
                "Management et leadership",
                "Entrepreneuriat",
            ],
            PilierIkigai.PROFESSION: [
                "Ingénierie et métiers techniques",
                "Recherche et développement",
                "Data science et informatique",
                "Métiers de précision (chirurgie, architecture)",
            ],
        }

        metiers = list(recommandations.get(pilier_dominant, []))

        # Si la zone d'équilibre est élevée, ajoute des métiers "Ikigai complet"
        if intersections.get("zone_equilibre", 0) >= 65:
            metiers.extend([
                "Métiers de passion avec viabilité économique (artisanat d'art, éducation artistique)",
                "Entrepreneuriat à impact social",
            ])

        return metiers[:8]  # Limite à 8 recommandations

    @classmethod
    def _identifier_piliers_faibles(cls, scores: Dict[str, float]) -> List[str]:
        """Identifie les piliers les plus faibles (< 40)."""
        faibles = []
        noms = {
            PilierIkigai.PASSION: "Explorer ce qui vous passionne vraiment",
            PilierIkigai.MISSION: "Identifier les causes qui vous tiennent à cœur",
            PilierIkigai.VOCATION: "Rechercher les opportunités économiques de vos intérêts",
            PilierIkigai.PROFESSION: "Développer vos talents naturels en compétences",
        }
        for pilier, score in scores.items():
            if score < 40:
                faibles.append(f"{noms.get(pilier, pilier)} ({score}/100)")
        return faibles


# ─── Combinaison RIASEC + Ikigai (cahier des charges : "Fusion intelligente") ───

class CombinedScoringService:
    """
    Combine un résultat RIASEC et un résultat Ikigai pour produire
    un rapport d'orientation unifié (conformément au cahier des charges).
    """

    @classmethod
    def combiner_resultats(cls, etudiant) -> Dict:
        """
        Récupère le dernier résultat RIASEC et le dernier résultat Ikigai de l'étudiant
        et produit un rapport combiné.
        """
        from apps.orientation.models import ResultatTest, TypeTest

        dernier_riasec = (
            ResultatTest.objects
            .filter(reponse_utilisateur__etudiant=etudiant, reponse_utilisateur__test__type=TypeTest.INTERETS)
            .order_by("-date_calcul")
            .first()
        )
        dernier_ikigai = (
            ResultatTest.objects
            .filter(reponse_utilisateur__etudiant=etudiant, reponse_utilisateur__test__type=TypeTest.IKIGAI)
            .order_by("-date_calcul")
            .first()
        )

        rapport = {
            "etudiant": str(etudiant.id),
            "date_rapport": timezone.now().isoformat(),
            "riasec": None,
            "ikigai": None,
            "synthese": "",
            "metiers_prioritaires": [],
        }

        if dernier_riasec:
            rapport["riasec"] = {
                "code_holland": dernier_riasec.code_holland,
                "score_global": dernier_riasec.score_global,
                "scores_par_dimension": dernier_riasec.scores_par_dimension,
                "forces": dernier_riasec.forces,
            }

        if dernier_ikigai:
            rapport["ikigai"] = {
                "score_global": dernier_ikigai.score_global,
                "scores_par_dimension": dernier_ikigai.scores_par_dimension,
                "forces": dernier_ikigai.forces,
                "axes_amelioration": dernier_ikigai.axes_amelioration,
            }

        # Synthèse combinée
        if rapport["riasec"] and rapport["ikigai"]:
            rapport["synthese"] = cls._synthese_combinee(rapport["riasec"], rapport["ikigai"])
            rapport["metiers_prioritaires"] = cls._croiser_metiers(
                rapport["riasec"]["code_holland"],
                rapport["ikigai"]["scores_par_dimension"],
            )
        elif rapport["riasec"]:
            rapport["synthese"] = (
                f"Profil RIASEC : {rapport['riasec']['code_holland']}. "
                "Passez le test Ikigai pour compléter votre rapport d'orientation combiné."
            )
        elif rapport["ikigai"]:
            rapport["synthese"] = (
                f"Profil Ikigai identifié (score global : {rapport['ikigai']['score_global']}/100). "
                "Passez le test RIASEC pour affiner vos recommandations de métiers."
            )

        return rapport

    @classmethod
    def _synthese_combinee(cls, riasec: Dict, ikigai: Dict) -> str:
        """Génère une synthèse narrative combinée."""
        code = riasec.get("code_holland", "")
        pilier_dominant = max(
            (ikigai.get("scores_par_dimension") or {}).items(),
            key=lambda x: x[1],
            default=("", 0),
        )[0]

        synthese = (
            f"Votre profil combiné : RIASEC={code} × Ikigai={pilier_dominant}.\n\n"
            "Cette combinaison révèle une double lecture de votre orientation :\n"
            f"- Le RIASEC ({code}) décrit vos intérêts professionnels dominants.\n"
            f"- L'Ikigai ({pilier_dominant}) identifie votre moteur motivationnel principal.\n\n"
        )

        # Si le pilier Ikigai est "Passion" et le code RIASEC est Artistique → cohérence forte
        if pilier_dominant == PilierIkigai.PASSION and "A" in code:
            synthese += (
                "Cohérence forte : votre passion s'aligne avec un profil artistique. "
                "Poursuivez dans les métiers créatifs (design, architecture, arts, communication)."
            )
        elif pilier_dominant == PilierIkigai.MISSION and "S" in code:
            synthese += (
                "Cohérence forte : votre desire d'utilité sociale s'aligne avec un profil Social. "
                "Les métiers de l'enseignement, du soin et de l'accompagnement sont faits pour vous."
            )
        elif pilier_dominant == PilierIkigai.PROFESSION and ("I" in code or "R" in code):
            synthese += (
                "Cohérence forte : vos talents naturels s'alignent avec un profil technique/analytique. "
                "Les métiers de l'ingénierie, de la recherche et de la data vous correspondent."
            )
        elif pilier_dominant == PilierIkigai.VOCATION and "E" in code:
            synthese += (
                "Cohérence forte : votre recherche de viabilité économique s'aligne avec un profil entreprenant. "
                "Le commerce, le management et l'entrepreneuriat sont vos voies naturelles."
            )
        else:
            synthese += (
                "Profil atypique : votre RIASEC et votre Ikigai pointent dans des directions différentes. "
                "Un conseiller d'orientation peut vous aider à identifier des métiers "
                "qui réconcilient ces deux dimensions."
            )

        return synthese

    @classmethod
    def _croiser_metiers(cls, code_holland: str, scores_ikigai: Dict) -> List[str]:
        """
        Croise les familles de métiers RIASEC et Ikigai pour identifier les recommandations prioritaires.
        """
        # Mapping RIASEC → familles de métiers
        familles_riasec = {
            "R": ["Ingénierie", "Mécanique", "BTP", "Agriculture", "Maintenance industrielle"],
            "I": ["Recherche scientifique", "Data science", "Médecine", "Audit", "Analyse"],
            "A": ["Design", "Architecture", "Arts", "Communication", "Audiovisuel"],
            "S": ["Enseignement", "Santé", "Travail social", "Ressources humaines", "Coaching"],
            "E": ["Commerce", "Management", "Entrepreneuriat", "Marketing", "Conseil"],
            "C": ["Comptabilité", "Finance", "Logistique", "Administration", "Audit"],
        }
        # Mapping Ikigai (déjà implémenté dans IkigaiScoringService._recommander_metiers_ikigai)
        familles_ikigai = {
            PilierIkigai.PASSION: ["Arts", "Communication", "Médiation culturelle"],
            PilierIkigai.MISSION: ["Éducation", "Santé", "ONG", "Travail social", "Développement durable"],
            PilierIkigai.VOCATION: ["Commerce", "Finance", "Management", "Entrepreneuriat"],
            PilierIkigai.PROFESSION: ["Ingénierie", "Recherche", "Informatique", "Architecture"],
        }

        # Récupère les familles pour les 2-3 dimensions RIASEC dominantes
        riasec_set = set()
        for dim in code_holland.replace("-", "")[:3]:
            riasec_set.update(familles_riasec.get(dim, []))

        # Récupère les familles pour le pilier Ikigai dominant
        pilier_dominant = max(scores_ikigai.items(), key=lambda x: x[1])[0] if scores_ikigai else None
        ikigai_set = set(familles_ikigai.get(pilier_dominant, []))

        # Intersection = métiers prioritaires (cohérents avec les 2 cadres)
        intersection = riasec_set & ikigai_set
        if intersection:
            return sorted(intersection)[:8]

        # Sinon, union triée par score Ikigai
        return sorted(riasec_set | ikigai_set)[:8]
