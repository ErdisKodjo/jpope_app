# -*- coding: utf-8 -*-
"""
Commande de seed en masse — AvenSU-Orienta
Insère : 10 domaines, 20 établissements (dont IPNET), ~32 métiers, 200 formations,
8 événements, 11 forums, 10 classements, 5 conseillers.

INSTALLATION
------------
1. Copier ce fichier dans : <votre_app>/management/commands/seed_data.py
   (créer les dossiers management/ et management/commands/ avec un __init__.py vide dans chacun,
   si ce n'est pas déjà fait). Exemple : catalog/management/commands/seed_data.py
2. Copier data.py à la racine du même dossier que seed_data.py, OU ajuster l'import
   ci-dessous (`from . import data` suppose que data.py est dans le même dossier).
3. Adapter la constante APPS ci-dessous (ligne "MODELES À ADAPTER") si vos noms
   d'app/modèle diffèrent des noms déduits du guide insertion_donnees.md.
4. Dézipper le contenu du dossier media/ fourni à la racine de votre MEDIA_ROOT
   (généralement <projet>/media/).
5. Lancer : python manage.py seed_data
   Options : --flush (vide les tables concernées avant de réinsérer)

Le script est idempotent : il utilise get_or_create sur les champs naturels
(slug / email) donc peut être relancé sans dupliquer les données.
"""
import sys
import os
from decimal import Decimal
from datetime import datetime
from django.utils.timezone import make_aware

from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify
from django.apps import apps
from django.conf import settings
from django.db import transaction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as seed  # data.py doit être placé à côté de ce fichier


# ─────────────────────────────────────────────────────────────
# MODELES À ADAPTER : ajustez ces chemins "app_label.ModelName"
# si vos noms diffèrent de ceux déduits du guide.
# ─────────────────────────────────────────────────────────────
MODEL_PATHS = {
    "Domaine": "catalog.Domaine",
    "Etablissement": "catalog.Etablissement",
    "Metier": "catalog.Metier",
    "Formation": "catalog.Formation",
    "Evenement": "events.Evenement",
    "Forum": "community.Forum",
    "Classement": "ranking.Classement",
    "User": settings.AUTH_USER_MODEL,
    "CounselorProfile": "accounts.CounselorProfile",
}


def get_model(key):
    path = MODEL_PATHS[key]
    app_label, model_name = path.split(".")
    return apps.get_model(app_label, model_name)


def media_path(*parts):
    # commands/ → management/ → catalog/ → apps/ → projet root/ → media/
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "media", *parts)


