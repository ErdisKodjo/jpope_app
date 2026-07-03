# -*- coding: utf-8 -*-
"""
Données de seed — AvenSU-Orienta
Généré selon le guide insertion_donnees.md
20 établissements réels/plausibles du Togo (dont IPNET), 10 formations chacun (200 formations),
métiers liés, événements, forums, classements, conseillers.
"""
from django.utils.text import slugify

# ──────────────────────────────────────────────────────────────────────
# NIVEAU 1 — DOMAINES (10)
# ──────────────────────────────────────────────────────────────────────
DOMAINES = [
    dict(nom="Informatique & Numérique", icon="💻", couleur="#3B82F6", ordre=1,
         description="Développement logiciel, réseaux, data et cybersécurité : les métiers qui font tourner le numérique africain."),
    dict(nom="Santé & Médecine", icon="🏥", couleur="#EF4444", ordre=2,
         description="Formations médicales et paramédicales pour soigner et accompagner les populations."),
    dict(nom="Droit & Sciences Politiques", icon="⚖️", couleur="#8B5CF6", ordre=3,
         description="Droit privé, public, international et sciences politiques pour comprendre et faire évoluer les institutions."),
    dict(nom="Gestion & Commerce", icon="📊", couleur="#F59E0B", ordre=4,
         description="Management, marketing et entrepreneuriat pour piloter les organisations de demain."),
    dict(nom="Sciences & Ingénierie", icon="🔬", couleur="#10B981", ordre=5,
         description="Génie civil, électrique, mécanique et sciences fondamentales au service de l'innovation."),
    dict(nom="Lettres & Sciences Humaines", icon="📚", couleur="#EC4899", ordre=6,
         description="Langues, histoire, sociologie et sciences de l'éducation pour comprendre les sociétés."),
    dict(nom="Architecture & BTP", icon="🏗️", couleur="#6366F1", ordre=7,
         description="Conception, construction et aménagement des espaces urbains et ruraux."),
    dict(nom="Agriculture & Environnement", icon="🌱", couleur="#84CC16", ordre=8,
         description="Agronomie, élevage et gestion durable des ressources naturelles."),
    dict(nom="Arts, Design & Communication", icon="🎨", couleur="#F97316", ordre=9,
         description="Design graphique, audiovisuel, communication et industries créatives."),
    dict(nom="Finance & Comptabilité", icon="💰", couleur="#0EA5E9", ordre=10,
         description="Comptabilité, audit, finance d'entreprise et fiscalité."),
]
for d in DOMAINES:
    d["slug"] = slugify(d["nom"])

D = {d["slug"]: d["slug"] for d in DOMAINES}  # helper alias
INFO = "informatique-numerique"
SANTE = "sante-medecine"
DROIT = "droit-sciences-politiques"
GESTION = "gestion-commerce"
SCIENCES = "sciences-ingenierie"
LETTRES = "lettres-sciences-humaines"
ARCHI = "architecture-btp"
AGRI = "agriculture-environnement"
ARTS = "arts-design-communication"
FINANCE = "finance-comptabilite"

