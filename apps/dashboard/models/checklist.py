"""
Modèle ChecklistInscription — étapes à suivre pour une inscription.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class ChecklistItem(models.Model):
    """
    Élément de checklist générique (template).
    Peut être associé à un type de formation ou établissement.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    titre = models.CharField(_("titre"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    ordre = models.PositiveIntegerField(_("ordre"), default=0)

    # Association optionnelle
    formation = models.ForeignKey(
        "catalog.Formation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="checklist_items",
        verbose_name=_("formation associée"),
    )
    etablissement = models.ForeignKey(
        "catalog.Etablissement",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="checklist_items",
        verbose_name=_("établissement associé"),
    )

    # Documentation
    lien_utile = models.URLField(_("lien utile"), blank=True)
    documents_requis = models.JSONField(
        _("documents requis"),
        default=list,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("élément de checklist")
        verbose_name_plural = _("éléments de checklist")
        ordering = ["ordre"]

    def __str__(self):
        return self.titre

class ChecklistUtilisateur(models.Model):
    """
    Instance de checklist pour un utilisateur spécifique.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    utilisateur = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="checklists",
        verbose_name=_("utilisateur"),
    )
    item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.CASCADE,
        related_name="instances_utilisateur",
        verbose_name=_("élément"),
    )
    voeu = models.ForeignKey(
        "dashboard.Voeu",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="checklist_items",
        verbose_name=_("voeu associé"),
    )

    # État
    est_fait = models.BooleanField(_("fait"), default=False)
    date_fait = models.DateTimeField(_("date de complétion"), blank=True, null=True)
    notes = models.TextField(_("notes"), blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("checklist utilisateur")
        verbose_name_plural = _("checklists utilisateur")
        constraints = [
            models.UniqueConstraint(
                fields=["utilisateur", "item", "voeu"],
                name="unique_checklist_instance",
            )
        ]

    def __str__(self):
        status = "[x]" if self.est_fait else "[ ]"
        return f"{status} {self.item.titre}"

    @property
    def progression(self) -> int:
        return 100 if self.est_fait else 0
