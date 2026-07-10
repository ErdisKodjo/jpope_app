"""
Modèle AdmissionHistorique + extension de Formation pour le simulateur d'admissions.

Conformément au cahier des charges (section 2.1 — Candidat, Simulateur d'Admissions) :
"Outil prédictif calculant le pourcentage de chances d'intégrer une formation spécifique
en croisant la moyenne pondérée de l'élève avec les critères d'admission historiques
de l'établissement."
"""
import uuid
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .etablissement import Etablissement
from .formation import Formation


class AdmissionHistorique(models.Model):
    """
    Historique anonymisé des admissions sur une formation.
    Sert de base d'apprentissage au simulateur prédictif.

    Conformément au cahier des charges : "critères d'admission historiques de l'établissement".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="historique_admissions",
        verbose_name=_("formation"),
    )
    annee = models.PositiveIntegerField(
        _("année"),
        help_text=_("Année du concours / admission"),
    )

    # Profil du candidat (anonymisé — pas de lien User)
    moyenne_bac = models.FloatField(
        _("moyenne au bac"),
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text=_("Moyenne /20"),
    )
    serie_bac = models.CharField(
        _("série de bac"),
        max_length=10,
        help_text=_("Ex: C, D, G2, L, etc."),
    )
    mention = models.CharField(
        _("mention"),
        max_length=20,
        blank=True,
        help_text=_("Passable, Assez Bien, Bien, Très Bien"),
    )

    # Décision
    a_ete_admis = models.BooleanField(
        _("a été admis"),
        help_text=_("True si le candidat a été admis cette année-là"),
    )
    rang_admission = models.PositiveIntegerField(
        _("rang d'admission"),
        blank=True,
        null=True,
        help_text=_("Rang dans le classement (si admis)"),
    )

    # Métadonnées
    nombre_candidats_annee = models.PositiveIntegerField(
        _("nombre total de candidats cette année"),
        default=0,
    )
    nombre_admis_annee = models.PositiveIntegerField(
        _("nombre total d'admis cette année"),
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("historique d'admission")
        verbose_name_plural = _("historiques d'admissions")
        ordering = ["-annee", "-created_at"]
        indexes = [
            models.Index(fields=["formation", "annee"]),
            models.Index(fields=["a_ete_admis"]),
        ]

    def __str__(self):
        statut = "Admis" if self.a_ete_admis else "Refusé"
        return f"{self.formation.nom} {self.annee} — {self.moyenne_bac}/20 ({self.serie_bac}) — {statut}"


class ResultatSimulateur(models.Model):
    """
    Sauvegarde chaque simulation faite par un étudiant.
    Permet de suivre l'évolution des projections dans le temps.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etudiant = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="simulations_admission",
        verbose_name=_("étudiant"),
    )
    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="simulations",
        verbose_name=_("formation"),
    )
    # Inputs de la simulation
    moyenne_saisie = models.FloatField(
        _("moyenne saisie par l'étudiant"),
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    serie_bac_saisie = models.CharField(
        _("série de bac saisie"),
        max_length=10,
        blank=True,
    )
    # Résultat
    pourcentage_chances = models.FloatField(
        _("pourcentage de chances d'admission"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    niveau_confiance = models.CharField(
        _("niveau de confiance"),
        max_length=20,
        default="MOYEN",
        help_text=_("Faible, Moyen, Élevé — selon la quantité de données historiques"),
    )
    explication = models.JSONField(
        _("explication détaillée"),
        default=dict,
        help_text=_("Décomposition du calcul pour transparence"),
    )
    recommandations = models.JSONField(
        _("recommandations"),
        default=list,
        help_text=_("Liste de recommandations pour améliorer ses chances"),
    )
    date_simulation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("résultat de simulation")
        verbose_name_plural = _("résultats de simulations")
        ordering = ["-date_simulation"]

    def __str__(self):
        return f"{self.etudiant.email} → {self.formation.nom} : {self.pourcentage_chances}%"