# ──────────────────────────────────────────────────────────────────────
# NIVEAU 2 — ÉTABLISSEMENTS (20, dont IPNET)
# ──────────────────────────────────────────────────────────────────────
# type: PUBLIC / PRIVE_LAIC / PRIVE_CONFESSIONNEL / INTERNATIONAL / GRANDE_ECOLE
ETABLISSEMENTS = [
    dict(sigle="UL", nom="Université de Lomé", type="PUBLIC", statut="AGREÉ", ville="Lomé",
         date_creation=1970, domaines=[INFO, DROIT, GESTION, SCIENCES, LETTRES],
         nb_etudiants=45000, nb_enseignants=1200, note=3.8, classement_national=1,
         frais_min=25000, frais_max=50000, scol_min=100000, scol_max=400000,
         latitude=6.137069, longitude=1.222210, featured=True),
    dict(sigle="UK", nom="Université de Kara", type="PUBLIC", statut="AGREÉ", ville="Kara",
         date_creation=1999, domaines=[AGRI, SANTE, LETTRES, GESTION],
         nb_etudiants=12000, nb_enseignants=380, note=3.4, classement_national=6,
         frais_min=20000, frais_max=40000, scol_min=90000, scol_max=300000,
         latitude=9.556100, longitude=1.187400),
    dict(sigle="ESGIS", nom="École Supérieure de Gestion, d'Informatique et des Sciences", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=1996, domaines=[INFO, GESTION, FINANCE],
         nb_etudiants=6500, nb_enseignants=180, note=3.9, classement_national=3,
         frais_min=50000, frais_max=100000, scol_min=450000, scol_max=900000,
         latitude=6.171900, longitude=1.211600, featured=True),
    dict(sigle="ESIS", nom="École Supérieure d'Ingénierie et des Sciences", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=2005, domaines=[SCIENCES, INFO, ARCHI],
         nb_etudiants=2800, nb_enseignants=110, note=4.0, classement_national=2,
         frais_min=60000, frais_max=120000, scol_min=700000, scol_max=1200000,
         latitude=6.165300, longitude=1.202100, featured=True),
    dict(sigle="IAD", nom="Institut Africain de Développement", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=2001, domaines=[GESTION, FINANCE, DROIT],
         nb_etudiants=3200, nb_enseignants=95, note=3.5, classement_national=9,
         frais_min=40000, frais_max=80000, scol_min=400000, scol_max=700000,
         latitude=6.160800, longitude=1.229400),
    dict(sigle="UCAO", nom="Université Catholique de l'Afrique de l'Ouest", type="PRIVE_CONFESSIONNEL",
         statut="AGREÉ", ville="Lomé", date_creation=1990, domaines=[LETTRES, DROIT, GESTION, SANTE],
         nb_etudiants=8000, nb_enseignants=260, note=3.7, classement_national=4,
         frais_min=45000, frais_max=90000, scol_min=350000, scol_max=650000,
         latitude=6.178200, longitude=1.254600, featured=True),
    dict(sigle="EST", nom="École Supérieure de Technologie", type="GRANDE_ECOLE",
         statut="ACCREDITE", ville="Lomé", date_creation=2008, domaines=[SCIENCES, INFO, ARCHI],
         nb_etudiants=1800, nb_enseignants=75, note=3.9, classement_national=5,
         frais_min=55000, frais_max=110000, scol_min=600000, scol_max=1000000,
         latitude=6.132400, longitude=1.216700),
    dict(sigle="FODEF", nom="Formation pour le Développement", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=2010, domaines=[GESTION, LETTRES, ARTS],
         nb_etudiants=1500, nb_enseignants=55, note=3.2, classement_national=14,
         frais_min=30000, frais_max=60000, scol_min=300000, scol_max=550000,
         latitude=6.155900, longitude=1.198300),
    dict(sigle="IST", nom="Institut Supérieur de Technologie", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=2003, domaines=[INFO, SCIENCES, GESTION],
         nb_etudiants=3400, nb_enseignants=120, note=3.6, classement_national=7,
         frais_min=45000, frais_max=90000, scol_min=450000, scol_max=800000,
         latitude=6.149700, longitude=1.234800),
    dict(sigle="INFA", nom="Institut National de Formation Agricole", type="PUBLIC",
         statut="AGREÉ", ville="Tové", date_creation=1974, domaines=[AGRI, SCIENCES],
         nb_etudiants=1200, nb_enseignants=60, note=3.3, classement_national=12,
         frais_min=15000, frais_max=30000, scol_min=80000, scol_max=200000,
         latitude=6.900000, longitude=0.983000),
    dict(sigle="IPNET", nom="IPNET Institute of Technology", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=2015, domaines=[INFO, SCIENCES, ARTS],
         nb_etudiants=1400, nb_enseignants=65, note=3.8, classement_national=8,
         frais_min=40000, frais_max=80000, scol_min=400000, scol_max=750000,
         latitude=6.174800, longitude=1.216900, featured=True,
         description_extra="École togolaise spécialisée dans le développement web et mobile, "
                             "les réseaux et la formation professionnelle accélérée au numérique."),
    dict(sigle="ESAG", nom="École Supérieure Africaine de Gestion", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=1999, domaines=[GESTION, FINANCE],
         nb_etudiants=2600, nb_enseignants=90, note=3.5, classement_national=10,
         frais_min=40000, frais_max=85000, scol_min=400000, scol_max=750000,
         latitude=6.168300, longitude=1.223700),
    dict(sigle="GIA", nom="Groupe Informatique Appliquée", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=2007, domaines=[INFO, GESTION],
         nb_etudiants=1900, nb_enseignants=70, note=3.4, classement_national=13,
         frais_min=35000, frais_max=70000, scol_min=350000, scol_max=650000,
         latitude=6.140500, longitude=1.245200),
    dict(sigle="ISICOM", nom="Institut Supérieur d'Informatique et de Commerce", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=2004, domaines=[INFO, GESTION, FINANCE],
         nb_etudiants=2100, nb_enseignants=80, note=3.5, classement_national=11,
         frais_min=38000, frais_max=75000, scol_min=380000, scol_max=680000,
         latitude=6.185600, longitude=1.203900),
    dict(sigle="UCND", nom="Université Catholique Notre-Dame", type="PRIVE_CONFESSIONNEL",
         statut="EN_EVALUATION", ville="Atakpamé", date_creation=2012, domaines=[LETTRES, SANTE, GESTION],
         nb_etudiants=950, nb_enseignants=40, note=3.0, classement_national=17,
         frais_min=25000, frais_max=50000, scol_min=250000, scol_max=450000,
         latitude=7.531900, longitude=1.130400),
    dict(sigle="ENSI", nom="École Nationale Supérieure d'Ingénieurs", type="PUBLIC",
         statut="AGREÉ", ville="Lomé", date_creation=1978, domaines=[SCIENCES, ARCHI, INFO],
         nb_etudiants=2200, nb_enseignants=140, note=3.9, classement_national=5,
         frais_min=20000, frais_max=40000, scol_min=120000, scol_max=350000,
         latitude=6.128900, longitude=1.209800, featured=True),
    dict(sigle="ISFOP", nom="Institut Supérieur de Formation Professionnelle", type="PRIVE_LAIC",
         statut="RECONNU", ville="Sokodé", date_creation=2011, domaines=[GESTION, AGRI, ARTS],
         nb_etudiants=1100, nb_enseignants=45, note=3.1, classement_national=18,
         frais_min=25000, frais_max=50000, scol_min=250000, scol_max=450000,
         latitude=8.983300, longitude=1.133300),
    dict(sigle="ISMS", nom="Institut Supérieur de Management et de Statistiques", type="PRIVE_LAIC",
         statut="RECONNU", ville="Lomé", date_creation=2006, domaines=[GESTION, FINANCE, SCIENCES],
         nb_etudiants=1700, nb_enseignants=65, note=3.4, classement_national=15,
         frais_min=35000, frais_max=70000, scol_min=350000, scol_max=600000,
         latitude=6.152100, longitude=1.240300),
    dict(sigle="EAMAU", nom="École Africaine des Métiers de l'Architecture et de l'Urbanisme",
         type="INTERNATIONAL", statut="ACCREDITE", ville="Lomé", date_creation=1975,
         domaines=[ARCHI, SCIENCES], nb_etudiants=800, nb_enseignants=55, note=4.1,
         classement_national=2, frais_min=80000, frais_max=150000, scol_min=900000, scol_max=1500000,
         latitude=6.163700, longitude=1.230900, featured=True,
         description_extra="Établissement interétatique de référence en Afrique de l'Ouest et du Centre "
                             "pour la formation d'architectes et d'urbanistes."),
    dict(sigle="ISAE", nom="Institut Supérieur d'Agronomie et Environnement", type="PRIVE_LAIC",
         statut="RECONNU", ville="Kara", date_creation=2009, domaines=[AGRI, SCIENCES],
         nb_etudiants=1300, nb_enseignants=50, note=3.3, classement_national=16,
         frais_min=30000, frais_max=60000, scol_min=280000, scol_max=500000,
         latitude=9.548900, longitude=1.195600),
]
for e in ETABLISSEMENTS:
    e["slug"] = slugify(e["nom"])

