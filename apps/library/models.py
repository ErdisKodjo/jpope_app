"""
Modèles de la Bibliothèque numérique.

Conformément au cahier des charges (section 2.4 — Espace Commun et Apprentissage) :
"Bibliothèque Numérique : Base de connaissances centralisée regroupant des manuels
scolaires, des annales d'examens corrigées et des cours de préparation aux filières
du supérieur."

Modèles :
1. TypeRessource — enum (MANUEL, ANNALE, COURS_PREP, FICHE_REVISION, VIDEO, PODCAST)
2. RessourcePedagogique — ressource de la bibliothèque
3. TelechargementRessource — trace des téléchargements (analytics + RGPD)
4. FavoriBibliotheque — favoris utilisateur
5. CategorieBibliotheque — arbre de catégories
"""
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class TypeRessource(models.TextChoices):
    """Types de ressources pédagogiques disponibles dans la bibliothèque."""
    MANUEL = "MANUEL", _("Manuel scolaire")
    ANNALE = "ANNALE", _("Annale d'examen corrigée")
    COURS_PREP = "COURS_PREP", _("Cours de préparation au supérieur")
    FICHE_REVISION = "FICHE_REVISION", _("Fiche de révision")
    VIDEO = "VIDEO", _("Vidéo pédagogique")
    PODCAST = "PODCAST", _("Podcast éducatif")
    EXERCICE = "EXERCICE", _("Série d'exercices")
    DOCUMENT_RECHERCHE = "DOCUMENT_RECHERCHE", _("Document de recherche / article")


class NiveauScolaire(models.TextChoices):
    """Niveaux scolaires couverts par la bibliothèque."""
    COLLEGE = "COLLEGE", _("Collège (6e à 3e)")
    SECONDE = "SECONDE", _("Seconde")
    PREMIERE = "PREMIERE", _("Première")
    TERMINALE = "TERMINALE", _("Terminale")
    POST_BAC = "POST_BAC", _("Post-Bac (L1, L2, L3)")
    MASTER = "MASTER", _("Master / Cycle ingénieur")
    PREPA_CONCOURS = "PREPA_CONCOURS", _("Préparation aux concours")


