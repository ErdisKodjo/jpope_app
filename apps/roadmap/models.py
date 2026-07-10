"""
Modèles de la Roadmap évolutive étudiante.

Conformément au cahier des charges (section 2.1 — Candidat, Roadmap Évolutive) :
- Niveau Collège : Focus sur la découverte de soi, compréhension des secteurs, fiches métiers simplifiées
- Niveau Lycée : Choix stratégique des spécialités, préparation aux examens, calendrier des concours,
  recherche ciblée d'écoles
- Niveau Post-Bac / Étudiant : Suivi des candidatures, gestion des admissions, inscription administrative,
  recherche de stages/alternances, insertion sur le marché du travail

Modèles :
1. PhaseRoadmap — Collège / Lycée / Post-Bac
2. EtapeRoadmap — étape générique dans une phase (ex: "Choisir ses spécialités")
3. EtapePersonnelleEtudiant — étape personnalisée pour un étudiant (avec statut, date, etc.)
4. JalonRoadmap — jalon clé (ex: "Concours ESGIS — 15 juin")
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PhaseRoadmap(models.TextChoices):
    """Les 3 phases évolutives de la roadmap étudiante."""
    COLLEGE = "COLLEGE", _("Collège — Découverte de soi")
    LYCEE = "LYCEE", _("Lycée — Choix stratégiques")
    POST_BAC = "POST_BAC", _("Post-Bac — Admission & carrière")


class StatutEtape(models.TextChoices):
    NON_COMMENCE = "NON_COMMENCE", _("Non commencé")
    EN_COURS = "EN_COURS", _("En cours")
    COMPLETE = "COMPLETE", _("Complété")
    BLOQUE = "BLOQUE", _("Bloqué")
    ANNULE = "ANNULE", _("Annulé")


class CategorieEtape(models.TextChoices):
    DECOUVERTE = "DECOUVERTE", _("Découverte de soi / secteurs")
    ORIENTATION = "ORIENTATION", _("Tests d'orientation")
    ACADEMIQUE = "ACADEMIQUE", _("Choix académiques / spécialités")
    CONCOURS = "CONCOURS", _("Préparation aux concours / examens")
    CANDIDATURE = "CANDIDATURE", _("Candidatures aux écoles")
    ADMISSION = "ADMISSION", _("Admission & inscription administrative")
    STAGE = "STAGE", _("Recherche de stage / alternance")
    INSERTION = "INSERTION", _("Insertion professionnelle")
    FINANCEMENT = "FINANCEMENT", _("Financement (bourses, prêts)")


class EtapeRoadmap(models.Model):
    """
    Étape générique d'une roadmap (template applicable à tous les étudiants d'une phase).
    Exemple : "Passer le test RIASEC" (phase LYCEE, catégorie ORIENTATION).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phase = models.CharField(
        _("phase"),
        max_length=15,
        choices=PhaseRoadmap.choices,
        db_index=True,
    )
    categorie = models.CharField(
        _("catégorie"),
        max_length=20,
        choices=CategorieEtape.choices,
        db_index=True,
    )
    titre = models.CharField(_("titre"), max_length=255)
    description = models.TextField(_("description"))
    ordre = models.PositiveIntegerField(
        _("ordre"),
        default=0,
        help_text=_("Ordre d'affichage dans la phase"),
    )
    # Lien optionnel vers une ressource
    ressource_externe_url = models.URLField(
        _("URL ressource externe"),
        blank=True,
        help_text=_("Lien vers une page de la plateforme ou externe"),
    )
    # Critère de complétion
    critere_completion = models.TextField(
        _("critère de complétion"),
        blank=True,
        help_text=_("Description de ce qui valide l'étape (ex: 'Test RIASEC passé')"),
    )
    # Période recommandée
    age_min = models.PositiveIntegerField(
        _("âge minimum recommandé"),
        blank=True,
        null=True,
    )
    age_max = models.PositiveIntegerField(
        _("âge maximum recommandé"),
        blank=True,
        null=True,
    )
    # Métadonnées
    is_active = models.BooleanField(default=True)
    is_obligatoire = models.BooleanField(
        _("obligatoire"),
        default=False,
        help_text=_("Étape obligatoire pour valider la phase"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("étape de roadmap")
        verbose_name_plural = _("étapes de roadmap")
        ordering = ["phase", "ordre", "titre"]
        indexes = [
            models.Index(fields=["phase", "is_active"]),
            models.Index(fields=["categorie"]),
        ]

    def __str__(self):
        return f"[{self.phase}] {self.titre}"


class EtapePersonnelleEtudiant(models.Model):
    """
    Étape personnalisée pour un étudiant spécifique.
    Peut être :
    - Une instance d'une EtapeRoadmap générique (etape_generique_id renseigné)
    - Une étape créée sur mesure par l'étudiant ou son conseiller (etape_generique_id=null)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="etapes_roadmap",
        verbose_name=_("étudiant"),
    )
    etape_generique = models.ForeignKey(
        EtapeRoadmap,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="instances_etudiants",
        verbose_name=_("étape générique (template)"),
    )
    # Champs personnalisables
    phase = models.CharField(_("phase"), max_length=15, choices=PhaseRoadmap.choices)
    categorie = models.CharField(
        _("catégorie"),
        max_length=20,
        choices=CategorieEtape.choices,
        default=CategorieEtape.DECOUVERTE,
    )
    titre = models.CharField(_("titre"), max_length=255)
    description = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)
    # Statut
    statut = models.CharField(
        _("statut"),
        max_length=15,
        choices=StatutEtape.choices,
        default=StatutEtape.NON_COMMENCE,
    )
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateTimeField(blank=True, null=True)
    date_objectif = models.DateTimeField(
        _("date objectif"),
        blank=True,
        null=True,
        help_text=_("Date à laquelle l'étudiant vise de compléter l'étape"),
    )
    date_completion = models.DateTimeField(blank=True, null=True)
    # Notes
    notes_personnelles = models.TextField(blank=True)
    # Conseiller assigné (peut suivre l'étape avec l'étudiant)
    conseiller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="etapes_roadmap_supervisees",
        verbose_name=_("conseiller"),
    )

    class Meta:
        verbose_name = _("étape personnelle d'étudiant")
        verbose_name_plural = _("étapes personnelles d'étudiants")
        ordering = ["phase", "ordre", "date_objectif"]
        indexes = [
            models.Index(fields=["etudiant", "phase", "statut"]),
            models.Index(fields=["date_objectif"]),
        ]

    def __str__(self):
        return f"{self.etudiant.email} — {self.titre} ({self.statut})"

    def marquer_complete(self):
        from django.utils import timezone
        self.statut = StatutEtape.COMPLETE
        self.date_completion = timezone.now()
        self.save(update_fields=["statut", "date_completion"])

    def marquer_en_cours(self):
        from django.utils import timezone
        if self.statut == StatutEtape.NON_COMMENCE:
            self.date_debut = timezone.now()
        self.statut = StatutEtape.EN_COURS
        self.save(update_fields=["statut", "date_debut"])


class JalonRoadmap(models.Model):
    """
    Jalon clé d'une roadmap — date fixe à laquelle un événement se produit
    (ex: ouverture des inscriptions Parcoursup, concours national, etc.).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(_("nom"), max_length=255)
    description = models.TextField(blank=True)
    phase = models.CharField(_("phase"), max_length=15, choices=PhaseRoadmap.choices)
    date_evenement = models.DateField(_("date de l'événement"), db_index=True)
    # Périmètre
    is_national = models.BooleanField(_("national"), default=True)
    pays = models.CharField(max_length=100, default="Togo")
    ville = models.CharField(max_length=100, blank=True)
    # Lien
    url_inscription = models.URLField(blank=True)
    # Récurrence (pour les événements annuels)
    is_annuel = models.BooleanField(_("annuel"), default=False)
    # Étudiants concernés
    concerne_tous = models.BooleanField(
        _("concerne tous les étudiants de la phase"),
        default=True,
    )
    etudiants_cibles = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="jalons_roadmap",
        verbose_name=_("étudiants ciblés"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("jalon de roadmap")
        verbose_name_plural = _("jalons de roadmap")
        ordering = ["date_evenement"]

    def __str__(self):
        return f"{self.nom} ({self.date_evenement:%d/%m/%Y})"