# ──────────────────────────────────────────────────────────────────────
# NIVEAU 3 — MÉTIERS (par domaine)
# ──────────────────────────────────────────────────────────────────────
METIERS = [
    # Informatique & Numérique
    dict(nom="Développeur Logiciel", domaine=INFO, revenu_min=150000, revenu_max=1200000, revenu_moyen=450000,
         taux_emploi=85, demande="TRES_FORTE", niveau="BAC+3",
         competences=["Python", "JavaScript", "Bases de données", "Git"]),
    dict(nom="Data Analyst / Data Scientist", domaine=INFO, revenu_min=200000, revenu_max=1500000, revenu_moyen=550000,
         taux_emploi=80, demande="TRES_FORTE", niveau="BAC+5",
         competences=["Python", "SQL", "Statistiques", "Power BI"]),
    dict(nom="Administrateur Réseau", domaine=INFO, revenu_min=150000, revenu_max=900000, revenu_moyen=380000,
         taux_emploi=78, demande="FORTE", niveau="BAC+3",
         competences=["Cisco", "Linux", "Sécurité réseau"]),
    dict(nom="Chef de Projet IT", domaine=INFO, revenu_min=300000, revenu_max=1400000, revenu_moyen=600000,
         taux_emploi=76, demande="FORTE", niveau="BAC+5",
         competences=["Gestion de projet", "Agile/Scrum", "Leadership"]),
    dict(nom="Analyste Cybersécurité", domaine=INFO, revenu_min=250000, revenu_max=1600000, revenu_moyen=700000,
         taux_emploi=82, demande="TRES_FORTE", niveau="BAC+5",
         competences=["Pentest", "SIEM", "ISO 27001"]),
    dict(nom="Développeur Mobile", domaine=INFO, revenu_min=180000, revenu_max=1100000, revenu_moyen=420000,
         taux_emploi=79, demande="FORTE", niveau="BAC+3",
         competences=["Flutter", "React Native", "Kotlin"]),
    # Santé & Médecine
    dict(nom="Médecin généraliste", domaine=SANTE, revenu_min=300000, revenu_max=2000000, revenu_moyen=800000,
         taux_emploi=92, demande="TRES_FORTE", niveau="BAC+8",
         competences=["Diagnostic clinique", "Pharmacologie", "Relation patient"]),
    dict(nom="Infirmier(ère) diplômé(e)", domaine=SANTE, revenu_min=120000, revenu_max=600000, revenu_moyen=350000,
         taux_emploi=90, demande="FORTE", niveau="BAC+3",
         competences=["Soins infirmiers", "Urgences", "Hygiène hospitalière"]),
    dict(nom="Pharmacien(ne)", domaine=SANTE, revenu_min=250000, revenu_max=1400000, revenu_moyen=650000,
         taux_emploi=88, demande="FORTE", niveau="BAC+5",
         competences=["Pharmacologie", "Gestion officine", "Conseil patient"]),
    dict(nom="Sage-femme", domaine=SANTE, revenu_min=130000, revenu_max=550000, revenu_moyen=320000,
         taux_emploi=87, demande="FORTE", niveau="BAC+3",
         competences=["Suivi grossesse", "Accouchement", "Soins néonataux"]),
    # Gestion & Commerce
    dict(nom="Comptable / Auditeur", domaine=GESTION, revenu_min=150000, revenu_max=900000, revenu_moyen=400000,
         taux_emploi=75, demande="FORTE", niveau="BAC+3",
         competences=["Comptabilité générale", "Fiscalité", "Sage/SAP"]),
    dict(nom="Responsable Commercial", domaine=GESTION, revenu_min=180000, revenu_max=1200000, revenu_moyen=500000,
         taux_emploi=72, demande="FORTE", niveau="BAC+3",
         competences=["Négociation", "CRM", "Prospection"]),
    dict(nom="Gestionnaire RH", domaine=GESTION, revenu_min=150000, revenu_max=800000, revenu_moyen=380000,
         taux_emploi=68, demande="MOYENNE", niveau="BAC+3",
         competences=["Recrutement", "Droit du travail", "Paie"]),
    dict(nom="Entrepreneur / Chef d'entreprise", domaine=GESTION, revenu_min=0, revenu_max=3000000, revenu_moyen=450000,
         taux_emploi=60, demande="MOYENNE", niveau="BAC+3",
         competences=["Business plan", "Gestion financière", "Leadership"]),
    # Finance & Comptabilité
    dict(nom="Analyste Financier", domaine=FINANCE, revenu_min=250000, revenu_max=1500000, revenu_moyen=600000,
         taux_emploi=74, demande="FORTE", niveau="BAC+5",
         competences=["Analyse financière", "Excel avancé", "Marchés financiers"]),
    dict(nom="Expert-Comptable", domaine=FINANCE, revenu_min=350000, revenu_max=1800000, revenu_moyen=750000,
         taux_emploi=80, demande="FORTE", niveau="BAC+5",
         competences=["Normes IFRS", "Audit", "Fiscalité avancée"]),
    dict(nom="Chargé de clientèle bancaire", domaine=FINANCE, revenu_min=150000, revenu_max=700000, revenu_moyen=350000,
         taux_emploi=70, demande="MOYENNE", niveau="BAC+3",
         competences=["Produits bancaires", "Relation client", "Analyse de risque"]),
    # Sciences & Ingénierie
    dict(nom="Ingénieur Génie Civil", domaine=SCIENCES, revenu_min=300000, revenu_max=1800000, revenu_moyen=700000,
         taux_emploi=78, demande="FORTE", niveau="BAC+5",
         competences=["AutoCAD", "Béton armé", "Gestion de chantier"]),
    dict(nom="Ingénieur Électrique", domaine=SCIENCES, revenu_min=280000, revenu_max=1600000, revenu_moyen=650000,
         taux_emploi=76, demande="FORTE", niveau="BAC+5",
         competences=["Électrotechnique", "Automatisme", "Énergies renouvelables"]),
    dict(nom="Ingénieur Mécanique", domaine=SCIENCES, revenu_min=270000, revenu_max=1500000, revenu_moyen=600000,
         taux_emploi=74, demande="FORTE", niveau="BAC+5",
         competences=["CAO/DAO", "Maintenance industrielle", "Thermodynamique"]),
    # Droit & Sciences Politiques
    dict(nom="Avocat(e)", domaine=DROIT, revenu_min=200000, revenu_max=2500000, revenu_moyen=700000,
         taux_emploi=70, demande="MOYENNE", niveau="BAC+5",
         competences=["Plaidoirie", "Droit des affaires", "Rédaction juridique"]),
    dict(nom="Magistrat(e)", domaine=DROIT, revenu_min=300000, revenu_max=900000, revenu_moyen=500000,
         taux_emploi=65, demande="FAIBLE", niveau="BAC+5",
         competences=["Droit pénal", "Procédure civile", "Éthique judiciaire"]),
    dict(nom="Juriste d'entreprise", domaine=DROIT, revenu_min=250000, revenu_max=1300000, revenu_moyen=550000,
         taux_emploi=72, demande="MOYENNE", niveau="BAC+5",
         competences=["Droit des sociétés", "Contrats", "Conformité"]),
    # Lettres & Sciences Humaines
    dict(nom="Enseignant(e) / Professeur(e)", domaine=LETTRES, revenu_min=120000, revenu_max=500000, revenu_moyen=280000,
         taux_emploi=82, demande="FORTE", niveau="BAC+3",
         competences=["Pédagogie", "Communication", "Gestion de classe"]),
    dict(nom="Traducteur / Interprète", domaine=LETTRES, revenu_min=150000, revenu_max=800000, revenu_moyen=350000,
         taux_emploi=60, demande="MOYENNE", niveau="BAC+5",
         competences=["Anglais", "Français", "Traduction spécialisée"]),
    dict(nom="Psychologue", domaine=LETTRES, revenu_min=180000, revenu_max=900000, revenu_moyen=400000,
         taux_emploi=65, demande="MOYENNE", niveau="BAC+5",
         competences=["Écoute active", "Psychopathologie", "Thérapies"]),
    # Architecture & BTP
    dict(nom="Architecte", domaine=ARCHI, revenu_min=300000, revenu_max=2000000, revenu_moyen=750000,
         taux_emploi=73, demande="FORTE", niveau="BAC+5",
         competences=["AutoCAD/Revit", "Urbanisme", "Conception 3D"]),
    dict(nom="Conducteur de travaux BTP", domaine=ARCHI, revenu_min=200000, revenu_max=1100000, revenu_moyen=500000,
         taux_emploi=75, demande="FORTE", niveau="BAC+3",
         competences=["Gestion de chantier", "Lecture de plans", "Sécurité"]),
    # Agriculture & Environnement
    dict(nom="Ingénieur Agronome", domaine=AGRI, revenu_min=200000, revenu_max=1200000, revenu_moyen=480000,
         taux_emploi=70, demande="FORTE", niveau="BAC+5",
         competences=["Agronomie", "Gestion des sols", "Agroéconomie"]),
    dict(nom="Technicien Environnement", domaine=AGRI, revenu_min=150000, revenu_max=700000, revenu_moyen=350000,
         taux_emploi=66, demande="MOYENNE", niveau="BAC+3",
         competences=["Gestion des déchets", "Réglementation environnementale"]),
    # Arts, Design & Communication
    dict(nom="Designer Graphique", domaine=ARTS, revenu_min=120000, revenu_max=900000, revenu_moyen=350000,
         taux_emploi=68, demande="MOYENNE", niveau="BAC+3",
         competences=["Adobe Creative Suite", "Identité visuelle", "UI/UX"]),
    dict(nom="Chargé(e) de communication", domaine=ARTS, revenu_min=150000, revenu_max=900000, revenu_moyen=380000,
         taux_emploi=67, demande="MOYENNE", niveau="BAC+3",
         competences=["Réseaux sociaux", "Rédaction", "Stratégie de marque"]),
]
for m in METIERS:
    m["slug"] = slugify(m["nom"])
    m.setdefault("pays_concernes", ["Togo", "Bénin", "Côte d'Ivoire", "Sénégal", "Ghana"])
    m.setdefault("villes_principales", ["Lomé", "Kara", "Abidjan", "Dakar", "Cotonou"])
    m.setdefault("source_donnees", "INS Togo 2025 · Enquête emploi ANPE")
    m.setdefault("date_mise_a_jour", "2026-01-15")

