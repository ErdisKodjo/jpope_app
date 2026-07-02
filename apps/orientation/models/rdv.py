"""Modèle RendezVous — planification des séances conseiller/étudiant."""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class StatutRendezVous(models.TextChoices):
    PROPOSE  = "PROPOSE",   _("Proposé")
    CONFIRME = "CONFIRME",  _("Confirmé")
    ANNULE   = "ANNULE",    _("Annulé")
    TERMINE  = "TERMINE",   _("Terminé")


class FormatRendezVous(models.TextChoices):
    VISIO       = "VISIO",       _("Visioconférence")
    PRESENTIEL  = "PRESENTIEL",  _("Présentiel")
    TELEPHONE   = "TELEPHONE",   _("Téléphone")


class RendezVous(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    demande = models.ForeignKey(
        "orientation.DemandeAccompagnement",
        on_delete=models.CASCADE,
        related_name="rendez_vous",
        verbose_name=_("demande associée"),
    )
    propose_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rdv_proposes",
        verbose_name=_("proposé par"),
    )

    date_rdv       = models.DateTimeField(_("date et heure"))
    duree_minutes  = models.PositiveIntegerField(_("durée (min)"), default=30)
    format         = models.CharField(
        _("format"), max_length=20,
        choices=FormatRendezVous.choices,
        default=FormatRendezVous.VISIO,
    )
    lien_visio  = models.URLField(_("lien visioconférence"), blank=True)
    adresse     = models.CharField(_("adresse (présentiel)"), max_length=300, blank=True)
    notes       = models.TextField(_("ordre du jour"), blank=True)

    statut = models.CharField(
        _("statut"), max_length=20,
        choices=StatutRendezVous.choices,
        default=StatutRendezVous.PROPOSE,
        db_index=True,
    )
    motif_annulation = models.TextField(_("motif d'annulation"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name          = _("rendez-vous")
        verbose_name_plural   = _("rendez-vous")
        ordering              = ["date_rdv"]
        indexes = [
            models.Index(fields=["demande", "statut"], name="orient_rdv_demande_statut_idx"),
            models.Index(fields=["date_rdv"],          name="orient_rdv_date_idx"),
        ]

    def __str__(self):
        return f"RDV {self.date_rdv:%d/%m/%Y %H:%M} [{self.get_statut_display()}]"

    @property
    def autre_participant(self):
        """Retourne le participant qui n'a pas proposé le RDV."""
        d = self.demande
        return d.conseiller if self.propose_par == d.etudiant else d.etudiant
