"""
Modèle Favori — entités sauvegardées par l'étudiant.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import TypeFavori
from ..managers import FavoriManager

class Favori(models.Model):
    """
    Entité mise en favori par un utilisateur.
    Utilise des FK directes pour supporter plusieurs types d'entités.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Utilisateur
    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="favoris",
        verbose_name=_("utilisateur"),
    )

    # Type d'entité
    type_entite = models.CharField(
        _("type d'entité"),
        max_length=20,
        choices=TypeFavori.choices,
    )

    # Liens polymorphes (un seul rempli selon le type)
    formation = models.ForeignKey(
        "catalog.Formation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favoris",
        verbose_name=_("formation"),
    )
    metier = models.ForeignKey(
        "catalog.Metier",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favoris",
        verbose_name=_("métier"),
    )
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favoris",
        verbose_name=_("établissement"),
    )
    evenement = models.ForeignKey(
        "events.Evenement",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favoris",
        verbose_name=_("événement"),
    )

    # Personnalisation
    note_personnelle = models.TextField(
        _("note personnelle"),
        blank=True,
        help_text=_("Notes personnelles de l'utilisateur sur ce favori"),
    )
    tags = models.JSONField(
        _("tags personnels"),
        default=list,
        blank=True,
        help_text=_("Ex: ['mon_top', 'a_visiter', 'comparer']"),
    )

    # Métadonnées
    source = models.CharField(
        _("source"),
        max_length=50,
        blank=True,
        help_text=_("D'où vient le favori : recommandation, recherche, etc."),
    )
    recommandation = models.ForeignKey(
        "orientation.Recommandation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="favoris_crees",
        verbose_name=_("recommandation d'origine"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FavoriManager()

    class Meta:
        verbose_name = _("favori")
        verbose_name_plural = _("favoris")
        ordering = ["-created_at"]
        constraints = [
            # Un utilisateur ne peut pas avoir deux fois le même favori
            models.UniqueConstraint(
                fields=["utilisateur", "type_entite", "formation"],
                name="unique_favori_formation",
                condition=models.Q(type_entite="FORMATION"),
            ),
            models.UniqueConstraint(
                fields=["utilisateur", "type_entite", "metier"],
                name="unique_favori_metier",
                condition=models.Q(type_entite="METIER"),
            ),
            models.UniqueConstraint(
                fields=["utilisateur", "type_entite", "etablissement"],
                name="unique_favori_etablissement",
                condition=models.Q(type_entite="ETABLISSEMENT"),
            ),
        ]
        indexes = [
            models.Index(fields=["utilisateur", "type_entite"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Favori {self.type_entite} — {self.utilisateur.get_full_name()}"

    @property
    def entite(self):
        """Retourne l'entité favorite."""
        return self.formation or self.metier or self.etablissement or self.evenement

    @property
    def entite_nom(self) -> str:
        entite = self.entite
        return str(entite) if entite else "N/A"