METIERS_BY_DOMAINE = {}
for m in METIERS:
    METIERS_BY_DOMAINE.setdefault(m["domaine"], []).append(m["slug"])

# ──────────────────────────────────────────────────────────────────────
# NIVEAU 4 — CATALOGUE DE FORMATIONS PAR DOMAINE (gabarits réutilisables)
# Chaque tuple : (nom, niveau, duree_annees, cout_base_multiplicateur, programmes)
# ──────────────────────────────────────────────────────────────────────
FORMATION_TEMPLATES = {
    INFO: [
        ("BTS Informatique de Gestion", "BTS", 2, 0.55, ["Algorithmique", "Bases de données", "Réseaux", "Bureautique avancée"]),
        ("Licence Informatique", "LICENCE", 3, 0.75, ["Algorithmique", "Bases de données", "Réseaux", "Programmation orientée objet", "Projet tutoré"]),
        ("Licence Génie Logiciel", "LICENCE", 3, 0.85, ["Génie logiciel", "UML", "Développement web", "Tests logiciels"]),
        ("Licence Réseaux & Télécoms", "LICENCE", 3, 0.85, ["Architecture réseau", "Cisco", "Télécommunications", "Sécurité"]),
        ("Master Informatique", "MASTER", 2, 1.4, ["Intelligence artificielle", "Cloud computing", "Big Data", "Mémoire de recherche"]),
        ("Master Cybersécurité", "MASTER", 2, 1.6, ["Sécurité offensive", "Cryptographie", "Gouvernance SI", "Audit de sécurité"]),
        ("Diplôme Ingénieur Informatique", "INGENIEUR", 5, 2.2, ["Génie logiciel avancé", "Systèmes distribués", "IA appliquée", "Projet de fin d'études"]),
        ("Certificat Développement Web", "CERTIFICAT", 1, 0.3, ["HTML/CSS/JS", "Framework front-end", "API REST", "Déploiement"]),
        ("BTS Réseaux Informatiques", "BTS", 2, 0.55, ["Administration réseau", "Virtualisation", "Support technique"]),
        ("Licence Data Science", "LICENCE", 3, 0.95, ["Statistiques", "Python pour la data", "Machine Learning", "Visualisation de données"]),
    ],
    SANTE: [
        ("Licence Sciences Infirmières", "LICENCE", 3, 0.7, ["Anatomie", "Soins infirmiers", "Pharmacologie", "Stage clinique"]),
        ("Doctorat en Médecine", "DOCTORAT", 7, 2.5, ["Anatomie", "Physiologie", "Pathologie", "Internat hospitalier"]),
        ("Licence Sage-femme", "LICENCE", 3, 0.75, ["Obstétrique", "Suivi de grossesse", "Néonatologie", "Stage maternité"]),
        ("BTS Analyses Biomédicales", "BTS", 2, 0.6, ["Biologie médicale", "Microbiologie", "Techniques de laboratoire"]),
        ("Licence Pharmacie", "LICENCE", 5, 1.5, ["Pharmacologie", "Chimie thérapeutique", "Officine", "Toxicologie"]),
        ("Master Santé Publique", "MASTER", 2, 1.3, ["Épidémiologie", "Politiques de santé", "Gestion des systèmes de santé"]),
        ("Certificat Premiers Secours & Soins", "CERTIFICAT", 1, 0.25, ["Gestes d'urgence", "Soins de base", "Hygiène"]),
        ("Licence Kinésithérapie", "LICENCE", 3, 0.9, ["Anatomie fonctionnelle", "Rééducation", "Techniques de massage"]),
        ("BTS Nutrition & Diététique", "BTS", 2, 0.55, ["Nutrition humaine", "Diététique", "Hygiène alimentaire"]),
        ("Master Gestion des Établissements de Santé", "MASTER", 2, 1.2, ["Management hospitalier", "Finance de la santé", "Qualité des soins"]),
    ],
    GESTION: [
        ("BTS Gestion Commerciale", "BTS", 2, 0.55, ["Marketing", "Techniques de vente", "Gestion commerciale"]),
        ("Licence Gestion", "LICENCE", 3, 0.7, ["Comptabilité", "Marketing", "Management", "Droit des affaires"]),
        ("Licence Management des Organisations", "LICENCE", 3, 0.85, ["Management", "Stratégie d'entreprise", "GRH", "Communication d'entreprise"]),
        ("Master Management & Stratégie", "MASTER", 2, 1.4, ["Stratégie", "Management de projet", "Business plan", "Mémoire professionnel"]),
        ("Master Marketing & Communication", "MASTER", 2, 1.3, ["Marketing digital", "Branding", "Étude de marché", "Communication de crise"]),
        ("BTS Ressources Humaines", "BTS", 2, 0.55, ["GRH", "Droit du travail", "Recrutement", "Paie"]),
        ("Licence Entrepreneuriat", "LICENCE", 3, 0.8, ["Création d'entreprise", "Business model", "Financement", "Gestion de projet"]),
        ("Master Administration des Entreprises (MBA)", "MASTER", 2, 1.8, ["Finance", "Stratégie globale", "Leadership", "Négociation internationale"]),
        ("Certificat Gestion de Projet", "CERTIFICAT", 1, 0.3, ["Méthodologie Agile", "Planification", "Gestion des risques"]),
        ("Licence Logistique & Transport", "LICENCE", 3, 0.75, ["Chaîne logistique", "Transport international", "Douane"]),
    ],
    FINANCE: [
        ("BTS Comptabilité & Gestion", "BTS", 2, 0.55, ["Comptabilité générale", "Fiscalité", "Gestion budgétaire"]),
        ("Licence Finance-Comptabilité", "LICENCE", 3, 0.8, ["Comptabilité approfondie", "Analyse financière", "Fiscalité des entreprises"]),
        ("Master Finance-Comptabilité", "MASTER", 2, 1.5, ["Audit", "Contrôle de gestion", "Normes IFRS", "Ingénierie financière"]),
        ("Master Banque & Marchés Financiers", "MASTER", 2, 1.6, ["Marchés financiers", "Gestion de portefeuille", "Risque bancaire"]),
        ("Licence Audit & Contrôle de Gestion", "LICENCE", 3, 0.9, ["Audit interne", "Contrôle de gestion", "Système d'information comptable"]),
        ("Certificat Fiscalité d'Entreprise", "CERTIFICAT", 1, 0.3, ["Fiscalité TVA/IS", "Déclarations fiscales", "Optimisation fiscale"]),
        ("BTS Assurance", "BTS", 2, 0.5, ["Techniques d'assurance", "Gestion des sinistres", "Droit des assurances"]),
        ("Master Expertise Comptable", "MASTER", 2, 1.7, ["Révision comptable", "Droit des sociétés", "Déontologie professionnelle"]),
        ("Licence Banque & Finance", "LICENCE", 3, 0.85, ["Techniques bancaires", "Analyse de crédit", "Produits financiers"]),
        ("Master Microfinance & Inclusion Financière", "MASTER", 2, 1.3, ["Microfinance", "Développement local", "Gestion des risques"]),
    ],
    SCIENCES: [
        ("Licence Sciences Physiques", "LICENCE", 3, 0.65, ["Physique générale", "Mathématiques", "Mécanique", "Travaux pratiques"]),
        ("Diplôme Ingénieur Génie Civil", "INGENIEUR", 5, 2.3, ["Béton armé", "Résistance des matériaux", "Topographie", "Projet de fin d'études"]),
        ("Diplôme Ingénieur Électrique", "INGENIEUR", 5, 2.1, ["Électrotechnique", "Automatisme", "Énergies renouvelables"]),
        ("Diplôme Ingénieur Mécanique", "INGENIEUR", 5, 2.0, ["Mécanique des fluides", "CAO/DAO", "Maintenance industrielle"]),
        ("Master Sciences de l'Ingénieur", "MASTER", 2, 1.5, ["Modélisation", "Recherche appliquée", "Innovation technologique"]),
        ("BTS Électrotechnique", "BTS", 2, 0.6, ["Électricité industrielle", "Automatisme", "Maintenance"]),
        ("Doctorat en Sciences", "DOCTORAT", 3, 1.8, ["Recherche avancée", "Publication scientifique", "Thèse de doctorat"]),
        ("Licence Mathématiques Appliquées", "LICENCE", 3, 0.7, ["Analyse", "Algèbre", "Probabilités", "Statistiques"]),
        ("BTS Maintenance Industrielle", "BTS", 2, 0.6, ["Maintenance préventive", "Automatismes industriels", "Sécurité"]),
        ("Master Énergies Renouvelables", "MASTER", 2, 1.4, ["Solaire photovoltaïque", "Efficacité énergétique", "Réseaux électriques"]),
    ],
    LETTRES: [
        ("Licence Lettres Modernes", "LICENCE", 3, 0.6, ["Littérature francophone", "Linguistique", "Analyse de texte"]),
        ("Licence Sciences de l'Éducation", "LICENCE", 3, 0.65, ["Pédagogie", "Psychologie de l'enfant", "Didactique"]),
        ("Master Traduction & Interprétation", "MASTER", 2, 1.2, ["Traduction spécialisée", "Interprétation consécutive", "Terminologie"]),
        ("Licence Anglais Appliqué", "LICENCE", 3, 0.65, ["Grammaire anglaise", "Traduction", "Communication interculturelle"]),
        ("Master Psychologie", "MASTER", 2, 1.3, ["Psychopathologie", "Psychologie clinique", "Thérapies comportementales"]),
        ("Licence Sociologie", "LICENCE", 3, 0.6, ["Sociologie générale", "Méthodes d'enquête", "Sociologie du développement"]),
        ("Certificat Pédagogie & Formation", "CERTIFICAT", 1, 0.25, ["Ingénierie pédagogique", "Animation de formation"]),
        ("Master Histoire & Patrimoine", "MASTER", 2, 1.1, ["Histoire africaine", "Patrimoine culturel", "Recherche historique"]),
        ("Licence Communication", "LICENCE", 3, 0.7, ["Théories de la communication", "Médias", "Rédaction professionnelle"]),
        ("Master Sciences de l'Éducation", "MASTER", 2, 1.2, ["Ingénierie de formation", "Évaluation pédagogique", "Gestion scolaire"]),
    ],
    ARCHI: [
        ("Diplôme Architecte (Cycle intégré)", "INGENIEUR", 6, 2.6, ["Conception architecturale", "Histoire de l'architecture", "Urbanisme", "Projet de fin d'études"]),
        ("Licence Urbanisme & Aménagement", "LICENCE", 3, 0.9, ["Planification urbaine", "Cartographie", "Droit de l'urbanisme"]),
        ("BTS Bâtiment", "BTS", 2, 0.65, ["Technologie du bâtiment", "Dessin technique", "Métré"]),
        ("Master Architecture Durable", "MASTER", 2, 1.7, ["Éco-conception", "Matériaux durables", "Efficacité énergétique du bâtiment"]),
        ("BTS Travaux Publics", "BTS", 2, 0.65, ["Terrassement", "Voiries et réseaux", "Topographie"]),
        ("Licence Génie Civil", "LICENCE", 3, 0.9, ["Béton armé", "Structures", "Matériaux de construction"]),
        ("Master Urbanisme & Gestion des Villes", "MASTER", 2, 1.6, ["Gouvernance urbaine", "Aménagement du territoire", "Habitat social"]),
        ("Certificat Dessin Technique & BIM", "CERTIFICAT", 1, 0.35, ["AutoCAD", "Revit/BIM", "Modélisation 3D"]),
        ("Licence Design d'Espace", "LICENCE", 3, 0.85, ["Architecture d'intérieur", "Design d'espace", "Matériaux et couleurs"]),
        ("Master Ingénierie des Structures", "MASTER", 2, 1.7, ["Calcul de structures", "Génie parasismique", "Normes de construction"]),
    ],
    AGRI: [
        ("Licence Agronomie", "LICENCE", 3, 0.6, ["Sciences du sol", "Production végétale", "Agroéconomie"]),
        ("BTS Production Agricole", "BTS", 2, 0.45, ["Techniques culturales", "Élevage", "Machinisme agricole"]),
        ("Master Agroéconomie & Développement Rural", "MASTER", 2, 1.1, ["Économie agricole", "Développement rural", "Politiques agricoles"]),
        ("Licence Sciences de l'Environnement", "LICENCE", 3, 0.65, ["Écologie", "Gestion des ressources naturelles", "Impact environnemental"]),
        ("BTS Élevage & Production Animale", "BTS", 2, 0.45, ["Zootechnie", "Santé animale", "Alimentation animale"]),
        ("Master Gestion Durable des Ressources Naturelles", "MASTER", 2, 1.2, ["Biodiversité", "Changement climatique", "Gestion de l'eau"]),
        ("Certificat Agriculture Biologique", "CERTIFICAT", 1, 0.2, ["Agroécologie", "Certification bio", "Maraîchage durable"]),
        ("Licence Foresterie & Environnement", "LICENCE", 3, 0.65, ["Sylviculture", "Aménagement forestier", "Conservation"]),
        ("BTS Agroalimentaire", "BTS", 2, 0.5, ["Transformation agroalimentaire", "Qualité et sécurité alimentaire"]),
        ("Master Ingénierie Agronomique", "MASTER", 2, 1.2, ["Recherche agronomique", "Innovation agricole", "Génie rural"]),
    ],
    ARTS: [
        ("Licence Design Graphique", "LICENCE", 3, 0.75, ["Identité visuelle", "Typographie", "Adobe Creative Suite"]),
        ("BTS Communication Visuelle", "BTS", 2, 0.55, ["Infographie", "Mise en page", "Photographie"]),
        ("Licence Communication & Journalisme", "LICENCE", 3, 0.7, ["Journalisme", "Rédaction web", "Médias numériques"]),
        ("Master Communication Digitale", "MASTER", 2, 1.2, ["Marketing digital", "Réseaux sociaux", "Stratégie de contenu"]),
        ("BTS Audiovisuel & Multimédia", "BTS", 2, 0.6, ["Montage vidéo", "Production audiovisuelle", "Motion design"]),
        ("Licence Arts Plastiques", "LICENCE", 3, 0.6, ["Dessin", "Peinture", "Histoire de l'art"]),
        ("Certificat Photographie Professionnelle", "CERTIFICAT", 1, 0.3, ["Prise de vue", "Retouche photo", "Éclairage studio"]),
        ("Master Industries Créatives & Design", "MASTER", 2, 1.3, ["Design produit", "Innovation créative", "Entrepreneuriat créatif"]),
        ("Licence Mode & Stylisme", "LICENCE", 3, 0.7, ["Stylisme", "Modélisme", "Histoire de la mode"]),
        ("BTS Publicité", "BTS", 2, 0.55, ["Stratégie publicitaire", "Création publicitaire", "Médiaplanning"]),
    ],
    DROIT: [
        ("Licence Droit Privé", "LICENCE", 3, 0.6, ["Droit civil", "Droit des obligations", "Procédure civile"]),
        ("Licence Droit Public", "LICENCE", 3, 0.6, ["Droit constitutionnel", "Droit administratif", "Institutions politiques"]),
        ("Master Droit des Affaires", "MASTER", 2, 1.3, ["Droit des sociétés", "Droit commercial OHADA", "Contrats internationaux"]),
        ("Master Droit International & Relations Internationales", "MASTER", 2, 1.3, ["Droit international public", "Diplomatie", "Organisations internationales"]),
        ("Licence Sciences Politiques", "LICENCE", 3, 0.65, ["Théorie politique", "Relations internationales", "Institutions comparées"]),
        ("Master Droit Pénal & Sciences Criminelles", "MASTER", 2, 1.2, ["Droit pénal approfondi", "Criminologie", "Procédure pénale"]),
        ("Certificat Droit du Travail", "CERTIFICAT", 1, 0.25, ["Contrats de travail", "Contentieux social", "Droit de la sécurité sociale"]),
        ("Licence Droit Fiscal", "LICENCE", 3, 0.65, ["Fiscalité générale", "Contentieux fiscal", "Droit douanier"]),
        ("Master Administration Publique", "MASTER", 2, 1.1, ["Gestion publique", "Politiques publiques", "Gouvernance locale"]),
        ("Doctorat en Droit", "DOCTORAT", 3, 1.6, ["Recherche juridique", "Méthodologie de la thèse", "Séminaires doctoraux"]),
    ],
}

