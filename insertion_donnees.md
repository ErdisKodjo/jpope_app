# Guide d'insertion des données — AvenSU-Orienta

> **Ordre obligatoire d'insertion** : Domaine → Établissement → Métier → Formation → Événement → Forum → Classement → Conseiller
>
> Les slugs sont auto-générés à partir du nom. Ne pas renseigner sauf besoin de personnalisation.
> Les champs marqués `*` sont **obligatoires**. Tous les autres sont optionnels.

---

## NIVEAU 1 — Domaines

**Table** : `catalog_domaine`  
**Images** : aucune image directe — utiliser une icône emoji ou classe FontAwesome dans le champ `icon`.

| Champ | Type | Obligatoire | Valeurs possibles / Exemple |
|---|---|---|---|
| `nom` | texte | * | `Informatique & Numérique` |
| `slug` | texte | auto | `informatique-numerique` ← généré |
| `description` | texte long | — | Description en 2-3 phrases |
| `icon` | texte | — | `💻` · `🏥` · `⚖️` · `📊` · `🔬` |
| `couleur` | hex | — | `#3B82F6` (défaut) |
| `nombre_formations` | entier | — | `0` (mis à jour automatiquement) |
| `nombre_metiers` | entier | — | `0` (mis à jour automatiquement) |
| `is_active` | booléen | — | `true` |
| `ordre` | entier | — | `1` à `N` — contrôle l'ordre d'affichage |

### Exemples de domaines à insérer

```
1. nom=Informatique & Numérique       icon=💻  couleur=#3B82F6  ordre=1
2. nom=Santé & Médecine               icon=🏥  couleur=#EF4444  ordre=2
3. nom=Droit & Sciences Politiques    icon=⚖️  couleur=#8B5CF6  ordre=3
4. nom=Gestion & Commerce             icon=📊  couleur=#F59E0B  ordre=4
5. nom=Sciences & Ingénierie          icon=🔬  couleur=#10B981  ordre=5
6. nom=Lettres & Sciences Humaines    icon=📚  couleur=#EC4899  ordre=6
7. nom=Architecture & BTP             icon=🏗️  couleur=#6366F1  ordre=7
8. nom=Agriculture & Environnement    icon=🌱  couleur=#84CC16  ordre=8
9. nom=Arts, Design & Communication   icon=🎨  couleur=#F97316  ordre=9
10. nom=Finance & Comptabilité        icon=💰  couleur=#0EA5E9  ordre=10
```

---

## NIVEAU 2 — Établissements

**Table** : `catalog_etablissement`

### Images requises

| Champ image | Chemin de dépôt | Format recommandé | Nom suggéré |
|---|---|---|---|
| `logo` | `media/etablissements/logos/2026/` | PNG transparent, 400×160 px | `logo_<sigle>.png` ex: `logo_ul.png` |
| `banniere` | `media/etablissements/bannieres/2026/` | JPG/WebP, 1200×400 px | `banniere_<sigle>.jpg` ex: `banniere_ul.jpg` |

### Champs à renseigner

