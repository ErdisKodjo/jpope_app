"""
Managers personnalisés pour l'app dashboard.
"""
from django.db import models
from django.utils import timezone

class FavoriManager(models.Manager):
    def pour_utilisateur(self, utilisateur):
        return self.filter(utilisateur=utilisateur)

    def par_type(self, utilisateur, type_entite):
        return self.filter(utilisateur=utilisateur, type_entite=type_entite)

    def formations(self, utilisateur):
        return self.pour_utilisateur(utilisateur).filter(type_entite="FORMATION")

    def metiers(self, utilisateur):
        return self.pour_utilisateur(utilisateur).filter(type_entite="METIER")

    def etablissements(self, utilisateur):
        return self.pour_utilisateur(utilisateur).filter(type_entite="ETABLISSEMENT")

    def est_favori(self, utilisateur, type_entite, entity_id):
        """Vérifie si une entité est en favori."""
        field_map = {
            "FORMATION": "formation_id",
            "METIER": "metier_id",
            "ETABLISSEMENT": "etablissement_id",
            "EVENEMENT": "evenement_id",
        }
        field = field_map.get(type_entite)
        if not field:
            return False
        return self.filter(
            utilisateur=utilisateur,
            type_entite=type_entite,
            **{field: entity_id},
        ).exists()

class VoeuManager(models.Manager):
    def actifs(self, etudiant):
        return self.filter(
            etudiant=etudiant,
            statut__in=["BROUILLON", "SOUMIS", "EN_ATTENTE", "LISTE_ATTENTE"],
        )

    def par_statut(self, etudiant, statut):
        return self.filter(etudiant=etudiant, statut=statut)

    def acceptes(self, etudiant):
        return self.filter(etudiant=etudiant, statut="ACCEPTE")

    def principal(self, etudiant):
        return self.filter(etudiant=etudiant, est_principal=True).first()

    def en_attente_reponse(self, etudiant):
        return self.filter(etudiant=etudiant, statut="EN_ATTENTE")

    def ordonnes(self, etudiant):
        return self.filter(etudiant=etudiant).order_by("priorite")

class DemarcheManager(models.Manager):
    def actives(self, etudiant):
        return self.filter(
            etudiant=etudiant,
            statut__in=["A_FAIRE", "EN_COURS", "ENVOYEE"],
        )

    def en_retard(self, etudiant=None):
        """Démarches dont l'échéance est passée."""
        qs = self.filter(
            date_echeance__lt=timezone.now(),
            statut__in=["A_FAIRE", "EN_COURS", "ENVOYEE"],
        )
        if etudiant:
            qs = qs.filter(etudiant=etudiant)
        return qs

    def a_venir(self, etudiant, jours=30):
        """Démarches avec échéance dans les X prochains jours."""
        limite = timezone.now() + timezone.timedelta(days=jours)
        return self.filter(
            etudiant=etudiant,
            date_echeance__gte=timezone.now(),
            date_echeance__lte=limite,
            statut__in=["A_FAIRE", "EN_COURS"],
        )

    def completees(self, etudiant):
        return self.filter(etudiant=etudiant, statut="COMPLETEE")

class EvenementAgendaManager(models.Manager):
    def a_venir(self, utilisateur, jours=60):
        """Événements à venir dans les X prochains jours."""
        limite = timezone.now() + timezone.timedelta(days=jours)
        return self.filter(
            utilisateur=utilisateur,
            date_debut__gte=timezone.now(),
            date_debut__lte=limite,
            est_annule=False,
        ).order_by("date_debut")

    def passes(self, utilisateur):
        return self.filter(
            utilisateur=utilisateur,
            date_debut__lt=timezone.now(),
        ).order_by("-date_debut")

    def aujourdhui(self, utilisateur):
        """Événements du jour."""
        today = timezone.now().date()
        return self.filter(
            utilisateur=utilisateur,
            date_debut__date=today,
            est_annule=False,
        )

    def cette_semaine(self, utilisateur):
        """Événements de la semaine."""
        today = timezone.now().date()
        fin_semaine = today + timezone.timedelta(days=7)
        return self.filter(
            utilisateur=utilisateur,
            date_debut__date__gte=today,
            date_debut__date__lte=fin_semaine,
            est_annule=False,
        ).order_by("date_debut")