# ──────────────────────────────────────────────────────────────────────
# NIVEAU 5 — ÉVÉNEMENTS (8)
# ──────────────────────────────────────────────────────────────────────
EVENEMENTS = [
    dict(titre="Journée Portes Ouvertes UL 2026", type="JPO", statut="PUBLIE",
         date_debut="2026-09-15 09:00:00", date_fin="2026-09-15 17:00:00", etab="UL",
         format="PRESENTIEL", lieu_nom="Campus principal UL", ville="Lomé", capacite_max=2000,
         description_courte="Découvrez toutes les filières de l'Université de Lomé lors de cette journée portes ouvertes.",
         tags=["université", "lomé", "portes-ouvertes"]),
    dict(titre="Salon des Formations Supérieures Lomé", type="SALON", statut="PUBLIE",
         date_debut="2026-08-20 08:00:00", date_fin="2026-08-21 18:00:00", etab=None,
         format="PRESENTIEL", lieu_nom="Centre International des Foires de Lomé", ville="Lomé", capacite_max=5000,
         description_courte="Le plus grand salon d'orientation post-bac du Togo réunissant plus de 40 établissements.",
         tags=["salon", "orientation", "lomé"]),
    dict(titre="Conférence Métiers du Numérique", type="CONFERENCE", statut="PUBLIE",
         date_debut="2026-08-05 14:00:00", date_fin="2026-08-05 17:00:00", etab="IPNET",
         format="PRESENTIEL", lieu_nom="Campus IPNET", ville="Lomé", capacite_max=300,
         description_courte="Des professionnels du numérique togolais échangent sur les métiers d'avenir de la tech.",
         tags=["informatique", "numérique", "carrières"]),
    dict(titre="Webinaire Orientation Post-Bac", type="WEBINAIRE", statut="PUBLIE",
         date_debut="2026-07-25 15:00:00", date_fin="2026-07-25 17:00:00", etab=None,
         format="EN_LIGNE", lieu_nom=None, ville=None, capacite_max=0,
         description_courte="Un webinaire gratuit pour bien préparer son orientation après le baccalauréat.",
         tags=["webinaire", "orientation", "bac"]),
    dict(titre="Journée Portes Ouvertes ESGIS 2026", type="JPO", statut="PUBLIE",
         date_debut="2026-09-22 09:00:00", date_fin="2026-09-22 16:00:00", etab="ESGIS",
         format="PRESENTIEL", lieu_nom="Campus ESGIS", ville="Lomé", capacite_max=800,
         description_courte="Visitez le campus ESGIS et rencontrez les enseignants et étudiants des filières gestion et informatique.",
         tags=["esgis", "portes-ouvertes"]),
    dict(titre="Concours d'entrée ESIS 2026", type="CONCOURS", statut="PUBLIE",
         date_debut="2026-07-10 08:00:00", date_fin="2026-07-10 13:00:00", etab="ESIS",
         format="PRESENTIEL", lieu_nom="Campus ESIS", ville="Lomé", capacite_max=500,
         description_courte="Concours national d'entrée aux cycles ingénieur de l'École Supérieure d'Ingénierie et des Sciences.",
         tags=["concours", "ingénieur", "esis"]),
    dict(titre="Atelier CV et Lettre de Motivation", type="ATELIER", statut="PUBLIE",
         date_debut="2026-08-12 10:00:00", date_fin="2026-08-12 13:00:00", etab=None,
         format="PRESENTIEL", lieu_nom="Espace TeCoX", ville="Lomé", capacite_max=100,
         description_courte="Un atelier pratique pour apprendre à rédiger un CV percutant et une lettre de motivation efficace.",
         tags=["atelier", "emploi", "cv"]),
    dict(titre="Rencontre Professionnels du Droit", type="RENCONTRE", statut="PUBLIE",
         date_debut="2026-08-28 14:00:00", date_fin="2026-08-28 17:00:00", etab="UL",
         format="PRESENTIEL", lieu_nom="Amphithéâtre Faculté de Droit", ville="Lomé", capacite_max=250,
         description_courte="Avocats, magistrats et juristes d'entreprise partagent leur expérience avec les étudiants en droit.",
         tags=["droit", "carrières", "rencontre"]),
]
for ev in EVENEMENTS:
    ev["slug"] = slugify(ev["titre"])

