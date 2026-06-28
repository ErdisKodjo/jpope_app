"""
Managers personnalisés pour l'app orientation.
"""
from django.db import models
from django.utils import timezone

class TestOrientationManager(models.Manager):
    def actifs(self):
        return self.filter(is_active=True)

    def publics(self):
        return self.actifs().filter(is_public=True)

    def par_type(self, type_test):
        return self.actifs().filter(type=type_test)

    def featured(self):
        return self.actifs().filter(is_featured=True)

class ReponseUtilisateurManager(models.Manager):
    def en_cours(self, etudiant):
        return self.filter(etudiant=etudiant, statut="EN_COURS")

    def termines(self, etudiant=None):
        qs = self.filter(statut="TERMINE")
        if etudiant:
            qs = qs.filter(etudiant=etudiant)
        return qs

    def par_test(self, test_id):
        return self.filter(test_id=test_id, statut="TERMINE")

    def historiques(self, etudiant):
        """Historique chronologique des tests terminés d'un étudiant."""
        return (
            self.filter(etudiant=etudiant, statut="TERMINE")
            .select_related("test", "resultat")
            .order_by("-date_debut")
        )

    def expirees(self):
        """Sessions en cours depuis plus de 24h → expirées."""
        seuil = timezone.now() - timezone.timedelta(hours=24)
        return self.filter(statut="EN_COURS", date_debut__lt=seuil)

class RecommandationManager(models.Manager):
    def pour_etudiant(self, etudiant):
        return (
            self.filter(etudiant=etudiant)
            .select_related("formation", "metier", "etablissement")
            .order_by("plan", "ordre", "-taux_compatibilite")
        )

    def principales(self, etudiant):
        return self.pour_etudiant(etudiant).filter(plan="PRINCIPAL")

    def alternatives(self, etudiant):
        return self.pour_etudiant(etudiant).filter(plan="ALTERNATIF")

    def non_vues(self, etudiant):
        return self.pour_etudiant(etudiant).filter(a_ete_vue=False)

    def statistiques_engagement(self, etudiant):
        qs = self.filter(etudiant=etudiant)
        return {
            "total": qs.count(),
            "vues": qs.filter(a_ete_vue=True).count(),
            "favorisees": qs.filter(a_ete_favorisee=True).count(),
            "cliquees": qs.filter(a_ete_cliquee=True).count(),
        }
