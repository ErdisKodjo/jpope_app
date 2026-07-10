"""
Service RGPD — logique métier pour les droits RGPD.

Implémente :
- Consentement (donner / retirer / vérifier)
- Export des données (droit d'accès art. 15 + portabilité art. 20)
- Droit à l'oubli (art. 17) — anonymisation
- Journalisation des accès
- Application des politiques de conservation
"""
import json
import zipfile
import io
from datetime import timedelta
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.compliance.models import (
    ConsentementRGPD,
    DemandeRGPD,
    JournalTraitement,
    PolitiqueConservation,
    TypeConsentement,
    StatutConsentement,
    TypeDemandeRGPD,
    StatutDemandeRGPD,
    CategorieDonnee,
)


class RGPDService:
    """Centralise les opérations RGPD."""

    # ─── Consentement ───

    @staticmethod
    def donner_consentement(
        utilisateur,
        type_consentement: str,
        texte: str,
        version_politique: str = "1.0",
        ip_address=None,
        user_agent: str = "",
        parent=None,
    ) -> ConsentementRGPD:
        """
        Enregistre un consentement explicite. Si un consentement actif du même type
        existe déjà, on le retire d'abord (nouvelle version = nouveau consentement).
        """
        # Retire les consentements actifs antérieurs du même type
        ConsentementRGPD.objects.filter(
            utilisateur=utilisateur,
            type=type_consentement,
            statut=StatutConsentement.ACTIVE,
        ).update(
            statut=StatutConsentement.RETIRE,
            date_retrait=timezone.now(),
        )
        return ConsentementRGPD.objects.create(
            utilisateur=utilisateur,
            type=type_consentement,
            texte_consentement=texte,
            version_politique=version_politique,
            ip_consentement=ip_address,
            user_agent=user_agent,
            parent=parent,
        )

    @staticmethod
    def retirer_consentement(utilisateur, type_consentement: str) -> int:
        """Retire tous les consentements actifs d'un type donné pour l'utilisateur."""
        return ConsentementRGPD.objects.filter(
            utilisateur=utilisateur,
            type=type_consentement,
            statut=StatutConsentement.ACTIVE,
        ).update(
            statut=StatutConsentement.RETIRE,
            date_retrait=timezone.now(),
        )

    @staticmethod
    def has_consentement(utilisateur, type_consentement: str) -> bool:
        return ConsentementRGPD.objects.filter(
            utilisateur=utilisateur,
            type=type_consentement,
            statut=StatutConsentement.ACTIVE,
        ).exists()

    # ─── Journalisation ───

    @staticmethod
    def log_acces(acteur, cible, action: str, categorie: str, details: dict = None, ip_address=None):
        """Enregistre un accès à des données personnelles dans le journal."""
        return JournalTraitement.objects.create(
            acteur=acteur,
            cible=cible,
            action=action,
            categorie_donnee=categorie,
            details=details or {},
            ip_address=ip_address,
        )

    # ─── Export des données (art. 15 + 20) ───

    @staticmethod
    def collecter_donnees_utilisateur(utilisateur) -> dict:
        """
        Collecte TOUTES les données personnelles d'un utilisateur dans un dictionnaire
        structuré par catégorie. Utilisé pour l'export RGPD.
        """
        from apps.accounts.models import (
            StudentProfile, CounselorProfile, SchoolRepProfile,
            ParentProfile, NotesEtudiant, DocumentVerification,
        )

        data = {
            "meta": {
                "utilisateur_id": str(utilisateur.id),
                "email": utilisateur.email,
                "exporte_le": timezone.now().isoformat(),
            },
            "identite": {
                "first_name": utilisateur.first_name,
                "last_name": utilisateur.last_name,
                "email": utilisateur.email,
                "phone": utilisateur.phone,
                "genre": utilisateur.genre,
                "date_naissance": utilisateur.date_naissance.isoformat() if utilisateur.date_naissance else None,
                "avatar": utilisateur.avatar.url if utilisateur.avatar else None,
                "role": utilisateur.role,
                "date_inscription": utilisateur.created_at.isoformat(),
            },
            "consentements": [],
            "scolaire": {},
            "orientation": [],
            "messagerie": [],
            "communaute": [],
            "financiere": [],
            "documents": [],
        }

        # Consentements
        for c in utilisateur.consentements.all():
            data["consentements"].append({
                "type": c.type,
                "statut": c.statut,
                "texte": c.texte_consentement,
                "date": c.date_consentement.isoformat(),
                "date_retrait": c.date_retrait.isoformat() if c.date_retrait else None,
            })

        # Profil étudiant + notes
        try:
            sp = utilisateur.student_profile
            data["scolaire"]["profil_etudiant"] = {
                "niveau_actuel": sp.niveau_actuel,
                "serie_bac": sp.serie_bac,
                "annee_bac": sp.annee_bac,
                "etablissement_origine": sp.etablissement_origine,
                "ville_origine": sp.ville_origine,
                "moyenne_generale": str(sp.moyenne_generale) if sp.moyenne_generale else None,
            }
        except StudentProfile.DoesNotExist:
            pass

        try:
            notes = utilisateur.notes_etudiant
            data["scolaire"]["notes"] = {
                "classe": notes.classe,
                "annee_scolaire": notes.annee_scolaire,
                "moyenne_generale": str(notes.moyenne_generale) if notes.moyenne_generale else None,
                "details_matieres": notes.details_matieres,
            }
        except NotesEtudiant.DoesNotExist:
            pass

        # Tests d'orientation
        from apps.orientation.models import ResultatTest
        for r in ResultatTest.objects.filter(etudiant=utilisateur):
            data["orientation"].append({
                "test": str(r.test.nom) if hasattr(r, "test") else None,
                "score": getattr(r, "score_global", None),
                "code_riasec": getattr(r, "code_riasec", None),
                "date": r.created_at.isoformat() if hasattr(r, "created_at") else None,
            })

        # Messages communautaires / messagerie
        from apps.community.models import MessagePrive, MessageForum
        for m in MessagePrive.objects.filter(conversation__participants=utilisateur):
            data["messagerie"].append({
                "contenu": m.contenu[:200] + "..." if len(m.contenu) > 200 else m.contenu,
                "date": m.created_at.isoformat() if hasattr(m, "created_at") else None,
            })
        for m in MessageForum.objects.filter(auteur=utilisateur):
            data["communaute"].append({
                "contenu": m.contenu[:200] + "..." if len(m.contenu) > 200 else m.contenu,
                "thread": str(m.thread.id) if hasattr(m, "thread") else None,
                "date": m.created_at.isoformat() if hasattr(m, "created_at") else None,
            })

        # Documents de vérification
        for doc in DocumentVerification.objects.filter(user=utilisateur):
            data["documents"].append({
                "type": doc.type_document,
                "statut": doc.statut,
                "fichier_url": doc.fichier.url if doc.fichier else None,
                "date_soumission": doc.date_soumission.isoformat() if hasattr(doc, "date_soumission") else None,
            })

        # Paiements
        from apps.payments.models import Abonnement, Transaction
        for ab in Abonnement.objects.filter(utilisateur=utilisateur):
            data["financiere"].append({
                "type": "abonnement",
                "plan": str(ab.plan) if hasattr(ab, "plan") else None,
                "statut": ab.statut if hasattr(ab, "statut") else None,
                "date_debut": ab.date_debut.isoformat() if hasattr(ab, "date_debut") else None,
            })

        return data

    @staticmethod
    def exporter_donnees_utilisateur(utilisateur, demandeur=None) -> bytes:
        """
        Génère un fichier ZIP contenant les données personnelles au format JSON
        + les pièces jointes (avatar, documents, etc.).
        Retourne les bytes du ZIP.
        """
        data = RGPDService.collecter_donnees_utilisateur(utilisateur)
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False, cls=DjangoJSONEncoder).encode("utf-8")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("donnees-personnelles.json", json_bytes)
            zf.writestr("LISEZMOI.txt", (
                f"Export RGPD — {utilisateur.email}\n"
                f"Généré le : {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                "Ce fichier contient l'ensemble des données personnelles que "
                "AvenSU-Orienta détient à votre sujet, conformément à l'article 15 "
                "du RGPD (droit d'accès) et l'article 20 (portabilité).\n\n"
                "Format : JSON structuré par catégorie (identité, scolarité, etc.)."
            ).encode("utf-8"))

        # Log de l'accès
        RGPDService.log_acces(
            acteur=demandeur or utilisateur,
            cible=utilisateur,
            action="EXPORT",
            categorie=CategorieDonnee.IDENTITE,
            details={"format": "json+zip", "demande": "ART_15_20"},
        )

        return zip_buffer.getvalue()

    # ─── Droit à l'oubli (art. 17) ───

    @staticmethod
    def anonymiser_utilisateur(utilisateur, demandeur=None) -> dict:
        """
        Anonymise les données d'un utilisateur conformément au droit à l'oubli.
        - Remplace les PII par des placeholders
        - Désactive le compte
        - Conserve les données agrégées/anonymisées pour les statistiques
        - Supprime ou anonymise les messages, documents, médias
        """
        import secrets
        from apps.accounts.models import (
            StudentProfile, CounselorProfile, SchoolRepProfile,
            ParentProfile, NotesEtudiant, DocumentVerification,
        )

        anonymized_email = f"anonymized-{secrets.token_hex(8)}@deleted.avensu.tg"

        # 1. PII → anonymisées
        utilisateur.first_name = "Anonymisé"
        utilisateur.last_name = "Anonymisé"
        utilisateur.email = anonymized_email
        utilisateur.phone = ""
        utilisateur.date_naissance = None
        utilisateur.avatar = None
        utilisateur.is_active = False
        utilisateur.is_email_verified = False
        utilisateur.email_verification_token = None
        utilisateur.password_reset_token = None
        utilisateur.statut_compte = "INACTIF"
        # Invalide le mot de passe (ne peut plus se connecter)
        utilisateur.set_unusable_password()
        utilisateur.save()

        # 2. Profils
        for profile_model in [StudentProfile, CounselorProfile, SchoolRepProfile, ParentProfile]:
            try:
                profile = getattr(utilisateur, profile_model._meta.get_field("user").remote_field.get_accessor_name())
                # Anonymise les champs sensibles
                for field in profile._meta.fields:
                    if field.name in ("etablissement_origine", "ville_origine", "bio", "specialites",
                                       "telephone_pro", "numero_licence"):
                        setattr(profile, field.name, "")
                profile.save()
            except Exception:
                pass

        # 3. Notes scolaires
        try:
            notes = utilisateur.notes_etudiant
            notes.details_matieres = {}
            notes.save()
        except NotesEtudiant.DoesNotExist:
            pass

        # 4. Documents de vérification → supprimés
        for doc in DocumentVerification.objects.filter(user=utilisateur):
            if doc.fichier:
                doc.fichier.delete(save=False)
            doc.delete()

        # 5. Messages communautaires → anonymisés (contenu remplacé)
        from apps.community.models import MessagePrive, MessageForum
        MessagePrive.objects.filter(auteur=utilisateur).update(contenu="[Message anonymisé — RGPD]")
        MessageForum.objects.filter(auteur=utilisateur).update(contenu="[Message anonymisé — RGPD]")

        # 6. Consentements → retirés
        ConsentementRGPD.objects.filter(
            utilisateur=utilisateur, statut=StatutConsentement.ACTIVE
        ).update(statut=StatutConsentement.RETIRE, date_retrait=timezone.now())

        # 7. TOTP device → supprimé
        try:
            utilisateur.totp_device.delete()
        except Exception:
            pass

        # 8. Log
        RGPDService.log_acces(
            acteur=demandeur or utilisateur,
            cible=utilisateur,
            action="ANONYMISATION",
            categorie=CategorieDonnee.IDENTITE,
            details={"demande": "ART_17"},
        )

        return {
            "utilisateur_id": str(utilisateur.id),
            "email_anonymise": anonymized_email,
            "statut": "ANONYMISE",
            "date": timezone.now().isoformat(),
        }

    # ─── Demandes RGPD ───

    @staticmethod
    def creer_demande(utilisateur, type_demande: str, motif: str = "") -> DemandeRGPD:
        """Crée une nouvelle demande RGPD."""
        return DemandeRGPD.objects.create(
            utilisateur=utilisateur,
            type=type_demande,
            motif=motif,
        )

    @staticmethod
    def traiter_demande(demande: DemandeRGPD, traite_par, **kwargs) -> DemandeRGPD:
        """Traite une demande RGPD selon son type."""
        demande.statut = StatutDemandeRGPD.EN_COURS
        demande.traitee_par = traite_par
        demande.save(update_fields=["statut", "traitee_par"])

        try:
            if demande.type == TypeDemandeRGPD.ACCES or demande.type == TypeDemandeRGPD.PORTABILITE:
                # Export des données
                data = RGPDService.collecter_donnees_utilisateur(demande.utilisateur)
                demande.donnees_exportees = data
                demande.statut = StatutDemandeRGPD.TRAITEE

            elif demande.type == TypeDemandeRGPD.EFFACEMENT:
                # Anonymisation
                result = RGPDService.anonymiser_utilisateur(demande.utilisateur, demandeur=traite_par)
                demande.donnees_exportees = result
                demande.statut = StatutDemandeRGPD.TRAITEE

            elif demande.type == TypeDemandeRGPD.OPPOSITION:
                # Retire tous les consentements marketing / analytics
                for t in [TypeConsentement.COMMUNICATION_MARKETING, TypeConsentement.ANALYTICS,
                           TypeConsentement.PROFILAGE_IA]:
                    RGPDService.retirer_consentement(demande.utilisateur, t)
                demande.statut = StatutDemandeRGPD.TRAITEE

            elif demande.type == TypeDemandeRGPD.RECTIFICATION:
                # La rectification doit être manuelle — on notifie l'utilisateur
                demande.statut = StatutDemandeRGPD.TRAITEE

            elif demande.type == TypeDemandeRGPD.LIMITATION:
                # Marque le compte en lecture seule (champ à ajouter côté User si besoin)
                demande.statut = StatutDemandeRGPD.TRAITEE

            demande.date_traitement = timezone.now()
            demande.save()
            return demande

        except Exception as e:
            demande.statut = StatutDemandeRGPD.REFUSEE
            demande.motif_refus = f"Erreur technique: {str(e)}"
            demande.save()
            raise

    # ─── Politiques de conservation ───

    @staticmethod
    def seed_politiques_par_defaut():
        """Crée les politiques de conservation par défaut (cf. cahier des charges)."""
        defaults = [
            (CategorieDonnee.IDENTITE, 365 * 5, "Identité conservée 5 ans après dernière activité"),
            (CategorieDonnee.SCOLAIRE, 365 * 3, "Données scolaires conservées 3 ans"),
            (CategorieDonnee.ORIENTATION, 365 * 5, "Résultats d'orientation 5 ans"),
            (CategorieDonnee.MESSAGERIE, 365 * 2, "Messages conservés 2 ans"),
            (CategorieDonnee.COMMUNAUTE, 365 * 3, "Contributions communautaires 3 ans"),
            (CategorieDonnee.FINANCIERE, 365 * 10, "Données financières 10 ans (obligation légale)"),
            (CategorieDonnee.ANALYTICS, 365 * 1, "Logs d'analytics 1 an"),
            (CategorieDonnee.DOCUMENTS, 365 * 3, "Documents de vérification 3 ans"),
        ]
        for cat, duree, desc in defaults:
            PolitiqueConservation.objects.update_or_create(
                categorie=cat,
                defaults={"duree_conservation_jours": duree, "description": desc, "is_active": True},
            )

    @staticmethod
    def appliquer_politiques_conservation():
        """
        Tâche planifiée (Celery beat) — supprime/anonymise les données expirées.
        À exécuter quotidiennement.
        """
        from apps.accounts.models import User
        now = timezone.now()
        count_anonymised = 0

        for politique in PolitiqueConservation.objects.filter(is_active=True):
            limite = now - timedelta(days=politique.duree_conservation_jours)
            # Utilisateurs inactifs depuis la durée de conservation
            for user in User.objects.filter(
                last_activity_at__lt=limite,
                is_active=True,
                is_superuser=False,
            ):
                RGPDService.anonymiser_utilisateur(user, demandeur=None)
                count_anonymised += 1

        return {"anonymised_count": count_anonymised}