# ──────────────────────────────────────────────────────────────────────
# NIVEAU 6 — FORUMS (11)
# ──────────────────────────────────────────────────────────────────────
FORUMS = [
    dict(nom="Général & Bienvenue", type="GENERAL", icone="👋", ordre=1, domaine=None, etab=None),
    dict(nom="Informatique & Tech", type="PAR_DOMAINE", icone="💻", ordre=2, domaine=INFO, etab=None),
    dict(nom="Santé & Médecine", type="PAR_DOMAINE", icone="🏥", ordre=3, domaine=SANTE, etab=None),
    dict(nom="Gestion & Commerce", type="PAR_DOMAINE", icone="📊", ordre=4, domaine=GESTION, etab=None),
    dict(nom="Droit & Sciences Politiques", type="PAR_DOMAINE", icone="⚖️", ordre=5, domaine=DROIT, etab=None),
    dict(nom="Sciences & Ingénierie", type="PAR_DOMAINE", icone="🔬", ordre=6, domaine=SCIENCES, etab=None),
    dict(nom="Forum Université de Lomé", type="PAR_ETABLISSEMENT", icone="🎓", ordre=7, domaine=None, etab="UL"),
    dict(nom="Forum ESGIS", type="PAR_ETABLISSEMENT", icone="🎓", ordre=8, domaine=None, etab="ESGIS"),
    dict(nom="Offres d'emploi & Stages", type="EMPLOI", icone="💼", ordre=9, domaine=None, etab=None),
    dict(nom="Études à l'international", type="INTERNATIONAL", icone="✈️", ordre=10, domaine=None, etab=None),
    dict(nom="Entraide & Questions pratiques", type="ENTRAIDE", icone="🤝", ordre=11, domaine=None, etab=None),
]
for f in FORUMS:
    f["slug"] = slugify(f["nom"])