| Champ | Type | Obligatoire | Valeurs / Exemple |
|---|---|---|---|
| `nom` | texte | * | `Université de Lomé` |
| `sigle` | texte | — | `UL` |
| `description` | texte long | — | Présentation de l'établissement |
| `description_courte` | texte (500) | — | Résumé pour les listes |
| `logo` | image | — | `logo_ul.png` |
| `banniere` | image | — | `banniere_ul.jpg` |
| `type` | choix | * | `PUBLIC` · `PRIVE_LAIC` · `PRIVE_CONFESSIONNEL` · `INTERNATIONAL` · `GRANDE_ECOLE` |
| `statut` | choix | * | `AGREÉ` · `RECONNU` · `AUTORISE` · `ACCREDITE` · `NON_ACCREDITE` · `EN_EVALUATION` |
| `date_creation` | entier | — | `1970` |
| `adresse` | texte | — | `Boulevard du 13 Janvier, Lomé` |
| `ville` | texte | * | `Lomé` · `Kara` · `Sokodé` · `Atakpamé` |
| `pays` | texte | — | `Togo` (défaut) |
| `latitude` | décimal | — | `6.137069` |
| `longitude` | décimal | — | `1.222210` |
| `site_web` | URL | — | `https://univ-lome.tg` |
| `email` | email | — | `info@univ-lome.tg` |
| `telephone` | texte | — | `+228 22 25 50 04` |
| `facebook` | URL | — | `https://facebook.com/univlome` |
| `linkedin` | URL | — | |
| `frais_inscription_min` | FCFA | — | `25000` |
| `frais_inscription_max` | FCFA | — | `50000` |
| `frais_scolarite_annuel_min` | FCFA | — | `150000` |
| `frais_scolarite_annuel_max` | FCFA | * | `400000` |
| `nombre_etudiants` | entier | — | `12000` |
| `nombre_enseignants` | entier | — | `450` |
| `taux_encadrement` | décimal | — | `26.7` (étudiants/enseignant) |
| `taux_reussite` | % (0-100) | — | `72.5` |
| `taux_insertion_professionnelle` | % (0-100) | — | `68.0` |
| `note_globale` | 0-5 | — | `3.80` |
| `classement_national` | entier | — | `1` |
| `classement_regional` | entier | — | `12` |
| `score_qualite_global` | 0-100 | — | `74.5` |
| `equipements` | JSON liste | — | `["Bibliothèque", "Labo informatique", "Wifi", "Restaurant", "Clinique"]` |
| `labels_qualite` | JSON liste | — | `["Accrédité CAMES", "Membre AUF"]` |
| `domaines_enseignes` | M2M → Domaine | — | slugs des domaines liés |
| `propose_bourses` | booléen | — | `true` |
| `montant_bourse_max` | FCFA | — | `500000` |
| `criteres_bourses` | JSON liste | — | `["Mérite", "Ressources limitées"]` |
| `residences_universitaires` | booléen | — | `true` |
| `clubs_et_associations` | JSON liste | — | `["Club Informatique", "Association Sportive"]` |
| `sports_proposes` | JSON liste | — | `["Football", "Basketball", "Athlétisme"]` |
| `is_verified` | booléen | — | `true` |
| `is_featured` | booléen | — | `false` |

### Exemples d'établissements à insérer (Togo)

```
1.  sigle=UL        nom=Université de Lomé                          type=PUBLIC            ville=Lomé
2.  sigle=UPET      nom=Université de Kara (Pya)                    type=PUBLIC            ville=Kara
3.  sigle=ESGIS     nom=École Supérieure de Gestion, d'Informatique et des Sciences  type=PRIVE_LAIC  ville=Lomé
4.  sigle=ESIS      nom=École Supérieure d'Ingénierie et des Sciences  type=PRIVE_LAIC     ville=Lomé
5.  sigle=IAD       nom=Institut Africain de Développement                           type=PRIVE_LAIC  ville=Lomé
6.  sigle=UCAO      nom=Université Catholique de l'Afrique de l'Ouest               type=PRIVE_CONFESSIONNEL  ville=Lomé
7.  sigle=EST       nom=École Supérieure de Technologie                              type=GRANDE_ECOLE  ville=Lomé
8.  sigle=FODEF     nom=Formation pour le Développement                              type=PRIVE_LAIC  ville=Lomé
9.  sigle=IST       nom=Institut Supérieur de Technologie                            type=PRIVE_LAIC  ville=Lomé
10. sigle=INFA      nom=Institut National de Formation Agricole                      type=PUBLIC      ville=Tové
```

---

## NIVEAU 3 — Métiers

**Table** : `catalog_metier`  
**Images** : aucune — illustration via `icon` dans le domaine parent.

