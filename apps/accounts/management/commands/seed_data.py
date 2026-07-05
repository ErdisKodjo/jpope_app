"""
Commande de seed — peuple la BDD avec des données de démonstration réalistes.
Usage : python manage.py seed_data [--flush]
  --flush  supprime toutes les données seedées avant de recommencer
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# Données de référence
# ─────────────────────────────────────────────────────────────

DOMAINES = [
    {"nom": "Informatique & Numérique",     "icon": "💻", "couleur": "#3B82F6", "ordre": 1},
    {"nom": "Santé & Médecine",             "icon": "🏥", "couleur": "#EF4444", "ordre": 2},
    {"nom": "Droit & Sciences Politiques",  "icon": "⚖️", "couleur": "#8B5CF6", "ordre": 3},
    {"nom": "Économie & Gestion",           "icon": "📊", "couleur": "#F59E0B", "ordre": 4},
    {"nom": "Sciences de l'Ingénieur",      "icon": "⚙️", "couleur": "#6B7280", "ordre": 5},
    {"nom": "Lettres & Sciences Humaines",  "icon": "📚", "couleur": "#10B981", "ordre": 6},
    {"nom": "Agriculture & Environnement",  "icon": "🌿", "couleur": "#22C55E", "ordre": 7},
    {"nom": "Communication & Journalisme",  "icon": "📡", "couleur": "#F97316", "ordre": 8},
    {"nom": "Arts & Design",                "icon": "🎨", "couleur": "#EC4899", "ordre": 9},
    {"nom": "Éducation & Formation",        "icon": "🎓", "couleur": "#06B6D4", "ordre": 10},
]

ETABLISSEMENTS = [
    {"nom": "Université de Lomé",                          "sigle": "UL",     "type": "PUBLIC",     "statut": "ACCREDITE",  "ville": "Lomé"},
    {"nom": "Université de Kara",                          "sigle": "UK",     "type": "PUBLIC",     "statut": "AGREÉ",      "ville": "Kara"},
    {"nom": "École Supérieure de Gestion Info. & Sciences","sigle": "ESGIS",  "type": "PRIVE_LAIC", "statut": "ACCREDITE",  "ville": "Lomé"},
    {"nom": "Institut Africain de Management",             "sigle": "IAM",    "type": "PRIVE_LAIC", "statut": "AGREÉ",      "ville": "Lomé"},
    {"nom": "École Supérieure des Techniques Bio-Médicales","sigle": "ESTBA",  "type": "PRIVE_LAIC", "statut": "AUTORISE",   "ville": "Lomé"},
    {"nom": "Institut National des Sciences de Gestion",  "sigle": "INSG",   "type": "PUBLIC",     "statut": "AGREÉ",      "ville": "Lomé"},
    {"nom": "École Polytechnique de Lomé",                 "sigle": "EPL",    "type": "GRANDE_ECOLE","statut": "ACCREDITE", "ville": "Lomé"},
    {"nom": "Université Catholique de l'Afrique de l'Ouest","sigle": "UCAO",  "type": "PRIVE_CONFESSIONNEL","statut": "RECONNU","ville": "Lomé"},
    {"nom": "Institut Supérieur de Technologie",           "sigle": "IST",    "type": "PRIVE_LAIC", "statut": "AUTORISE",   "ville": "Atakpamé"},
    {"nom": "Centre de Formation Professionnelle du Togo", "sigle": "CFPT",   "type": "PUBLIC",     "statut": "AGREÉ",      "ville": "Lomé"},
]

METIERS = [
    # (nom, domaine_nom, revenu_min, revenu_moyen, revenu_max, demande)
    ("Ingénieur logiciel",         "Informatique & Numérique",    250000, 500000, 900000,  "FORTE"),
    ("Médecin généraliste",        "Santé & Médecine",            350000, 700000, 1200000, "TRES_FORTE"),
    ("Avocat",                     "Droit & Sciences Politiques", 200000, 600000, 1500000, "MOYENNE"),
    ("Comptable",                  "Économie & Gestion",          150000, 300000, 500000,  "FORTE"),
    ("Ingénieur civil",            "Sciences de l'Ingénieur",     200000, 450000, 800000,  "FORTE"),
    ("Professeur de lycée",        "Éducation & Formation",       120000, 200000, 300000,  "TRES_FORTE"),
    ("Agronome",                   "Agriculture & Environnement", 150000, 280000, 450000,  "FORTE"),
    ("Journaliste",                "Communication & Journalisme", 100000, 220000, 400000,  "MOYENNE"),
    ("Graphiste / Designer UI",    "Arts & Design",               120000, 280000, 500000,  "FORTE"),
    ("Data Scientist",             "Informatique & Numérique",    300000, 600000, 1000000, "TRES_FORTE"),
]

FORMATIONS = [
    # (nom, domaine_nom, etablissement_sigle, niveau, duree, cout_annuel, importance)
    ("Licence en Informatique",                "Informatique & Numérique",    "UL",    "LICENCE",  3, 250000,  "ELEVEE"),
    ("Médecine générale (Doctorat d'État)",    "Santé & Médecine",            "UL",    "DOCTORAT", 7, 100000,  "CRITIQUE"),
    ("Licence en Droit Privé",                 "Droit & Sciences Politiques", "UL",    "LICENCE",  3, 200000,  "MOYENNE"),
    ("BTS Comptabilité & Gestion",             "Économie & Gestion",          "ESGIS", "BTS",      2, 450000,  "ELEVEE"),
    ("Licence Gestion des Entreprises",        "Économie & Gestion",          "IAM",   "LICENCE",  3, 600000,  "ELEVEE"),
    ("Diplôme d'Ingénieur Génie Civil",        "Sciences de l'Ingénieur",     "EPL",   "INGENIEUR",5, 800000,  "CRITIQUE"),
    ("Licence Sciences de l'Éducation",        "Éducation & Formation",       "UK",    "LICENCE",  3, 180000,  "MOYENNE"),
    ("BTS Agriculture & Développement Rural",  "Agriculture & Environnement", "CFPT",  "BTS",      2, 150000,  "ELEVEE"),
    ("Licence Communication & Journalisme",    "Communication & Journalisme", "UCAO",  "LICENCE",  3, 700000,  "MOYENNE"),
    ("Master Data Science & IA",               "Informatique & Numérique",    "UL",    "MASTER",   2, 350000,  "CRITIQUE"),
]

# 10 questions RIASEC Likert pour le test principal
QUESTIONS_RIASEC = [
    ("J'aime travailler avec des outils, des machines ou des appareils électroniques.",
     {"R": 1.0}),
    ("J'aime analyser des données, résoudre des problèmes complexes ou faire des recherches.",
     {"I": 1.0}),
    ("J'aime créer des œuvres artistiques, écrire des histoires ou composer de la musique.",
     {"A": 1.0}),
    ("J'aime aider les autres, enseigner ou soigner des personnes.",
     {"S": 1.0}),
    ("J'aime convaincre des gens, diriger des équipes ou lancer des projets.",
     {"E": 1.0}),
    ("J'aime classer, organiser des dossiers et respecter des procédures précises.",
     {"C": 1.0}),
    ("J'aime coder des applications ou développer des logiciels.",
     {"I": 0.5, "N": 0.5}),
    ("J'aime travailler en plein air, protéger la nature ou cultiver la terre.",
     {"R": 0.5, "ENV": 0.5}),
    ("Je préfère travailler seul(e) sur des projets techniques plutôt qu'en groupe.",
     {"R": 0.5, "I": 0.5}),
    ("J'apprécie animer des réunions, présenter des idées ou motiver mon entourage.",
     {"E": 0.5, "S": 0.5}),
]

USERS_DEMO = [
    # (first_name, last_name, email, role, statut_compte, password)
    ("Admin",      "AvenSU",    "admin@avensu.tg",      "ADMIN",    "ACTIF", "AdminAvenSU2026!"),
    ("Kofi",       "Mensah",    "conseiller1@avensu.tg","COUNSELOR","ACTIF", "Conseil2026!"),
    ("Ama",        "Koffi",     "conseiller2@avensu.tg","COUNSELOR","ACTIF", "Conseil2026!"),
    ("Yao",        "Agbeko",    "etudiant1@avensu.tg",  "STUDENT",  "ACTIF", "Etudiant2026!"),
]


class Command(BaseCommand):
    help = "Peuple la base de données avec 10 entrées par modèle (démo)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Supprime toutes les données seedées avant de recréer.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        self.stdout.write(self.style.MIGRATE_HEADING("\n── Seed AvenSU-Orienta ──\n"))

        domaines    = self._seed_domaines()
        metiers     = self._seed_metiers(domaines)
        etablissements = self._seed_etablissements()
        formations  = self._seed_formations(domaines, etablissements, metiers)
        test        = self._seed_test_orientation()
        self._seed_questions(test)
        self._seed_users()

        self.stdout.write(self.style.SUCCESS("\n✅  Seed terminé avec succès !\n"))

    # ─────────────────────────── flush ────────────────────────────

    def _flush(self):
        from apps.catalog.models import Domaine, Metier, Etablissement, Formation
        from apps.orientation.models import TestOrientation

        self.stdout.write(self.style.WARNING("⚠  Suppression des données seedées…"))
        Formation.objects.all().delete()
        Metier.objects.all().delete()
        Etablissement.objects.all().delete()
        Domaine.objects.all().delete()
        TestOrientation.objects.filter(slug="test-riasec-principal").delete()
        User.objects.filter(email__in=[u[2] for u in USERS_DEMO]).delete()
        self.stdout.write("   Données supprimées.")

    # ─────────────────────────── domaines ──────────────────────────

    def _seed_domaines(self):
        from apps.catalog.models import Domaine

        domaines = {}
        created = 0
        for d in DOMAINES:
            obj, is_new = Domaine.objects.get_or_create(
                nom=d["nom"],
                defaults={
                    "slug": slugify(d["nom"]),
                    "icon": d["icon"],
                    "couleur": d["couleur"],
                    "ordre": d["ordre"],
                    "is_active": True,
                },
            )
            domaines[d["nom"]] = obj
            if is_new:
                created += 1

        self._log("Domaines", len(DOMAINES), created)
        return domaines

    # ─────────────────────────── métiers ──────────────────────────

    def _seed_metiers(self, domaines):
        from apps.catalog.models import Metier

        metiers = {}
        created = 0
        for nom, dom_nom, rev_min, rev_moy, rev_max, demande in METIERS:
            obj, is_new = Metier.objects.get_or_create(
                slug=slugify(nom),
                defaults={
                    "nom": nom,
                    "description_courte": f"Métier en {dom_nom}.",
                    "domaine": domaines[dom_nom],
                    "revenu_min": rev_min,
                    "revenu_moyen": rev_moy,
                    "revenu_max": rev_max,
                    "demande_marche": demande,
                    "niveau_etude_requis": "BAC+3",
                    "pays_concernes": ["Togo", "Bénin", "Côte d'Ivoire"],
                    "taux_emploi": 70.0,
                },
            )
            metiers[nom] = obj
            if is_new:
                created += 1

        self._log("Métiers", len(METIERS), created)
        return metiers

    # ─────────────────────── établissements ───────────────────────

    def _seed_etablissements(self):
        from apps.catalog.models import Etablissement

        etabs = {}
        created = 0
        for e in ETABLISSEMENTS:
            slug = slugify(e["sigle"])
            obj, is_new = Etablissement.objects.get_or_create(
                sigle=e["sigle"],
                defaults={
                    "nom": e["nom"],
                    "slug": slug,
                    "type": e["type"],
                    "statut": e["statut"],
                    "ville": e.get("ville", "Lomé"),
                    "pays": "Togo",
                    "description_courte": f"{e['nom']} — {e.get('ville','Lomé')}.",
                    "is_active": True,
                    "is_verified": True,
                },
            )
            etabs[e["sigle"]] = obj
            if is_new:
                created += 1

        self._log("Établissements", len(ETABLISSEMENTS), created)
        return etabs

    # ─────────────────────────── formations ───────────────────────

    def _seed_formations(self, domaines, etabs, metiers):
        from apps.catalog.models import Formation

        formations = []
        created = 0
        for nom, dom_nom, etab_sigle, niveau, duree, cout, importance in FORMATIONS:
            slug_base = slugify(f"{nom}-{etab_sigle}")
            obj, is_new = Formation.objects.get_or_create(
                slug=slug_base,
                defaults={
                    "nom": nom,
                    "etablissement": etabs[etab_sigle],
                    "domaine": domaines[dom_nom],
                    "niveau": niveau,
                    "duree_annees": duree,
                    "cout_annuel": cout,
                    "importance_strategique": importance,
                    "description_courte": f"{nom} proposée par {etabs[etab_sigle].sigle}.",
                    "modalite": "PRESENTIEL",
                    "is_active": True,
                    "frais_inscription": 0,
                    "frais_dossier": 0,
                },
            )
            formations.append(obj)
            if is_new:
                created += 1

        self._log("Formations", len(FORMATIONS), created)
        return formations

    # ─────────────────────── test orientation ─────────────────────

    def _seed_test_orientation(self):
        from apps.orientation.models import TestOrientation

        test, is_new = TestOrientation.objects.get_or_create(
            slug="test-riasec-principal",
            defaults={
                "nom": "Test d'orientation RIASEC — AvenSU",
                "description_courte": "Découvrez votre profil Holland en 10 minutes.",
                "description": (
                    "Ce test évalue vos intérêts professionnels selon le modèle RIASEC "
                    "(Holland), adapté au contexte ouest-africain avec les dimensions "
                    "Numérique (N) et Environnement (ENV)."
                ),
                "type": "INTERETS",
                "duree_estimee_minutes": 10,
                "is_active": True,
                "is_public": True,
                "dimensions_evaluees": ["R", "I", "A", "S", "E", "C", "N", "ENV"],
            },
        )
        label = "créé" if is_new else "existant"
        self.stdout.write(f"   Test RIASEC         : {label}")
        return test

    # ─────────────────────────── questions ────────────────────────

    def _seed_questions(self, test):
        from apps.orientation.models import Question

        created = 0
        for i, (texte, dimensions) in enumerate(QUESTIONS_RIASEC, start=1):
            _, is_new = Question.objects.get_or_create(
                test=test,
                ordre=i,
                defaults={
                    "texte": texte,
                    "type": "ECHELLE_LIKERT",
                    "dimensions": dimensions,
                    "poids": 1.0,
                    "obligatoire": True,
                    "is_active": True,
                },
            )
            if is_new:
                created += 1

        test.nombre_questions = test.questions.filter(is_active=True).count()
        test.save(update_fields=["nombre_questions"])
        self._log("Questions RIASEC", len(QUESTIONS_RIASEC), created)

    # ─────────────────────────── users ────────────────────────────

    def _seed_users(self):
        created = 0
        for first_name, last_name, email, role, statut, password in USERS_DEMO:
            if User.objects.filter(email=email).exists():
                continue
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                statut_compte=statut,
                is_email_verified=True,
                is_active=True,
                is_staff=(role == "ADMIN"),
                is_superuser=(role == "ADMIN"),
            )
            created += 1

        self._log("Utilisateurs démo", len(USERS_DEMO), created)
        if created:
            self.stdout.write(
                self.style.WARNING(
                    "   Comptes créés (changer les mots de passe en production !) :\n"
                    "     admin@avensu.tg          / AdminAvenSU2026!\n"
                    "     conseiller1@avensu.tg    / Conseil2026!\n"
                    "     conseiller2@avensu.tg    / Conseil2026!\n"
                    "     etudiant1@avensu.tg      / Etudiant2026!"
                )
            )

    # ─────────────────────────── utilitaire ───────────────────────

    def _log(self, label, total, created):
        skipped = total - created
        parts = []
        if created:
            parts.append(self.style.SUCCESS(f"+{created} créés"))
        if skipped:
            parts.append(f"{skipped} déjà présents")
        self.stdout.write(f"   {label:<25} {', '.join(parts) if parts else 'aucun changement'}")