# ──────────────────────────────────────────────────────────────────────
# NIVEAU 7 — CLASSEMENTS 2026 (top 10)
# ──────────────────────────────────────────────────────────────────────
CLASSEMENTS = [
    dict(etab="UL", annee=2026, rang_national=1, score_final=78.5,
         details=dict(qualite_enseignement=82.0, insertion_professionnelle=75.0, recherche=45.0, infrastructures=80.0, vie_etudiante=70.0, accessibilite_financiere=85.0)),
    dict(etab="EAMAU", annee=2026, rang_national=2, score_final=76.8,
         details=dict(qualite_enseignement=85.0, insertion_professionnelle=80.0, recherche=60.0, infrastructures=78.0, vie_etudiante=65.0, accessibilite_financiere=40.0)),
    dict(etab="ESIS", annee=2026, rang_national=3, score_final=75.2,
         details=dict(qualite_enseignement=80.0, insertion_professionnelle=72.0, recherche=40.0, infrastructures=70.0, vie_etudiante=68.0, accessibilite_financiere=55.0)),
    dict(etab="ESGIS", annee=2026, rang_national=4, score_final=72.8,
         details=dict(qualite_enseignement=74.0, insertion_professionnelle=78.0, recherche=35.0, infrastructures=68.0, vie_etudiante=72.0, accessibilite_financiere=60.0)),
    dict(etab="ENSI", annee=2026, rang_national=5, score_final=71.5,
         details=dict(qualite_enseignement=78.0, insertion_professionnelle=70.0, recherche=55.0, infrastructures=65.0, vie_etudiante=60.0, accessibilite_financiere=82.0)),
    dict(etab="UCAO", annee=2026, rang_national=6, score_final=70.1,
         details=dict(qualite_enseignement=75.0, insertion_professionnelle=70.0, recherche=38.0, infrastructures=72.0, vie_etudiante=68.0, accessibilite_financiere=58.0)),
    dict(etab="EST", annee=2026, rang_national=7, score_final=68.9,
         details=dict(qualite_enseignement=70.0, insertion_professionnelle=72.0, recherche=42.0, infrastructures=66.0, vie_etudiante=62.0, accessibilite_financiere=55.0)),
    dict(etab="IPNET", annee=2026, rang_national=8, score_final=66.4,
         details=dict(qualite_enseignement=68.0, insertion_professionnelle=74.0, recherche=25.0, infrastructures=60.0, vie_etudiante=65.0, accessibilite_financiere=62.0)),
    dict(etab="IST", annee=2026, rang_national=9, score_final=64.7,
         details=dict(qualite_enseignement=66.0, insertion_professionnelle=68.0, recherche=30.0, infrastructures=62.0, vie_etudiante=60.0, accessibilite_financiere=60.0)),
    dict(etab="UK", annee=2026, rang_national=10, score_final=63.2,
         details=dict(qualite_enseignement=65.0, insertion_professionnelle=62.0, recherche=40.0, infrastructures=58.0, vie_etudiante=58.0, accessibilite_financiere=75.0)),
]

