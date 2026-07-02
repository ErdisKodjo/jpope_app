"""
Modèle de notes académiques des étudiants.
"""
import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotesEtudiant(models.Model):
    """Notes académiques d'un étudiant par matière, utilisées pour affiner les recommandations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etudiant = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
        limit_choices_to={"role": "STUDENT"},
        verbose_name=_("Étudiant"),
    )

    # ── Sciences ──────────────────────────────────────────────────────────
    note_maths = models.DecimalField(
        _("Mathématiques"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    note_physique = models.DecimalField(
        _("Physique-Chimie"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    note_svt = models.DecimalField(
        _("SVT"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    note_info = models.DecimalField(
        _("Informatique / TIC"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )

    # ── Lettres & Langues ─────────────────────────────────────────────────
    note_francais = models.DecimalField(
        _("Français"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    note_anglais = models.DecimalField(
        _("Anglais"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    note_philosophie = models.DecimalField(
        _("Philosophie"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    note_histoire_geo = models.DecimalField(
        _("Histoire-Géographie"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )

    # ── Économie & Gestion ────────────────────────────────────────────────
    note_economie = models.DecimalField(
        _("Économie"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    note_comptabilite = models.DecimalField(
        _("Comptabilité"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    note_gestion = models.DecimalField(
        _("Gestion / Management"), max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )

    # ── Méta ──────────────────────────────────────────────────────────────
    annee_scolaire = models.CharField(_("Année scolaire"), max_length=9, default="2024-2025")
    classe = models.CharField(
        _("Classe"), max_length=50, blank=True,
        help_text=_("Ex : Terminale C, BTS 1ère année…"),
    )
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Notes étudiant")
        verbose_name_plural = _("Notes étudiants")

    def __str__(self):
        return f"Notes de {self.etudiant} ({self.annee_scolaire})"

    # ── Propriétés académiques ─────────────────────────────────────────────

    @property
    def _notes_sciences(self):
        return [float(n) for n in [self.note_maths, self.note_physique, self.note_svt, self.note_info] if n is not None]

    @property
    def _notes_lettres(self):
        return [float(n) for n in [self.note_francais, self.note_anglais, self.note_philosophie, self.note_histoire_geo] if n is not None]

    @property
    def _notes_economie(self):
        return [float(n) for n in [self.note_economie, self.note_comptabilite, self.note_gestion] if n is not None]

    @property
    def score_scientifique(self):
        """Moyenne des notes scientifiques (0-20)."""
        notes = self._notes_sciences
        return round(sum(notes) / len(notes), 2) if notes else None

    @property
    def score_litteraire(self):
        """Moyenne des notes littéraires (0-20)."""
        notes = self._notes_lettres
        return round(sum(notes) / len(notes), 2) if notes else None

    @property
    def score_commercial(self):
        """Moyenne des notes économie/gestion (0-20)."""
        notes = self._notes_economie
        return round(sum(notes) / len(notes), 2) if notes else None

    @property
    def profil_academique(self):
        """Retourne {domaine: ratio_0_1} pour le moteur de recommandation."""
        profil = {}
        if self.score_scientifique is not None:
            profil["sciences"] = self.score_scientifique / 20
        if self.score_litteraire is not None:
            profil["lettres"] = self.score_litteraire / 20
        if self.score_commercial is not None:
            profil["commerce"] = self.score_commercial / 20
        return profil

    @property
    def profil_dominant(self):
        """Domaine académique dominant ('sciences', 'lettres', 'commerce')."""
        profil = self.profil_academique
        return max(profil, key=profil.get) if profil else None

    @property
    def notes_renseignees(self):
        """Nombre de matières renseignées (sur 11)."""
        champs = [
            self.note_maths, self.note_physique, self.note_svt, self.note_info,
            self.note_francais, self.note_anglais, self.note_philosophie, self.note_histoire_geo,
            self.note_economie, self.note_comptabilite, self.note_gestion,
        ]
        return sum(1 for n in champs if n is not None)

    @property
    def completude_pct(self):
        """Pourcentage de complétion du profil académique."""
        return round((self.notes_renseignees / 11) * 100)