| Champ | Type | Obligatoire | Valeurs / Exemple |
|---|---|---|---|
| `nom` | texte | * | `Développeur Logiciel` |
| `domaine` | FK → Domaine | * | slug du domaine ex: `informatique-numerique` |
| `description` | texte long | — | Description complète du métier |
| `description_courte` | texte (300) | — | Résumé pour les cartes |
| `revenu_min` | FCFA/mois | * | `150000` |
| `revenu_max` | FCFA/mois | * | `1200000` |
| `revenu_moyen` | FCFA/mois | * | `450000` |
| `taux_emploi` | % (0-100) | — | `82.0` |
| `demande_marche` | choix | — | `TRES_FORTE` · `FORTE` · `MOYENNE` · `FAIBLE` · `EN_DECLIN` |
| `niveau_etude_requis` | choix | — | `BAC` · `BAC+2` · `BAC+3` · `BAC+5` · `BAC+8` |
| `duree_formation_typique_annees` | entier | — | `3` |
| `competences_cles` | JSON liste | — | `["Python", "JavaScript", "Base de données", "Git"]` |
| `taches_principales` | JSON liste | — | `["Développement back-end", "Tests unitaires", "Documentation"]` |
| `perspectives_evolution` | texte long | — | Description des évolutions de carrière |
| `pays_concernes` | JSON liste | * | `["Togo", "Bénin", "Côte d'Ivoire", "Sénégal"]` |
| `villes_principales` | JSON liste | — | `["Lomé", "Abidjan", "Dakar"]` |
| `source_donnees` | texte | — | `INS Togo 2025 · Enquête emploi ANPE` |
| `date_mise_a_jour` | date | — | `2026-01-15` |

> **Note** : `score_attractivite` est **calculé automatiquement** à chaque `save()` — ne pas renseigner.

### Exemples de métiers par domaine

```
Informatique & Numérique
  1. Développeur Logiciel        revenu_moy=450000  demande=TRES_FORTE   taux_emploi=85
  2. Data Analyst / Data Scientist  revenu_moy=550000  demande=TRES_FORTE   taux_emploi=80
  3. Administrateur Réseau       revenu_moy=380000  demande=FORTE        taux_emploi=78
  4. Chef de Projet IT           revenu_moy=600000  demande=FORTE        taux_emploi=76
  5. Cybersécurité (Analyste)    revenu_moy=700000  demande=TRES_FORTE   taux_emploi=82

Santé & Médecine
  6. Médecin généraliste         revenu_moy=800000  demande=TRES_FORTE   taux_emploi=92
  7. Infirmier(ère) diplômé(e)   revenu_moy=350000  demande=FORTE        taux_emploi=90
  8. Pharmacien(ne)              revenu_moy=650000  demande=FORTE        taux_emploi=88

Gestion & Commerce
  9. Comptable / Auditeur        revenu_moy=400000  demande=FORTE        taux_emploi=75
 10. Responsable Commercial      revenu_moy=500000  demande=FORTE        taux_emploi=72
 11. Gestionnaire RH             revenu_moy=380000  demande=MOYENNE      taux_emploi=68

Finance & Comptabilité
 12. Analyste Financier          revenu_moy=600000  demande=FORTE        taux_emploi=74
 13. Expert-Comptable            revenu_moy=750000  demande=FORTE        taux_emploi=80

Sciences & Ingénierie
 14. Ingénieur Génie Civil       revenu_moy=700000  demande=FORTE        taux_emploi=78
 15. Ingénieur Électrique        revenu_moy=650000  demande=FORTE        taux_emploi=76
```

---

## NIVEAU 4 — Formations

**Table** : `catalog_formation`  
**Images** : aucune image propre — hérite des images de l'établissement.

| Champ | Type | Obligatoire | Valeurs / Exemple |
|---|---|---|---|
| `nom` | texte | * | `Licence Informatique` |
| `etablissement` | FK → Établissement | * | sigle/slug ex: `universite-de-lome` |
| `domaine` | FK → Domaine | * | slug ex: `informatique-numerique` |
| `debouches` | M2M → Métier | — | slugs des métiers accessibles |
| `description` | texte long | — | Description complète du programme |
| `description_courte` | texte (400) | — | Résumé pour les listes |
| `niveau` | choix | * | `CERTIFICAT` · `BTS` · `DUT` · `LICENCE` · `MASTER` · `DOCTORAT` · `INGENIEUR` · `ECOLE` |
| `duree_annees` | entier (1-10) | * | `3` |
| `modalite` | choix | — | `PRESENTIEL` · `DISTANCIEL` · `HYBRIDE` · `ALTERNANCE` |
| `cout_annuel` | FCFA | * | `350000` |
| `frais_inscription` | FCFA | — | `30000` |
| `frais_dossier` | FCFA | — | `5000` |
| `bourses_disponibles` | booléen | — | `true` |
| `montant_bourse_max` | FCFA | — | `300000` |
| `facilites_paiement` | booléen | — | `true` |
| `importance_strategique` | choix | — | `CRITIQUE` · `ELEVEE` · `MOYENNE` · `FAIBLE` |
| `taux_reussite` | % (0-100) | — | `75.0` |
| `taux_insertion_6mois` | % (0-100) | — | `62.0` |
| `taux_insertion_12mois` | % (0-100) | — | `78.0` |
| `salaire_sortie_moyen` | FCFA/mois | — | `320000` |
| `prerequis` | JSON liste | — | `["BAC C ou D", "Mention Passable minimum"]` |
| `serie_bac_admises` | JSON liste | — | `["C", "D", "G2"]` |
| `programmes` | JSON liste | — | `["Algorithmique", "Base de données", "Réseaux", "POO", "Projet tutoré"]` |
| `dates_rentree` | JSON liste | — | `["2026-10-01"]` |
| `date_limite_inscription` | date | — | `2026-09-15` |
| `places_disponibles` | entier | — | `80` |
| `is_featured` | booléen | — | `false` |

