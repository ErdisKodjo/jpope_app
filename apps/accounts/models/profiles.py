"""
Profils spécifiques selon le rôle de l'utilisateur.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from .enums import SerieBac
from .user import User


class StudentProfile(models.Model):
    """Profil détaillé d'un étudiant."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        verbose_name=_("utilisateur"),
    )

    # Informations scolaires
    serie_bac = models.CharField(
        _("série de bac"),
        max_length=10,
        choices=SerieBac.choices,
        blank=True,
    )
    annee_bac = models.PositiveIntegerField(
        _("année du bac"),
        blank=True,
        null=True,
        validators=[MinValueValidator(2000), MaxValueValidator(2030)],
    )
    moyenne_generale = models.DecimalField(
        _("moyenne générale"),
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    mentions_obtenues = models.JSONField(
        _("mentions obtenues"),
        default=list,
        blank=True,
        help_text=_("Ex: ['Passable', 'Assez Bien']"),
    )

    # Établissement scolaire actuel
    etablissement_scolaire = models.CharField(
        _("lycée/établissement actuel"),
        max_length=255,
        blank=True,
    )
    ville_etablissement = models.CharField(
        _("ville de l'établissement"),
        max_length=100,
        blank=True,
    )

    # Préférences et contraintes
    centres_interet = models.JSONField(
        _("centres d'intérêt"),
        default=list,
        blank=True,
        help_text=_("Liste des domaines d'intérêt"),
    )
    matieres_fortes = models.JSONField(
        _("matières fortes"),
        default=list,
        blank=True,
    )
    matieres_faibles = models.JSONField(
        _("matières faibles"),
        default=list,
        blank=True,
    )

    # Contraintes
    contraintes_financieres = models.BooleanField(
        _("contraintes financières"),
        default=False,
    )
    budget_max_annuel = models.DecimalField(
        _("budget max annuel (FCFA)"),
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
    )
    mobilite_geographique = models.BooleanField(
        _("mobilité géographique"),
        default=True,
    )
    villes_preferees = models.JSONField(
        _("villes préférées"),
        default=list,
        blank=True,
    )

    # Projet professionnel
    projet_professionnel = models.TextField(
        _("projet professionnel"),
        blank=True,
    )
    metiers_envisages = models.JSONField(
        _("métiers envisagés"),
        default=list,
        blank=True,
    )

    # Statistiques
    nombre_tests_passes = models.PositiveIntegerField(default=0)
    dernier_test_date = models.DateTimeField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil étudiant")
        verbose_name_plural = _("profils étudiants")

    def __str__(self):
        return f"Profil étudiant de {self.user.get_full_name()}"

    @property
    def is_complete(self):
        """Vérifie si le profil est suffisamment complet."""
        required_fields = [
            self.serie_bac,
            self.annee_bac,
            self.centres_interet,
        ]
        return all(required_fields)


class CounselorProfile(models.Model):
    """Profil d'un conseiller d'orientation."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="counselor_profile",
        verbose_name=_("utilisateur"),
    )

    # Informations professionnelles
    specialites = models.JSONField(
        _("spécialités"),
        default=list,
        blank=True,
        help_text=_("Domaines de spécialisation"),
    )
    qualifications = models.TextField(
        _("qualifications/diplômes"),
        blank=True,
    )
    annees_experience = models.PositiveIntegerField(
        _("années d'expérience"),
        default=0,
    )
    numero_agrement = models.CharField(
        _("numéro d'agrément"),
        max_length=100,
        blank=True,
    )

    # Établissements suivis
    etablissements_suivis = models.ManyToManyField(
        "catalog.Etablissement",
        blank=True,
        related_name="conseillers",
        verbose_name=_("établissements suivis"),
    )

    # Statistiques
    nombre_eleves_suivis = models.PositiveIntegerField(default=0)
    nombre_accompagnements_total = models.PositiveIntegerField(
        _("nombre total d'accompagnements"),
        default=0,
    )
    nombre_accompagnements_actifs = models.PositiveIntegerField(
        _("nombre d'accompagnements actifs"),
        default=0,
    )

    # Notation
    note_moyenne = models.FloatField(
        _("note moyenne (0-5)"),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    nombre_evaluations = models.PositiveIntegerField(
        _("nombre d'évaluations reçues"),
        default=0,
    )

    # Disponibilité
    is_available = models.BooleanField(
        _("disponible pour mentorat"),
        default=True,
    )
    tarif_consultation = models.DecimalField(
        _("tarif consultation (FCFA)"),
        max_digits=10,
        decimal_places=0,
        blank=True,
        null=True,
    )
    taux_ristourne = models.FloatField(
        _("taux de ristourne (%)"),
        default=10.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Pourcentage du tarif consultation reversé comme commission"),
    )
    solde_ristournes = models.DecimalField(
        _("solde ristournes (FCFA)"),
        max_digits=12,
        decimal_places=0,
        default=0,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil conseiller")
        verbose_name_plural = _("profils conseillers")

    def __str__(self):
        return f"Conseiller {self.user.get_full_name()}"


class SchoolRepProfile(models.Model):
    """Profil d'un représentant d'établissement."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="school_rep_profile",
        verbose_name=_("utilisateur"),
    )

    # Lien avec l'établissement
    etablissement = models.OneToOneField(
        "catalog.Etablissement",
        on_delete=models.CASCADE,
        related_name="representant",
        verbose_name=_("établissement représenté"),
    )

    # Informations professionnelles
    poste = models.CharField(
        _("poste/fonction"),
        max_length=100,
    )
    telephone_pro = models.CharField(
        _("téléphone professionnel"),
        max_length=20,
        blank=True,
    )
    date_nomination = models.DateField(
        _("date de nomination"),
        blank=True,
        null=True,
    )

    # Permissions
    can_publish_events = models.BooleanField(
        _("peut publier des événements"),
        default=True,
    )
    can_edit_formation = models.BooleanField(
        _("peut modifier les formations"),
        default=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil représentant établissement")
        verbose_name_plural = _("profils représentants établissement")

    def __str__(self):
        return f"Représentant {self.etablissement.nom} ({self.user.get_full_name()})"


class ParentProfile(models.Model):
    """Profil d'un parent/tuteur."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent_profile",
        verbose_name=_("utilisateur"),
    )

    # Enfants suivis
    enfants_suivis = models.ManyToManyField(
        User,
        blank=True,
        related_name="parents_tuteurs",
        limit_choices_to={"role": "STUDENT"},
        verbose_name=_("enfants suivis"),
    )

    # Informations
    profession = models.CharField(
        _("profession"),
        max_length=100,
        blank=True,
    )
    preferences_orientation = models.JSONField(
        _("préférences d'orientation"),
        default=list,
        blank=True,
        help_text=_("Souhaits des parents pour l'orientation"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil parent")
        verbose_name_plural = _("profils parents")

    def __str__(self):
        return f"Parent {self.user.get_full_name()}"