class CategorieBibliotheque(models.Model):
    """
    Catégorie arborescente pour organiser les ressources
    (ex: Mathématiques > Algèbre > Équations du second degré).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(_("nom"), max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sous_categories",
        verbose_name=_("catégorie parente"),
    )
    description = models.TextField(blank=True)
    icone = models.CharField(
        _("icône"),
        max_length=50,
        blank=True,
        help_text=_("Nom de l'icône Font Awesome ou emoji"),
    )
    ordre = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("catégorie de bibliothèque")
        verbose_name_plural = _("catégories de bibliothèque")
        ordering = ["ordre", "nom"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.nom} › {self.nom}"
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class RessourcePedagogique(models.Model):
    """
    Ressource pédagogique de la bibliothèque (manuel, annale, cours, etc.).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(_("titre"), max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    description = models.TextField(_("description"))
    description_courte = models.CharField(max_length=500, blank=True)

    # Type et catégorie
    type = models.CharField(
        _("type de ressource"),
        max_length=20,
        choices=TypeRessource.choices,
        db_index=True,
    )
    categorie = models.ForeignKey(
        CategorieBibliotheque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ressources",
        verbose_name=_("catégorie"),
    )

    # Niveau et matière
    niveaux = models.JSONField(
        _("niveaux scolaires"),
        default=list,
        help_text=_("Liste de NiveauScolaire.values ciblés"),
    )
    matiere = models.CharField(
        _("matière"),
        max_length=100,
        blank=True,
        help_text=_("Ex: Mathématiques, Physique, SVT, Histoire, etc."),
    )

    # Fichier et prévisualisation
    fichier = models.FileField(
        _("fichier"),
        upload_to="bibliotheque/ressources/%Y/%m/",
        max_length=500,
    )
    fichier_taille_mo = models.FloatField(
        _("taille du fichier (Mo)"),
        default=0,
        help_text=_("Calculé automatiquement à l'upload"),
    )
    url_externe = models.URLField(
        _("URL externe"),
        blank=True,
        help_text=_("Si la ressource est hébergée ailleurs (YouTube, etc.)"),
    )
    apercu = models.ImageField(
        _("aperçu"),
        upload_to="bibliotheque/apercus/%Y/%m/",
        blank=True,
        null=True,
    )

    # Métadonnées pédagogiques
    auteur = models.CharField(_("auteur"), max_length=255, blank=True)
    editeur = models.CharField(_("éditeur"), max_length=255, blank=True)
    annee_publication = models.PositiveIntegerField(
        _("année de publication"),
        blank=True,
        null=True,
    )
    isbn = models.CharField(_("ISBN"), max_length=20, blank=True)
    langue = models.CharField(max_length=10, default="fr")
    nombre_pages = models.PositiveIntegerField(
        _("nombre de pages"),
        blank=True,
        null=True,
    )
    duree_minutes = models.PositiveIntegerField(
        _("durée (minutes)"),
        blank=True,
        null=True,
        help_text=_("Pour les vidéos et podcasts"),
    )

    # Restrictions d'accès (freemium)
    is_premium = models.BooleanField(
        _("premium"),
        default=False,
        help_text=_("Réservé aux abonnés Premium"),
    )
    is_free = models.BooleanField(
        _("gratuit"),
        default=True,
        help_text=_("Accessible gratuitement"),
    )

    # Qualité et stats
    note_moyenne = models.FloatField(
        _("note moyenne (0-5)"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    nombre_votes = models.PositiveIntegerField(default=0)
    nombre_telechargements = models.PositiveIntegerField(default=0)
    nombre_vues = models.PositiveIntegerField(default=0)

    # Modération
    is_verified = models.BooleanField(
        _("vérifié"),
        default=False,
        help_text=_("Contenu vérifié par l'équipe éditoriale"),
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(_("mis en avant"), default=False)

    # Conforme programme officiel
    programme_officiel = models.BooleanField(
        _("conforme au programme officiel"),
        default=False,
    )

    # Soumetteur et timestamps
    soumis_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ressources_soumises",
        verbose_name=_("soumis par"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("ressource pédagogique")
        verbose_name_plural = _("ressources pédagogiques")
        ordering = ["-nombre_telechargements", "-created_at"]
        indexes = [
            models.Index(fields=["type", "is_active"]),
            models.Index(fields=["matiere", "niveaux"]),
            models.Index(fields=["-note_moyenne"]),
            models.Index(fields=["is_premium", "is_free"]),
        ]

    def __str__(self):
        return f"{self.titre} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            counter = 1
            while RessourcePedagogique.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Calcule la taille si fichier présent
        if self.fichier and not self.fichier_taille_mo:
            try:
                self.fichier_taille_mo = round(self.fichier.size / (1024 * 1024), 2)
            except Exception:
                pass
        super().save(*args, **kwargs)

    @property
    def est_accessible_premium(self):
        """Indique si la ressource est réservée aux Premium."""
        return self.is_premium and not self.is_free


class TelechargementRessource(models.Model):
    """Trace chaque téléchargement (analytics + RGPD)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telechargements_biblio",
    )
    ressource = models.ForeignKey(
        RessourcePedagogique,
        on_delete=models.CASCADE,
        related_name="historique_telechargements",
    )
    date_telechargement = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = _("téléchargement")
        verbose_name_plural = _("téléchargements")
        ordering = ["-date_telechargement"]
        indexes = [
            models.Index(fields=["utilisateur", "-date_telechargement"]),
            models.Index(fields=["ressource", "-date_telechargement"]),
        ]


class FavoriBibliotheque(models.Model):
    """Ressources favorites de l'utilisateur (bibliothèque personnelle)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favoris_biblio",
    )
    ressource = models.ForeignKey(
        RessourcePedagogique,
        on_delete=models.CASCADE,
        related_name="favoris_de",
    )
    date_ajout = models.DateTimeField(auto_now_add=True)
    note_personnelle = models.TextField(
        _("note personnelle"),
        blank=True,
        help_text=_("Annotation personnelle de l'utilisateur"),
    )

    class Meta:
        verbose_name = _("favori bibliothèque")
        verbose_name_plural = _("favoris bibliothèque")
        unique_together = ("utilisateur", "ressource")
        ordering = ["-date_ajout"]


class VoteRessource(models.Model):
    """Vote (note 1-5) d'un utilisateur sur une ressource."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="votes_ressources",
    )
    ressource = models.ForeignKey(
        RessourcePedagogique,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    note = models.PositiveSmallIntegerField(
        _("note (1-5)"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    commentaire = models.TextField(blank=True)
    date_vote = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("vote ressource")
        verbose_name_plural = _("votes ressources")
        unique_together = ("utilisateur", "ressource")
        ordering = ["-date_vote"]