> **Note** : `score_qualite` est **calculé automatiquement** — ne pas renseigner.

### Exemples de formations à insérer

```
Établissement UL — Université de Lomé
  1. nom=Licence Informatique           niveau=LICENCE    duree=3  cout=200000  imp=ELEVEE
  2. nom=Master Informatique            niveau=MASTER     duree=2  cout=350000  imp=ELEVEE
  3. nom=Licence Gestion                niveau=LICENCE    duree=3  cout=180000  imp=MOYENNE
  4. nom=Licence Droit                  niveau=LICENCE    duree=3  cout=150000  imp=MOYENNE
  5. nom=Doctorat Sciences              niveau=DOCTORAT   duree=3  cout=300000  imp=ELEVEE

Établissement ESGIS
  6. nom=BTS Informatique               niveau=BTS        duree=2  cout=500000  imp=ELEVEE
  7. nom=Licence Management             niveau=LICENCE    duree=3  cout=650000  imp=MOYENNE
  8. nom=Master Finance-Comptabilité    niveau=MASTER     duree=2  cout=800000  imp=ELEVEE

Établissement ESIS
  9. nom=Diplôme Ingénieur Informatique  niveau=INGENIEUR  duree=5  cout=900000  imp=CRITIQUE
 10. nom=Diplôme Ingénieur Génie Civil   niveau=INGENIEUR  duree=5  cout=850000  imp=CRITIQUE
```

---

## NIVEAU 5 — Événements

**Table** : `events_evenement`

### Images requises

| Champ image | Chemin de dépôt | Format recommandé | Nom suggéré |
|---|---|---|---|
| `image_principale` | `media/evenements/2026/07/` | JPG/WebP, 800×450 px (16:9) | `evt_<slug>.jpg` ex: `evt_jpo_ul_2026.jpg` |
| `image_couverture` | `media/evenements/couvertures/2026/07/` | JPG/WebP, 1200×400 px | `cover_<slug>.jpg` ex: `cover_jpo_ul_2026.jpg` |

### Champs à renseigner

