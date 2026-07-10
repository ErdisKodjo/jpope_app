"""
Service Marketing & CRM pour les Établissements.

Fonctionnalités :
- Ciblage de candidats selon un segment (matching algorithm)
- Gestion des leads qualifiés (facturation au lead)
- Gestion des candidatures (CRM : accepter / rejeter / mettre en attente)
- Statistiques marketing (vues, clics, conversions, ROI)
- Synchronisation API externe (extensibilité)
"""
import logging
from typing import List, Dict
from django.db.models import Q, F, Count
from django.utils import timezone

from apps.marketing.models import (
    SegmentCandidats, CampagneMarketing, LeadQualifie,
    CandidatureCRM, LogInteractionCRM, TypeInteraction,
    StatutLead, StatutCampagne, StatutCandidatureCRM,
)
from apps.accounts.models import User, UserRole
from apps.accounts.models.enums import UserRole as UR

logger = logging.getLogger(__name__)


class MarketingService:
    """Service de ciblage et gestion des campagnes."""

    @staticmethod
    def cibler_candidats(segment: SegmentCandidats, limit: int = 500) -> List[User]:
        """
        Identifie les candidats correspondant aux critères du segment.
        Conformément au cahier des charges : "profils de candidats spécifiques
        (selon la région, les notes ou les résultats des tests d'orientation)".
        """
        qs = User.objects.filter(
            role=UR.STUDENT,
            is_active=True,
            statut_compte="ACTIF",
        )

        # Filtre par niveau actuel
        if segment.niveau_actuel:
            qs = qs.filter(
                student_profile__niveau_actuel__in=segment.niveau_actuel
            )

        # Filtre par séries de bac
        if segment.series_bac:
            qs = qs.filter(
                student_profile__serie_bac__in=segment.series_bac
            )

        # Filtre par moyenne
        if segment.moyenne_min is not None:
            qs = qs.filter(student_profile__moyenne_generale__gte=segment.moyenne_min)
        if segment.moyenne_max is not None:
            qs = qs.filter(student_profile__moyenne_generale__lte=segment.moyenne_max)

        # TODO: filtre par région (nécessite champ ville sur StudentProfile)
        # TODO: filtre par RIASEC (nécessite jointure avec ResultatTest)

        return list(qs[:limit])

    @staticmethod
    def calculer_score_matching(candidat: User, segment: SegmentCandidats) -> tuple:
        """
        Calcule un score de matching (0-100) entre un candidat et un segment.
        Retourne (score, dict des critères matchés).
        """
        score = 0
        max_score = 0
        matches = {}

        try:
            sp = candidat.student_profile
        except Exception:
            sp = None

        # Critère 1: niveau actuel (poids 25)
        if segment.niveau_actuel:
            max_score += 25
            if sp and sp.niveau_actuel in segment.niveau_actuel:
                score += 25
                matches["niveau_actuel"] = sp.niveau_actuel
            else:
                matches["niveau_actuel"] = False
        else:
            matches["niveau_actuel"] = None

        # Critère 2: séries de bac (poids 25)
        if segment.series_bac:
            max_score += 25
            if sp and sp.serie_bac in segment.series_bac:
                score += 25
                matches["serie_bac"] = sp.serie_bac
            else:
                matches["serie_bac"] = False
        else:
            matches["serie_bac"] = None

        # Critère 3: moyenne (poids 25)
        if segment.moyenne_min is not None or segment.moyenne_max is not None:
            max_score += 25
            moyenne_candidat = float(sp.moyenne_generale) if sp and sp.moyenne_generale else 0
            ok_min = segment.moyenne_min is None or moyenne_candidat >= segment.moyenne_min
            ok_max = segment.moyenne_max is None or moyenne_candidat <= segment.moyenne_max
            if ok_min and ok_max:
                score += 25
                matches["moyenne"] = moyenne_candidat
            else:
                matches["moyenne"] = False
        else:
            matches["moyenne"] = None

        # Critère 4: code RIASEC (poids 25)
        if segment.code_riasec_cible:
            max_score += 25
            try:
                from apps.orientation.models import ResultatTest
                dernier_resultat = (
                    ResultatTest.objects
                    .filter(reponse_utilisateur__etudiant=candidat)
                    .order_by("-date_calcul")
                    .first()
                )
                if dernier_resultat and dernier_resultat.code_holland:
                    code_candidat = dernier_resultat.code_holland
                    # Match si au moins une lettre du segment est dans le code du candidat
                    for cible in segment.code_riasec_cible:
                        if any(lettre in code_candidat for lettre in cible if len(lettre) == 1):
                            score += 25
                            matches["code_riasec"] = code_candidat
                            break
                    else:
                        matches["code_riasec"] = False
                else:
                    matches["code_riasec"] = False
            except Exception:
                matches["code_riasec"] = False
        else:
            matches["code_riasec"] = None

        # Si aucun critère défini → score = 50 (neutre)
        if max_score == 0:
            return 50.0, matches

        return round((score / max_score) * 100, 1), matches

    @staticmethod
    def activer_campagne(campagne: CampagneMarketing) -> int:
        """
        Active une campagne et génère les leads qualifiés pour tous les candidats
        correspondant au segment. Retourne le nombre de leads générés.
        """
        if not campagne.segment:
            raise ValueError("La campagne doit avoir un segment défini.")

        campagne.statut = StatutCampagne.ACTIVE
        campagne.save(update_fields=["statut"])

        candidats = MarketingService.cibler_candidats(campagne.segment)
        leads_crees = 0
        for candidat in candidats:
            score, matches = MarketingService.calculer_score_matching(
                candidat, campagne.segment
            )
            # Ne génère un lead que si le score >= 50%
            if score >= 50:
                _, created = LeadQualifie.objects.get_or_create(
                    campagne=campagne,
                    candidat=candidat,
                    defaults={
                        "score_matching": score,
                        "critères_matches": matches,
                    },
                )
                if created:
                    leads_crees += 1

        campagne.leads_generes = leads_crees
        campagne.save(update_fields=["leads_generes"])
        return leads_crees

    @staticmethod
    def enregistrer_vue_campagne(campagne: CampagneMarketing):
        """Incrémente le compteur de vues d'une campagne."""
        CampagneMarketing.objects.filter(pk=campagne.pk).update(vues=F("vues") + 1)

    @staticmethod
    def enregistrer_clic_campagne(campagne: CampagneMarketing):
        """Incrémente le compteur de clics."""
        CampagneMarketing.objects.filter(pk=campagne.pk).update(clics=F("clics") + 1)

    @staticmethod
    def facturer_lead_si_contact_initie(lead: LeadQualifie) -> bool:
        """
        Facture le lead à l'établissement si celui-ci initie un contact direct
        avec le candidat. Conformément au cahier des charges : "Modèle au Lead Qualifié :
        Facturation à la performance lorsque l'établissement initie un contact direct".
        """
        if lead.is_facture:
            return False  # Déjà facturé

        montant = lead.campagne.cout_par_lead_qualifie
        lead.is_facture = True
        lead.date_facturation = timezone.now()
        lead.montant_facture = montant
        lead.statut = StatutLead.CONTACTE
        lead.date_premier_contact = timezone.now()
        lead.save(update_fields=[
            "is_facture", "date_facturation", "montant_facture",
            "statut", "date_premier_contact",
        ])

        # TODO: déclencher la facturation via apps.payments (Stripe / Flooz / TMoney)
        logger.info(
            f"Lead facturé : {lead.candidat.email} → {lead.campagne.etablissement.nom} "
            f"({montant} FCFA)"
        )
        return True


