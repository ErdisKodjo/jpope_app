"""
Modèle Résultat de test avec analyse détaillée.

🔒 Sécurité : l'interprétation et les scores par dimension sont chiffrés au repos (Fernet).
Conformément au cahier des charges (section 3 — Sécurité) :
"Chiffrement de bout en bout des données sensibles (notes scolaires, rapports psychologiques)."
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from apps.compliance.encryption_fields import EncryptedTextField, EncryptedJSONField

class ResultatTest(models.Model):
    """
    Résultat final d'un test d'orientation.
    Créé automatiquement par le ScoringService après complétion.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Lien
    reponse_utilisateur = models.OneToOneField(
        "orientation.ReponseUtilisateur",
        on_delete=models.CASCADE,
        related_name="resultat",
        verbose_name=_("réponse utilisateur"),
    )

    # Scores
    score_global = models.FloatField(
        _("score global (0-100)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    scores_par_dimension = EncryptedJSONField(
        _("scores par dimension (0-100 chacun)"),
        default=dict,
        help_text=_(
            "Ex: {'R': 75, 'I': 82, 'A': 45, 'S': 68, 'E': 55, 'C': 60}"
        ),
    )

    # Profil RIASEC
    code_holland = models.CharField(
        _("code profil (Holland ou multi-domaine)"),
        max_length=15,
        blank=True,
        help_text=_("Ex: 'IRE' (RIASEC) ou 'N-ENV-I' (multi-domaine)"),
    )
    profil_dominant = models.CharField(
        _("dimension dominante"),
        max_length=5,
        blank=True,
    )
    profil_secondaire = models.CharField(
        _("dimension secondaire"),
        max_length=5,
        blank=True,
    )

    # Interprétation
    interpretation = EncryptedTextField(
        _("interprétation du résultat"),
        blank=True,
        help_text=_("Texte explicatif généré pour l'étudiant (chiffré au repos)"),
    )
    forces = models.JSONField(
        _("forces identifiées"),
        default=list,
        blank=True,
    )
    axes_amelioration = models.JSONField(
        _("axes d'amélioration"),
        default=list,
        blank=True,
    )

    # Comparaison avec les précédents tests
    evolution_vs_precedent = models.JSONField(
        _("évolution vs test précédent"),
        default=dict,
        blank=True,
        help_text=_(
            "Ex: {'R': +5, 'I': -2, 'A': +10} — "
            "Différence avec le test précédent du même type"
        ),
    )

    # Timestamps
    date_calcul = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("résultat de test")
        verbose_name_plural = _("résultats de tests")
        ordering = ["-date_calcul"]

    def __str__(self):
        return (
            f"Résultat {self.code_holland} — "
            f"{self.reponse_utilisateur.etudiant.get_full_name()}"
        )

    @property
    def dimension_dominante_nom(self) -> str:
        """Nom complet de la dimension dominante."""
        from .enums import TypeDimension
        mapping = {c.value: c.label for c in TypeDimension}
        return mapping.get(self.profil_dominant, self.profil_dominant)

    @property
    def top_3_dimensions(self) -> list:
        """Retourne les 3 dimensions avec les scores les plus élevés."""
        if not self.scores_par_dimension:
            return []
        sorted_dims = sorted(
            self.scores_par_dimension.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_dims[:3]