# ──────────────────────────────────────────────────────────────────────
# NIVEAU 8 — CONSEILLERS (5)
# ──────────────────────────────────────────────────────────────────────
CONSEILLERS = [
    dict(email="k.mensah@avensu.tg", prenom="Kokou", nom="Mensah", exp=8, tarif=15000,
         spec=["Informatique", "Gestion"], qualifications="Master en Génie Logiciel, ESGIS",
         bio="Ancien développeur devenu conseiller d'orientation, Kokou aide les étudiants à choisir entre les filières tech et gestion."),
    dict(email="a.koffi@avensu.tg", prenom="Ama", nom="Koffi", exp=12, tarif=20000,
         spec=["Santé", "Médecine"], qualifications="Doctorat en Sciences de l'Éducation, Université de Lomé",
         bio="Spécialiste de l'orientation vers les filières santé, Ama accompagne les futurs médecins et infirmiers depuis 12 ans."),
    dict(email="e.agbeko@avensu.tg", prenom="Edem", nom="Agbeko", exp=5, tarif=12000,
         spec=["Droit", "Sciences Politiques"], qualifications="Master en Droit des Affaires, Université de Lomé",
         bio="Juriste de formation, Edem conseille les étudiants souhaitant s'orienter vers le droit et les sciences politiques."),
    dict(email="m.aziabeme@avensu.tg", prenom="Mawuli", nom="Aziabémé", exp=10, tarif=18000,
         spec=["Finance", "Comptabilité"], qualifications="Expert-comptable diplômé, ESGIS",
         bio="Expert-comptable en exercice, Mawuli guide les étudiants vers les carrières de la finance et de l'audit."),
    dict(email="s.abotsi@avensu.tg", prenom="Sena", nom="Abotsi", exp=6, tarif=12000,
         spec=["Lettres", "Sciences Humaines"], qualifications="Master en Sciences de l'Éducation, UCAO",
         bio="Passionnée de pédagogie, Sena accompagne les étudiants dans les filières lettres, langues et éducation."),
]


def build_formations():
    """Génère 10 formations par établissement (200 au total) à partir des
    domaines de spécialité de chaque établissement et du catalogue de gabarits."""
    formations = []
    for etab in ETABLISSEMENTS:
        etab_domaines = etab["domaines"]
        is_public = etab["type"] == "PUBLIC"
        pool = []
        for dom in etab_domaines:
            for tpl in FORMATION_TEMPLATES.get(dom, []):
                pool.append((dom, tpl))
        # cycle sur le pool jusqu'à 10 formations, en variant légèrement le nom si répétition
        count_by_name = {}
        for i in range(10):
            dom, tpl = pool[i % len(pool)]
            nom, niveau, duree, mult, programmes = tpl
            occ = count_by_name.get(nom, 0)
            count_by_name[nom] = occ + 1
            final_nom = nom if occ == 0 else f"{nom} (Parcours {occ+1})"
            base_cost = 180000 if is_public else 550000
            cout = round(base_cost * mult / 5000) * 5000
            debouches = METIERS_BY_DOMAINE.get(dom, [])[:3]
            formations.append(dict(
                nom=final_nom,
                etablissement=etab["sigle"],
                domaine=dom,
                niveau=niveau,
                duree_annees=duree,
                cout_annuel=cout,
                frais_inscription=round(cout * 0.06 / 1000) * 1000,
                frais_dossier=5000,
                modalite="PRESENTIEL",
                importance_strategique="ELEVEE" if niveau in ("INGENIEUR", "DOCTORAT", "MASTER") else "MOYENNE",
                bourses_disponibles=is_public or etab["sigle"] in ("ESGIS", "ESIS", "EAMAU"),
                montant_bourse_max=300000 if is_public else 200000,
                taux_reussite=round(65 + (hash(final_nom + etab["sigle"]) % 20), 1),
                taux_insertion_6mois=round(50 + (hash(etab["sigle"] + final_nom) % 25), 1),
                taux_insertion_12mois=round(65 + (hash(final_nom) % 20), 1),
                salaire_sortie_moyen=round(150000 + mult * 120000, -3),
                programmes=programmes,
                serie_bac_admises=["C", "D"] if dom in (SCIENCES, INFO, ARCHI) else (
                    ["A", "B"] if dom in (LETTRES, DROIT, ARTS) else ["A", "C", "D", "G2"]),
                debouches_metiers=debouches,
                places_disponibles=40 if niveau in ("INGENIEUR", "DOCTORAT") else 80,
                dates_rentree=["2026-10-01"],
                date_limite_inscription="2026-09-15",
                is_featured=(i == 0),
            ))
    return formations


FORMATIONS = build_formations()
