"""
Managers personnalisés pour le catalog.
"""
from django.db import models


class EtablissementManager(models.Manager):
    def actifs(self):
        return self.filter(is_active=True)

    def verifies(self):
        return self.filter(is_verified=True, is_active=True)

    def par_ville(self, ville):
        return self.actifs().filter(ville__iexact=ville)

    def top_notes(self, limit=10):
        return self.verifies().order_by("-note_globale")[:limit]

    def top_qualite(self, limit=10):
        return self.verifies().order_by("-score_qualite_global")[:limit]

    def abordables(self, budget_max):
        return self.actifs().filter(frais_scolarite_annuel_max__lte=budget_max)

    def avec_bourses(self):
        return self.actifs().filter(propose_bourses=True)


class FormationManager(models.Manager):
    def actives(self):
        return self.filter(is_active=True)

    def par_domaine(self, domaine_id):
        return self.actives().filter(domaine_id=domaine_id)

    def par_etablissement(self, etablissement_id):
        return self.actives().filter(etablissement_id=etablissement_id)

    def par_niveau(self, niveau):
        return self.actives().filter(niveau=niveau)

    def strategiques(self):
        """Formations d'importance stratégique élevée ou critique."""
        return self.actives().filter(
            importance_strategique__in=["CRITIQUE", "ELEVEE"]
        )

    def avec_bourses(self):
        return self.actives().filter(bourses_disponibles=True)

    def budget_max(self, budget):
        return self.actives().filter(cout_annuel__lte=budget)

    def top_qualite(self, limit=20):
        return self.actives().order_by("-score_qualite")[:limit]

    def inscriptions_ouvertes(self):
        """Formations avec date limite d'inscription dans le futur."""
        from django.utils import timezone
        return self.actives().filter(
            date_limite_inscription__gte=timezone.now().date()
        )


class MetierManager(models.Manager):
    def actifs(self):
        return self.filter(is_active=True)

    def forte_demande(self):
        return self.actifs().filter(
            demande_marche__in=["TRES_FORTE", "FORTE"]
        )

    def par_domaine(self, domaine_id):
        return self.actifs().filter(domaine_id=domaine_id)

    def top_revenus(self, limit=20):
        return self.actifs().order_by("-revenu_moyen")[:limit]

    def top_attractivite(self, limit=20):
        return self.actifs().order_by("-score_attractivite")[:limit]