| Champ | Type | Obligatoire | Valeurs / Exemple |
|---|---|---|---|
| `titre` | texte | * | `Journée Portes Ouvertes UL 2026` |
| `description` | texte long | — | Programme détaillé de l'événement |
| `description_courte` | texte (300) | — | Résumé pour les listes |
| `image_principale` | image | — | `evt_jpo_ul_2026.jpg` |
| `image_couverture` | image | — | `cover_jpo_ul_2026.jpg` |
| `type` | choix | * | `JPO` · `SALON` · `CONFERENCE` · `WEBINAIRE` · `ATELIER` · `SEANCE_INFO` · `CONCOURS` · `PRESELECTION` · `ORIENTATION` · `RENCONTRE` · `VISITE` · `AUTRE` |
| `format` | choix | — | `PRESENTIEL` · `EN_LIGNE` · `HYBRIDE` |
| `statut` | choix | * | `PUBLIE` (pour qu'il soit visible) |
| `cible` | choix | — | `TOUS` · `TERMINALES` · `LICENCE` · `MASTER` · `PARENTS` · `CONSEILLERS` · `PROFESSIONNELS` |
| `priorite` | choix | — | `BASSE` · `NORMALE` · `HAUTE` · `CRITIQUE` |
| `date_debut` | datetime | * | `2026-09-15 09:00:00` |
| `date_fin` | datetime | — | `2026-09-15 17:00:00` |
| `date_limite_inscription` | datetime | — | `2026-09-12 23:59:00` |
| `lieu_nom` | texte | — | `Campus principal UL` |
| `adresse` | texte | — | `Boulevard du 13 Janvier, Lomé` |
| `ville` | texte | — | `Lomé` |
| `lien_visio` | URL | — | Pour les événements en ligne |
| `plateforme_visio` | texte | — | `Zoom` · `Google Meet` · `Teams` |
| `capacite_max` | entier | — | `200` · `0` = illimité |
| `inscriptions_ouvertes` | booléen | — | `true` |
| `est_gratuit` | booléen | — | `true` |
| `cout_participation` | FCFA | — | `0` |
| `etablissement` | FK → Établissement | — | sigle ex: `UL` |
| `programme` | JSON liste | — | `[{"heure": "09:00", "titre": "Accueil"}, {"heure": "10:00", "titre": "Présentation filières"}]` |
| `intervenants` | JSON liste | — | `[{"nom": "Dr. Akakpo", "fonction": "Directeur pédagogique", "bio": "..."}]` |
| `tags` | JSON liste | — | `["informatique", "bac+3", "lomé", "licence"]` |
| `domaines_concernes` | M2M → Domaine | — | slugs des domaines |
| `email_contact` | email | — | `jpo@univ-lome.tg` |
| `telephone_contact` | texte | — | `+228 22 25 50 04` |
| `published_at` | datetime | — | Date de publication (auto si laissé vide) |

### Exemples d'événements à insérer

```
1. titre=Journée Portes Ouvertes UL 2026          type=JPO          statut=PUBLIE  date=2026-09-15 09:00  etab=UL
2. titre=Salon des Formations Supérieures Lomé     type=SALON        statut=PUBLIE  date=2026-08-20 08:00
3. titre=Conférence Métiers du Numérique           type=CONFERENCE   statut=PUBLIE  date=2026-08-05 14:00
4. titre=Webinaire Orientation Post-Bac            type=WEBINAIRE    statut=PUBLIE  date=2026-07-25 15:00  format=EN_LIGNE
5. titre=Journée Portes Ouvertes ESGIS 2026        type=JPO          statut=PUBLIE  date=2026-09-22 09:00  etab=ESGIS
6. titre=Concours d'entrée ESIS 2026               type=CONCOURS     statut=PUBLIE  date=2026-07-10 08:00  etab=ESIS
7. titre=Atelier CV et Lettre de Motivation        type=ATELIER      statut=PUBLIE  date=2026-08-12 10:00
8. titre=Rencontre Professionnels du Droit         type=RENCONTRE    statut=PUBLIE  date=2026-08-28 14:00
```

---

## NIVEAU 6 — Forums Communauté

**Table** : `community_forum`  
**Images** : aucune — illustration via emoji `icone`.

| Champ | Type | Obligatoire | Valeurs / Exemple |
|---|---|---|---|
| `nom` | texte | * | `Informatique & Tech` |
| `description` | texte long | — | Description du forum |
| `icone` | emoji | — | `💻` · `🏥` · `📊` · `🎓` · `💬` |
| `couleur` | hex | — | `#3B82F6` |
| `type` | choix | * | `GENERAL` · `PAR_DOMAINE` · `PAR_ETABLISSEMENT` · `ENTRAIDE` · `EMPLOI` · `INTERNATIONAL` |
| `domaine` | FK → Domaine | — | Pour les forums par domaine |
| `etablissement` | FK → Établissement | — | Pour les forums par établissement |
| `moderation_auto` | booléen | — | `false` |
| `acces_restreint` | booléen | — | `false` |
| `is_active` | booléen | — | `true` |
| `is_featured` | booléen | — | `false` |
| `ordre` | entier | — | `1` à `N` |

### Exemples de forums à insérer

```
1. nom=Général & Bienvenue             type=GENERAL          icone=👋  ordre=1
2. nom=Informatique & Tech             type=PAR_DOMAINE      icone=💻  ordre=2  domaine=informatique-numerique
3. nom=Santé & Médecine                type=PAR_DOMAINE      icone=🏥  ordre=3  domaine=sante-medecine
4. nom=Gestion & Commerce              type=PAR_DOMAINE      icone=📊  ordre=4  domaine=gestion-commerce
5. nom=Droit & Sciences Politiques     type=PAR_DOMAINE      icone=⚖️  ordre=5  domaine=droit-sciences-politiques
6. nom=Sciences & Ingénierie           type=PAR_DOMAINE      icone=🔬  ordre=6  domaine=sciences-ingenierie
7. nom=Forum Université de Lomé        type=PAR_ETABLISSEMENT icone=🎓  ordre=7  etab=UL
8. nom=Forum ESGIS                     type=PAR_ETABLISSEMENT icone=🎓  ordre=8  etab=ESGIS
9. nom=Offres d'emploi & Stages        type=EMPLOI           icone=💼  ordre=9
10. nom=Études à l'international        type=INTERNATIONAL    icone=✈️  ordre=10
11. nom=Entraide & Questions pratiques  type=ENTRAIDE         icone=🤝  ordre=11
```

---

## NIVEAU 7 — Classements

**Table** : `ranking_classement`  
**Images** : aucune.

| Champ | Type | Obligatoire | Valeurs / Exemple |
|---|---|---|---|
| `etablissement` | FK → Établissement | * | slug de l'établissement |
| `annee` | entier | * | `2026` |
| `rang_national` | entier | — | `1` à `N` |
| `rang_regional` | entier | — | `1` à `N` |
| `score_final` | 0-100 | * | `78.5` |
| `details_scores` | JSON objet | — | voir format ci-dessous |

#### Format `details_scores`
```json
{
  "qualite_enseignement": 82.0,
  "insertion_professionnelle": 75.0,
  "recherche": 45.0,
  "infrastructures": 80.0,
  "vie_etudiante": 70.0,
  "accessibilite_financiere": 85.0
}
```

### Exemples de classements à insérer (année 2026)

```
rang  etablissement  score_final  details_scores (résumé)
  1   UL             78.5         qualité=82  insertion=75  infra=80
  2   ESIS           75.2         qualité=80  insertion=72  infra=70
  3   ESGIS          72.8         qualité=74  insertion=78  infra=68
  4   UCAO           70.1         qualité=75  insertion=70  infra=72
  5   EST            68.9         qualité=70  insertion=72  infra=66
```

---

## NIVEAU 8 — Comptes Utilisateurs (Conseillers)

**Table** : `accounts_user` + `accounts_counselorprofile`

### Images requises

| Champ image | Chemin de dépôt | Format recommandé | Nom suggéré |
|---|---|---|---|
| `avatar` (profil) | `media/avatars/` | JPG, 400×400 px (carré) | `avatar_<prenom>_<nom>.jpg` ex: `avatar_kokou_mensah.jpg` |

### Champs User

| Champ | Type | Obligatoire | Valeurs / Exemple |
|---|---|---|---|
| `email` | email | * | `k.mensah@avensu.tg` |
| `first_name` | texte | * | `Kokou` |
| `last_name` | texte | * | `Mensah` |
| `phone` | texte | — | `+228 91 23 45 67` |
| `role` | choix | * | `COUNSELOR` |
| `password` | hash | * | Utiliser `set_password()` |
| `is_active` | booléen | — | `true` |

### Champs CounselorProfile

| Champ | Type | Obligatoire | Valeurs / Exemple |
|---|---|---|---|
| `specialites` | JSON liste | — | `["Informatique", "Gestion", "Orientation post-bac"]` |
| `qualifications` | texte long | — | `Doctorat en Sciences de l'Éducation, Université de Lomé` |
| `annees_experience` | entier | — | `8` |
| `tarif_horaire` | FCFA | — | `15000` |
| `bio` | texte long | — | Présentation personnelle du conseiller |
| `disponible` | booléen | — | `true` |

### Exemples de conseillers à insérer

```
1. email=k.mensah@avensu.tg       prenom=Kokou    nom=Mensah     exp=8   tarif=15000  spec=["Informatique","Gestion"]
2. email=a.koffi@avensu.tg        prenom=Ama      nom=Koffi      exp=12  tarif=20000  spec=["Santé","Médecine"]
3. email=e.agbeko@avensu.tg       prenom=Edem     nom=Agbeko     exp=5   tarif=12000  spec=["Droit","Sciences Politiques"]
4. email=m.aziabeme@avensu.tg     prenom=Mawuli   nom=Aziabémé   exp=10  tarif=18000  spec=["Finance","Comptabilité"]
5. email=s.abotsi@avensu.tg       prenom=Sena     nom=Abotsi     exp=6   tarif=12000  spec=["Lettres","Sciences Humaines"]
```

---

## Récapitulatif des images à préparer

| Entité | Champ | Dossier de dépôt | Dimensions | Format | Convention de nommage |
|---|---|---|---|---|---|
| Établissement | `logo` | `media/etablissements/logos/2026/` | 400×160 px | PNG transparent | `logo_<SIGLE>.png` |
| Établissement | `banniere` | `media/etablissements/bannieres/2026/` | 1200×400 px | JPG/WebP | `banniere_<SIGLE>.jpg` |
| Événement | `image_principale` | `media/evenements/2026/07/` | 800×450 px | JPG/WebP | `evt_<slug>.jpg` |
| Événement | `image_couverture` | `media/evenements/couvertures/2026/07/` | 1200×400 px | JPG/WebP | `cover_<slug>.jpg` |
| Utilisateur/Conseiller | `avatar` | `media/avatars/` | 400×400 px | JPG | `avatar_<prenom>_<nom>.jpg` |

### Liste complète des images pour les 10 établissements

```
logos/
  logo_UL.png
  logo_UPET.png
  logo_ESGIS.png
  logo_ESIS.png
  logo_IAD.png
  logo_UCAO.png
  logo_EST.png
  logo_FODEF.png
  logo_IST.png
  logo_INFA.png

bannieres/
  banniere_UL.jpg
  banniere_UPET.jpg
  banniere_ESGIS.jpg
  banniere_ESIS.jpg
  banniere_IAD.jpg
  banniere_UCAO.jpg
  banniere_EST.jpg
  banniere_FODEF.jpg
  banniere_IST.jpg
  banniere_INFA.jpg
```

### Liste complète des images pour les 8 événements

```
evenements/
  evt_jpo_ul_2026.jpg            cover_jpo_ul_2026.jpg
  evt_salon_formations_lome.jpg  cover_salon_formations_lome.jpg
  evt_conf_metiers-numerique.jpg cover_conf_metiers-numerique.jpg
  evt_webinaire_orientation.jpg  cover_webinaire_orientation.jpg
  evt_jpo_esgis_2026.jpg         cover_jpo_esgis_2026.jpg
  evt_concours_esis_2026.jpg     cover_concours_esis_2026.jpg
  evt_atelier_cv.jpg             cover_atelier_cv.jpg
  evt_rencontre_droit.jpg        cover_rencontre_droit.jpg
```

### Liste complète des avatars conseillers

```
avatars/
  avatar_kokou_mensah.jpg
  avatar_ama_koffi.jpg
  avatar_edem_agbeko.jpg
  avatar_mawuli_aziabeme.jpg
  avatar_sena_abotsi.jpg
```

---

## Notes de production

- **FCFA** : tous les montants sont en francs CFA (XOF). 1 EUR ≈ 655 FCFA.
- **Slugs** : générés automatiquement depuis `nom` via `django.utils.text.slugify`. Ex : `Université de Lomé` → `universite-de-lome`.
- **Scores calculés** : `score_qualite` (Formation) et `score_attractivite` (Métier) sont recalculés à chaque `save()`. Ne pas les renseigner manuellement.
- **Insertion via l'admin Django** : aller sur `/admin/` avec un compte `ADMIN`. L'admin Django permet l'insertion unitaire et l'import CSV (via `django-import-export` si installé).
- **Insertion en masse** : utiliser un script de seed (`python manage.py shell`) ou un fichier `fixtures/` JSON.
- **Ordre strict** : respecter l'ordre des niveaux 1→8 pour éviter les erreurs de clé étrangère.