class CRMService:
    """Service de gestion des candidatures (CRM établissement)."""

    @staticmethod
    def changer_statut_candidature(
        candidature: CandidatureCRM,
        nouveau_statut: str,
        auteur,
        commentaire: str = "",
        motif_refus: str = "",
    ) -> CandidatureCRM:
        """Change le statut d'une candidature et log l'interaction."""
        candidature.statut = nouveau_statut
        candidature.commentaire_etablissement = commentaire
        if nouveau_statut == StatutCandidatureCRM.REFUSEE:
            candidature.motif_refus = motif_refus
        if nouveau_statut in (StatutCandidatureCRM.ACCEPTEE, StatutCandidatureCRM.REFUSEE,
                              StatutCandidatureCRM.EN_ATTENTE):
            candidature.date_decision = timezone.now()
        if nouveau_statut == StatutCandidatureCRM.INSCRIT:
            candidature.date_inscription = timezone.now()
        candidature.save()

        # Log l'interaction
        LogInteractionCRM.objects.create(
            candidature=candidature,
            type=TypeInteraction.NOTE_INTERNE,
            auteur=auteur,
            sujet=f"Statut changé → {nouveau_statut}",
            contenu=commentaire or motif_refus or "Changement de statut",
            is_automatique=False,
        )
        return candidature

    @staticmethod
    def statistiques_pipeline(etablissement) -> Dict:
        """Statistiques agrégées du pipeline de candidatures d'un établissement."""
        qs = CandidatureCRM.objects.filter(etablissement=etablissement)
        total = qs.count()
        return {
            "total": total,
            "recues": qs.filter(statut=StatutCandidatureCRM.RECUE).count(),
            "en_revue": qs.filter(statut=StatutCandidatureCRM.EN_REVUE).count(),
            "acceptees": qs.filter(statut=StatutCandidatureCRM.ACCEPTEE).count(),
            "refusees": qs.filter(statut=StatutCandidatureCRM.REFUSEE).count(),
            "en_attente": qs.filter(statut=StatutCandidatureCRM.EN_ATTENTE).count(),
            "inscrites": qs.filter(statut=StatutCandidatureCRM.INSCRIT).count(),
            "desistes": qs.filter(statut=StatutCandidatureCRM.DESISTE).count(),
            "taux_conversion": round(
                (qs.filter(statut=StatutCandidatureCRM.INSCRIT).count() / total * 100) if total > 0 else 0,
                1,
            ),
        }

    @staticmethod
    def synchroniser_externe(candidature: CandidatureCRM) -> bool:
        """
        Synchronise la candidature avec le système externe de l'établissement.
        En production : appel HTTP à l'API de l'établissement.
        Ici : stub qui marque la candidature comme synchronisée.
        """
        # TODO: implémenter l'appel HTTP selon le format API de l'établissement
        candidature.is_synced_external = True
        candidature.last_sync_at = timezone.now()
        candidature.save(update_fields=["is_synced_external", "last_sync_at"])
        LogInteractionCRM.objects.create(
            candidature=candidature,
            type=TypeInteraction.NOTE_INTERNE,
            sujet="Synchronisation API externe",
            contenu=f"Candidature synchronisée à {timezone.now():%d/%m/%Y %H:%M}",
            is_automatique=True,
        )
        return True

    @staticmethod
    def statistiques_campagne(campagne: CampagneMarketing) -> Dict:
        """Statistiques d'une campagne marketing."""
        leads = LeadQualifie.objects.filter(campagne=campagne)
        return {
            "vues": campagne.vues,
            "clics": campagne.clics,
            "taux_clic": round((campagne.clics / campagne.vues * 100) if campagne.vues > 0 else 0, 1),
            "leads_generes": campagne.leads_generes,
            "leads_contactes": leads.filter(statut=StatutLead.CONTACTE).count(),
            "leads_qualified": leads.filter(statut=StatutLead.QUALIFIE).count(),
            "leads_convertis": leads.filter(statut=StatutLead.CONVERTI).count(),
            "conversions": campagne.conversions,
            "taux_conversion": campagne.taux_conversion,
            "budget_fcfa": int(campagne.budget_fcfa),
            "cout_par_lead": int(campagne.cout_par_lead_qualifie),
            "cout_total_facture": int(
                leads.filter(is_facture=True).count() * campagne.cout_par_lead_qualifie
            ),
        }