class Command(BaseCommand):
    help = "Insère en masse les données du Seed Pack (20 établissements, 200 formations, 32 métiers, etc.)"

    def add_arguments(self, parser):
        parser.add_argument("--skip-images", action="store_true", help="Ne pas attacher les images (plus rapide)")

    @transaction.atomic
    def handle(self, *args, **options):
        skip_images = options["skip_images"]

        Domaine = get_model("Domaine")
        Etablissement = get_model("Etablissement")
        Metier = get_model("Metier")
        Formation = get_model("Formation")
        Evenement = get_model("Evenement")
        Forum = get_model("Forum")
        Classement = get_model("Classement")
        User = get_model("User")
        CounselorProfile = get_model("CounselorProfile")

        # ── 1. DOMAINES ──────────────────────────────────────────
        self.stdout.write("→ Domaines…")
        domaines_map = {}
        for d in seed.DOMAINES:
            obj, _ = Domaine.objects.get_or_create(
                slug=d["slug"],
                defaults=dict(
                    nom=d["nom"], description=d["description"], icon=d["icon"],
                    couleur=d["couleur"], is_active=True, ordre=d["ordre"],
                ),
            )
            domaines_map[d["slug"]] = obj
        self.stdout.write(self.style.SUCCESS(f"  {len(domaines_map)} domaines OK"))

        # ── 2. ÉTABLISSEMENTS ────────────────────────────────────
        self.stdout.write("→ Établissements…")
        etabs_map = {}
        for e in seed.ETABLISSEMENTS:
            obj, created = Etablissement.objects.get_or_create(
                slug=e["slug"],
                defaults=dict(
                    nom=e["nom"], sigle=e["sigle"],
                    description=e.get("description_extra") or
                        f"{e['nom']} ({e['sigle']}) est un établissement {e['type'].replace('_', ' ').lower()} "
                        f"basé à {e['ville']}, fondé en {e['date_creation']}.",
                    description_courte=f"{e['nom']} — {e['ville']}, Togo.",
                    type=e["type"], statut=e["statut"], date_creation=e["date_creation"],
                    ville=e["ville"], pays="Togo",
                    latitude=Decimal(str(e["latitude"])), longitude=Decimal(str(e["longitude"])),
                    frais_inscription_min=e["frais_min"], frais_inscription_max=e["frais_max"],
                    frais_scolarite_annuel_min=e["scol_min"], frais_scolarite_annuel_max=e["scol_max"],
                    nombre_etudiants=e["nb_etudiants"], nombre_enseignants=e["nb_enseignants"],
                    taux_encadrement=round(e["nb_etudiants"] / max(e["nb_enseignants"], 1), 1),
                    note_globale=Decimal(str(e["note"])),
                    classement_national=e["classement_national"],
                    equipements=["Bibliothèque", "Wifi", "Laboratoire informatique", "Cafétéria"],
                    labels_qualite=["Reconnu par l'État togolais"],
                    propose_bourses=True, montant_bourse_max=300000,
                    criteres_bourses=["Mérite", "Ressources limitées"],
                    residences_universitaires=e["type"] == "PUBLIC",
                    clubs_et_associations=["Club Informatique", "Association des Étudiants"],
                    sports_proposes=["Football", "Basketball"],
                    is_verified=True, is_featured=e.get("featured", False),
                ),
            )
            if not skip_images:
                logo_path = media_path("etablissements", "logos", "2026", f"logo_{e['sigle']}.png")
                banniere_path = media_path("etablissements", "bannieres", "2026", f"banniere_{e['sigle']}.jpg")
                if created or not obj.logo:
                    if os.path.exists(logo_path):
                        with open(logo_path, "rb") as f:
                            obj.logo.save(f"logo_{e['sigle']}.png", File(f), save=False)
                if created or not obj.banniere:
                    if os.path.exists(banniere_path):
                        with open(banniere_path, "rb") as f:
                            obj.banniere.save(f"banniere_{e['sigle']}.jpg", File(f), save=False)
                obj.save()
            # M2M domaines
            obj.domaines_enseignes.set([domaines_map[s] for s in e["domaines"] if s in domaines_map])
            etabs_map[e["sigle"]] = obj
        self.stdout.write(self.style.SUCCESS(f"  {len(etabs_map)} établissements OK"))

        # ── 3. MÉTIERS ───────────────────────────────────────────
        self.stdout.write("→ Métiers…")
        metiers_map = {}
        for m in seed.METIERS:
            obj, _ = Metier.objects.get_or_create(
                slug=m["slug"],
                defaults=dict(
                    nom=m["nom"], domaine=domaines_map[m["domaine"]],
                    description=f"{m['nom']} : métier en demande {m['demande'].replace('_', ' ').lower()} "
                                 f"nécessitant un niveau {m['niveau']}.",
                    description_courte=f"{m['nom']} — revenu moyen {m['revenu_moyen']:,} FCFA/mois".replace(",", " "),
                    revenu_min=m["revenu_min"], revenu_max=m["revenu_max"], revenu_moyen=m["revenu_moyen"],
                    taux_emploi=m["taux_emploi"], demande_marche=m["demande"],
                    niveau_etude_requis=m["niveau"], duree_formation_typique_annees=3,
                    competences_cles=m["competences"],
                    taches_principales=[f"Activité principale liée à {m['nom'].lower()}"],
                    pays_concernes=m["pays_concernes"], villes_principales=m["villes_principales"],
                    source_donnees=m["source_donnees"], date_mise_a_jour=m["date_mise_a_jour"],
                ),
            )
            metiers_map[m["slug"]] = obj
        self.stdout.write(self.style.SUCCESS(f"  {len(metiers_map)} métiers OK"))

        # ── 4. FORMATIONS ────────────────────────────────────────
        self.stdout.write("→ Formations (peut prendre quelques secondes)…")
        count = 0
        for f in seed.FORMATIONS:
            slug = slugify(f"{f['nom']}-{f['etablissement']}")
            obj, _ = Formation.objects.get_or_create(
                slug=slug,
                defaults=dict(
                    nom=f["nom"], etablissement=etabs_map[f["etablissement"]],
                    domaine=domaines_map[f["domaine"]],
                    description=f"{f['nom']} dispensée à {etabs_map[f['etablissement']].nom}. "
                                 f"Programme : {', '.join(f['programmes'][:3])}.",
                    description_courte=f"{f['nom']} — {f['duree_annees']} an(s), {etabs_map[f['etablissement']].sigle}.",
                    niveau=f["niveau"], duree_annees=f["duree_annees"], modalite=f["modalite"],
                    cout_annuel=f["cout_annuel"], frais_inscription=f["frais_inscription"],
                    frais_dossier=f["frais_dossier"], bourses_disponibles=f["bourses_disponibles"],
                    montant_bourse_max=f["montant_bourse_max"], facilites_paiement=True,
                    importance_strategique=f["importance_strategique"],
                    taux_reussite=f["taux_reussite"], taux_insertion_6mois=f["taux_insertion_6mois"],
                    taux_insertion_12mois=f["taux_insertion_12mois"], salaire_sortie_moyen=f["salaire_sortie_moyen"],
                    prerequis=[f"Niveau {f['niveau']} requis"], serie_bac_admises=f["serie_bac_admises"],
                    programmes=f["programmes"], dates_rentree=f["dates_rentree"],
                    date_limite_inscription=f["date_limite_inscription"],
                    places_disponibles=f["places_disponibles"], is_featured=f["is_featured"],
                ),
            )
            debouches = [metiers_map[s] for s in f["debouches_metiers"] if s in metiers_map]
            if debouches:
                obj.debouches.set(debouches)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"  {count} formations OK"))

        # ── 5. ÉVÉNEMENTS ────────────────────────────────────────
        self.stdout.write("→ Événements…")
        for ev in seed.EVENEMENTS:
            obj, created = Evenement.objects.get_or_create(
                slug=ev["slug"],
                defaults=dict(
                    titre=ev["titre"], description=ev["description_courte"] + " Programme détaillé communiqué "
                                                                              "aux participants inscrits.",
                    description_courte=ev["description_courte"], type=ev["type"], format=ev.get("format", "PRESENTIEL"),
                    statut=ev["statut"], cible="TOUS", priorite="NORMALE",
                    date_debut=make_aware(datetime.fromisoformat(ev["date_debut"])),
                    date_fin=make_aware(datetime.fromisoformat(ev["date_fin"])) if ev.get("date_fin") else None,
                    lieu_nom=ev.get("lieu_nom") or "", ville=ev.get("ville") or "",
                    capacite_max=ev.get("capacite_max", 0), inscriptions_ouvertes=True,
                    est_gratuit=True, cout_participation=0,
                    etablissement=etabs_map.get(ev["etab"]) if ev.get("etab") else None,
                    tags=ev["tags"],
                ),
            )
            if not skip_images:
                img_path = media_path("evenements", "2026", "07", f"evt_{ev['slug']}.jpg")
                cover_path = media_path("evenements", "couvertures", "2026", "07", f"cover_{ev['slug']}.jpg")
                if os.path.exists(img_path) and (created or not obj.image_principale):
                    with open(img_path, "rb") as f:
                        obj.image_principale.save(f"evt_{ev['slug']}.jpg", File(f), save=False)
                if os.path.exists(cover_path) and (created or not obj.image_couverture):
                    with open(cover_path, "rb") as f:
                        obj.image_couverture.save(f"cover_{ev['slug']}.jpg", File(f), save=False)
                obj.save()
        self.stdout.write(self.style.SUCCESS(f"  {len(seed.EVENEMENTS)} événements OK"))

        # ── 6. FORUMS ────────────────────────────────────────────
        self.stdout.write("→ Forums…")
        for fo in seed.FORUMS:
            Forum.objects.get_or_create(
                slug=fo["slug"],
                defaults=dict(
                    nom=fo["nom"], description=f"Espace d'échange : {fo['nom']}.",
                    icone=fo["icone"], couleur="#3B82F6", type=fo["type"],
                    domaine=domaines_map.get(fo["domaine"]) if fo.get("domaine") else None,
                    etablissement=etabs_map.get(fo["etab"]) if fo.get("etab") else None,
                    moderation_auto=False, acces_restreint=False,
                    is_active=True, is_featured=False, ordre=fo["ordre"],
                ),
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(seed.FORUMS)} forums OK"))

        # ── 7. CLASSEMENTS ───────────────────────────────────────
        self.stdout.write("→ Classements…")
        for c in seed.CLASSEMENTS:
            Classement.objects.get_or_create(
                etablissement=etabs_map[c["etab"]], annee=c["annee"],
                defaults=dict(
                    rang_national=c["rang_national"], score_final=c["score_final"],
                    details_scores=c["details"],
                ),
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(seed.CLASSEMENTS)} classements OK"))

        # ── 8. CONSEILLERS ───────────────────────────────────────
        self.stdout.write("→ Conseillers…")
        for co in seed.CONSEILLERS:
            user, created = User.objects.get_or_create(
                email=co["email"],
                defaults=dict(first_name=co["prenom"], last_name=co["nom"], role="COUNSELOR", is_active=True),
            )
            if created:
                user.set_password("AvenSU2026!")
                user.save()
            if not skip_images:
                avatar_path = media_path("avatars", f"avatar_{slugify(co['prenom'])}_{slugify(co['nom'])}.jpg")
                if os.path.exists(avatar_path) and hasattr(user, "avatar") and not user.avatar:
                    with open(avatar_path, "rb") as f:
                        user.avatar.save(os.path.basename(avatar_path), File(f), save=True)
            CounselorProfile.objects.get_or_create(
                user=user,
                defaults=dict(
                    specialites=co["spec"], qualifications=co["qualifications"],
                    annees_experience=co["exp"], tarif_consultation=co["tarif"],
                    bio=co["bio"], is_available=True,
                ),
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(seed.CONSEILLERS)} conseillers OK "
                                               f"(mot de passe par défaut : AvenSU2026!)"))

        self.stdout.write(self.style.SUCCESS("\n✅ Seed terminé avec succès."))
