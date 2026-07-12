# Implémentation du cahier des charges — AvenSU-Orienta

Ce document récapitule les modules implémentés dans la branche `feature/cahier-charge-impl`
pour couvrir les exigences fonctionnelles et techniques du cahier des charges.

## Périmètre couvert

Le projet existant couvrait déjà ~80% du cahier des charges (authentification email,
catalogue établissements/formations, tests RIASEC, dashboard, chatbot IA, communauté,
paiements Mobile Money, classements, etc.). Cette implémentation ajoute les **11 modules
manquants majeurs** identifiés lors de l'audit.

## Modules implémentés

### 1. Authentification à deux facteurs (2FA TOTP) — `apps/accounts`
- **Cahier des charges** : Section 3 — "Double authentification (2FA) obligatoire pour les comptes Établissements et Conseillers"
- **Modèles** : `TOTPDevice`, `TwoFactorChallenge`
- **Service** : `TwoFactorService` (setup, confirm, disable, backup codes, challenge/verify)
- **Middleware** : `TwoFactorEnforcementMiddleware` bloque l'accès tant que le 2FA n'est pas activé
- **7 endpoints API** : `/api/v1/auth/2fa/{setup,confirm,disable,backup/regenerate,challenge,verify,status}/`
- **Dépendances** : `pyotp`, `qrcode`, `django-otp`

### 2. Conformité RGPD — `apps/compliance` (nouvelle app)
- **Cahier des charges** : Section 3 — "Conformité stricte avec les réglementations sur la protection des données personnelles (ex: RGPD)"
- **4 modèles** : `ConsentementRGPD`, `DemandeRGPD`, `JournalTraitement`, `PolitiqueConservation`
- **9 types de consentement** tracés (inscription, tests, partage, marketing, etc.)
- **6 types de demandes RGPD** : accès (art.15), rectification (art.16), oubli (art.17), limitation (art.18), portabilité (art.20), opposition (art.21)
- **Service** : `RGPDService`
  - `collecter_donnees_utilisateur()` — export JSON structuré par catégorie
  - `exporter_donnees_utilisateur()` — fichier ZIP téléchargeable
  - `anonymiser_utilisateur()` — droit à l'oubli (irréversible)
  - `appliquer_politiques_conservation()` — tâche Celery de purge auto
- **7 endpoints API** : `/api/v1/rgpd/{consentements,demandes,export,droit-oubli,journal,politiques}/`
- **Commande** : `python manage.py seed_politiques_rgpd` (8 politiques par défaut)

### 3. Test Ikigai + Rapport combiné RIASEC × Ikigai — `apps/orientation`
- **Cahier des charges** : Section 2.1 — "Test Ikigai : Croisement des quatre piliers fondamentaux" + "Fusion intelligente et dynamique de plusieurs méthodologies"
- **Enum** : `TypeTest.IKIGAI`, `TypeTest.MIXTE`, `PilierIkigai` (PASSION/MISSION/VOCATION/PROFESSION)
- **Service** : `IkigaiScoringService`
  - 2 modes de calcul : structuré (dimensions taggées) + textuel (matching mots-clés)
  - 4 intersections calculées : Satisfaction, Excitation, Confort, Sécurité
  - Score global avec facteur d'équilibre
  - Recommandation de familles de métiers
- **Service** : `CombinedScoringService` — fusion RIASEC + Ikigai → rapport unifié
- **3 endpoints API** : `/api/v1/orientation/{ikigai/tests,ikigai/resultat,rapport-combine}/`

### 4. Bibliothèque numérique — `apps/library` (nouvelle app)
- **Cahier des charges** : Section 2.4 — "Bibliothèque Numérique : Base de connaissances centralisée regroupant des manuels scolaires, des annales d'examens corrigées et des cours de préparation aux filières du supérieur"
- **5 modèles** : `CategorieBibliotheque`, `RessourcePedagogique`, `TelechargementRessource`, `FavoriBibliotheque`, `VoteRessource`
- **8 types de ressources** : MANUEL, ANNALE, COURS_PREP, FICHE_REVISION, VIDEO, PODCAST, EXERCICE, DOCUMENT_RECHERCHE
- **7 niveaux scolaires** : COLLEGE → MASTER + PREPA_CONCOURS
- **Modèle freemium** : `is_premium` + `is_free` → contrôle d'accès via abonnement
- **Service** : `BibliothequeService` (recherche multi-critères, recommandations personnalisées, votes, favoris)
- **8 endpoints API** : `/api/v1/bibliotheque/`

### 5. Roadmap évolutive Collège/Lycée/Post-Bac — `apps/roadmap` (nouvelle app)
- **Cahier des charges** : Section 2.1 — "Roadmap Évolutive de l'Étudiant" avec 3 niveaux différenciés
- **3 modèles** : `EtapeRoadmap` (template), `EtapePersonnelleEtudiant` (instance), `JalonRoadmap` (événements datés)
- **3 phases** : COLLEGE (découverte), LYCEE (choix stratégiques), POST_BAC (admission & carrière)
- **9 catégories** d'étapes (DECOUVERTE, ORIENTATION, ACADEMIQUE, CONCOURS, CANDIDATURE, ADMISSION, STAGE, INSERTION, FINANCEMENT)
- **18 étapes par défaut** pré-remplies via `python manage.py seed_roadmap`
- **Service** : `RoadmapService` (initialisation idempotente, progression par phase, jalons à venir)
- **7 endpoints API** : `/api/v1/roadmap/`

### 6. Simulateur d'admissions prédictif — `apps/catalog`
- **Cahier des charges** : Section 2.1 — "Outil prédictif calculant le pourcentage de chances d'intégrer une formation spécifique en croisant la moyenne pondérée de l'élève avec les critères d'admission historiques de l'établissement"
- **2 modèles** : `AdmissionHistorique` (données passées anonymisées), `ResultatSimulateur` (simulations sauvegardées)
- **Service** : `SimulateurAdmissionService`
  - 2 modes : EMPIRIQUE (>= 15 enregistrements historiques) ou HEURISTIQUE (sinon)
  - Ajustement par écart vs moyenne des admis (bonus/malus ±20 pts)
  - Vérification d'éligibilité (série de bac)
  - 3 niveaux de confiance (Faible/Moyen/Élevé)
  - Explication détaillée + recommandations personnalisées
- **3 endpoints API** : `/api/v1/catalog/{simulateur/admission,simulateur/historique,etablissements/<id>/visite-3d}/`

### 7. Visites 3D campus + ateliers virtuels — `apps/catalog`
- **Cahier des charges** : Section 2.1 — "Découverte immersive et Carrières" + Section 2.2 — "Page vitrine : galerie pour la visite 3D"
- **4 champs ajoutés à `Etablissement`** :
  - `visite_virtuelle_url` (URL Matterport/Sketchfab/360°)
  - `galerie_3d` (JSON : liste de scènes 3D avec titre, type, URL, vignette)
  - `video_presentation_url` (YouTube/Vimeo)
  - `ateliers_virtuels_disponibles` (booléen)

### 8. CRM Établissements + Marketing ciblé + Leads qualifiés — `apps/marketing` (nouvelle app)
- **Cahier des charges** : Section 2.2 — "Outils de Visibilité et Marketing", "Gestion des Demandes d'Admission (CRM)", "Modèle au Lead Qualifié"
- **5 modèles** :
  - `SegmentCandidats` (critères démographiques + académiques + orientation)
  - `CampagneMarketing` (campagne d'un établissement)
  - `LeadQualifie` (candidat matchant un segment, avec score 0-100)
  - `CandidatureCRM` (candidature dans le pipeline de l'établissement)
  - `LogInteractionCRM` (audit trail des interactions)
- **Services** : `MarketingService` (ciblage, scoring, activation, facturation) + `CRMService` (changements de statut, stats, sync externe)
- **7 statuts de candidature** : RECUE → EN_REVUE → ACCEPTEE/REFUSEE/EN_ATTENTE → INSCRIT/DESISTE
- **Algorithme de matching** : 4 critères pondérés (niveau, série bac, moyenne, code RIASEC) → score 0-100
- **Facturation au lead** : déclenchée quand l'établissement initie un contact (modèle performance)
- **12 endpoints API** : `/api/v1/marketing/{segments,campagnes,leads,candidatures,pipeline}/`

## Modules pré-existants conservés

Le projet couvrait déjà (audit `rapport_audit.md`) :
- Authentification email + vérification token + reset password
- Modèle User personnalisé (email comme identifiant, 4 rôles : STUDENT/COUNSELOR/SCHOOL_REP/PARENT)
- Profils séparés (StudentProfile, CounselorProfile, SchoolRepProfile, ParentProfile)
- Vérification documents (CNI, diplôme, lettre de mission) avec validation admin
- Catalogue : Etablissement, Formation, Domaine, Metier
- Tests d'orientation RIASEC (avec scoring complet)
- Dashboard étudiant (voeux, demarches, agenda, favoris)
- Événements (JPO, ateliers, webinaires)
- Communauté (forum, messagerie, mentorat alumni)
- Chatbot AvenBot (vraie intégration Anthropic/OpenAI/Ollama)
- Notifications
- Analytics
- Paiements (Flooz, TMoney, abonnements freemium)
- Classements établissements/formations

## Installation

```bash
# Créer un venv Python 3.12+
python -m venv venv
source venv/bin/activate

# Installer les dépendances (y compris les nouvelles : pyotp, qrcode, django-otp, django-cryptography)
pip install -r requirements/dev.txt

# Configurer l'environnement
cp .env.example .env  # éditer avec vos valeurs
# DJANGO_SETTINGS_MODULE=config.settings.local  (pour SQLite local)

# Migrer
python manage.py migrate

# Seed initial (politiques RGPD + étapes de roadmap par défaut)
python manage.py seed_politiques_rgpd
python manage.py seed_roadmap

# Créer un superuser
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## Documentation API

- Swagger UI : http://localhost:8000/api/docs/
- ReDoc : http://localhost:8000/api/redoc/
- Schéma OpenAPI : http://localhost:8000/api/schema/

## Tests

```bash
pytest tests/ -v
```

## Liste complète des nouveaux endpoints API

| Module | Endpoint | Méthode | Description |
|---|---|---|---|
| 2FA | `/api/v1/auth/2fa/setup/` | POST | Initie le setup TOTP (secret + QR) |
| 2FA | `/api/v1/auth/2fa/confirm/` | POST | Confirme le code TOTP et active |
| 2FA | `/api/v1/auth/2fa/disable/` | POST | Désactive après vérification |
| 2FA | `/api/v1/auth/2fa/backup/regenerate/` | POST | Régénère les codes de secours |
| 2FA | `/api/v1/auth/2fa/challenge/` | POST | Crée un défi après étape 1 login |
| 2FA | `/api/v1/auth/2fa/verify/` | POST | Vérifie code + défi → JWT |
| 2FA | `/api/v1/auth/2fa/status/` | GET | Statut 2FA utilisateur courant |
| RGPD | `/api/v1/rgpd/consentements/` | GET/POST | Liste et crée des consentements |
| RGPD | `/api/v1/rgpd/consentements/<type>/` | DELETE | Retire un consentement |
| RGPD | `/api/v1/rgpd/demandes/` | GET/POST | Liste et crée des demandes RGPD |
| RGPD | `/api/v1/rgpd/export/` | GET | Export ZIP des données (art.15+20) |
| RGPD | `/api/v1/rgpd/droit-oubli/` | POST | Anonymise le compte (art.17) |
| RGPD | `/api/v1/rgpd/journal/` | GET | Journal des accès à mes données |
| RGPD | `/api/v1/rgpd/politiques/` | GET | Politiques de conservation |
| Ikigai | `/api/v1/orientation/ikigai/tests/` | GET | Liste des tests Ikigai |
| Ikigai | `/api/v1/orientation/ikigai/resultat/` | GET | Dernier résultat Ikigai |
| Ikigai | `/api/v1/orientation/rapport-combine/` | GET | Rapport RIASEC × Ikigai |
| Biblio | `/api/v1/bibliotheque/` | GET | Liste ressources (filtres) |
| Biblio | `/api/v1/bibliotheque/<slug>/` | GET | Détail ressource |
| Biblio | `/api/v1/bibliotheque/<slug>/download/` | GET | Téléchargement (check premium) |
| Biblio | `/api/v1/bibliotheque/<slug>/vote/` | POST | Vote 1-5 |
| Biblio | `/api/v1/bibliotheque/<slug>/favori/` | POST/DELETE | Toggle favori |
| Biblio | `/api/v1/bibliotheque/recommandations/` | GET | Recommandations personnalisées |
| Biblio | `/api/v1/bibliotheque/categories/` | GET | Arbre catégories |
| Biblio | `/api/v1/bibliotheque/stats/` | GET | Statistiques globales |
| Roadmap | `/api/v1/roadmap/progression/` | GET | Progression par phase |
| Roadmap | `/api/v1/roadmap/init/` | POST | Initialise roadmap étudiant |
| Roadmap | `/api/v1/roadmap/etapes/` | GET/POST | Liste et crée étapes |
| Roadmap | `/api/v1/roadmap/etapes/<pk>/` | GET/PUT/DELETE | Détail étape |
| Roadmap | `/api/v1/roadmap/etapes/<pk>/<action>/` | POST | complete/start/block/reset |
| Roadmap | `/api/v1/roadmap/etapes-a-venir/` | GET | Étapes non complétées |
| Roadmap | `/api/v1/roadmap/jalons/` | GET | Jalons à venir |
| Simulateur | `/api/v1/catalog/simulateur/admission/` | POST | Lance une simulation |
| Simulateur | `/api/v1/catalog/simulateur/historique/` | GET | Historique simulations |
| 3D | `/api/v1/catalog/etablissements/<id>/visite-3d/` | GET | Données visite virtuelle |
| Marketing | `/api/v1/marketing/segments/` | GET/POST | Segments de ciblage |
| Marketing | `/api/v1/marketing/campagnes/` | GET/POST | Campagnes marketing |
| Marketing | `/api/v1/marketing/campagnes/<pk>/activer/` | POST | Active + génère leads |
| Marketing | `/api/v1/marketing/campagnes/<pk>/stats/` | GET | Stats campagne |
| Marketing | `/api/v1/marketing/leads/` | GET | Liste leads |
| Marketing | `/api/v1/marketing/leads/<pk>/facturer/` | POST | Facture un lead |
| CRM | `/api/v1/marketing/candidatures/` | GET/POST | Candidatures CRM |
| CRM | `/api/v1/marketing/candidatures/<pk>/<action>/` | POST | accepter/refuser/attente/inscrire |
| CRM | `/api/v1/marketing/candidatures/<pk>/sync/` | POST | Sync API externe |
| CRM | `/api/v1/marketing/pipeline/stats/` | GET | Stats pipeline |

## Limitations et étapes suivantes

Cette implémentation couvre le **backend complet** (modèles + services + API) pour les
11 modules manquants. Les étapes complémentaires recommandées :

1. **Templates HTML** : Les vues web existent (`urls.py` dans chaque app) mais les templates
   ne sont pas créés — le frontend Flutter ou les templates Django restent à développer.
2. **Tests unitaires** : La suite de tests existante ne couvre pas les nouveaux modules.
   Ajouter `tests/test_two_factor.py`, `tests/test_rgpd.py`, `tests/test_ikigai.py`, etc.
3. **Social auth Google/Apple** : Non implémenté (nécessite `django-allauth` + clés OAuth).
   Le modèle User supporte déjà ce flux via l'ajout d'un `SocialAccount`.
4. **Chiffrement E2E des données sensibles** : `django-cryptography` est installé mais
   les champs sensibles (notes, messages, consentements) ne sont pas encore chiffrés au repos.
5. **Rattachement parent/tuteur avec validation email** : `ParentProfile` existe avec
   `enfants_suivis` M2M, mais le flux de validation par email token n'est pas implémenté.
6. **Sessions collectives conseiller** : `RendezVous` est 1-to-1 ; manque un modèle
   `SessionCollective` pour les sessions groupe.
7. **Avis certifiés alumni** : `TypeMentor.ANCIEN` existe ; manque le modèle `AvisAlumni`
   avec flag `is_certified`.
8. **Stripe** : Les champs `stripe_price_id` existent sur `PlanAbonnement` mais le SDK
   Stripe n'est pas installé ni le service implémenté.

## Branche Git

Tous ces changements sont sur la branche `feature/cahier-charge-impl` :
```
https://github.com/ErdisKodjo/jpope_app/tree/feature/cahier-charge-impl
```

Pull request à créer depuis :
```
https://github.com/ErdisKodjo/jpope_app/pull/new/feature/cahier-charge-impl
```

## Commits

1. `fix` — Corrige 3 bugs pré-existants bloquants (imports Greatest + clash related_name)
2. `feat(2FA)` — Authentification à deux facteurs TOTP
3. `feat(rgpd)` — Nouvelle app compliance (consentements, export, oubli, journal)
4. `feat(orientation)` — Test Ikigai + rapport combiné RIASEC × Ikigai
5. `feat(library)` — Nouvelle app bibliothèque numérique
6. `feat(roadmap)` — Nouvelle app roadmap évolutive 3 phases
7. `feat(catalog)` — Simulateur d'admissions prédictif + visites 3D
8. `feat(marketing)` — Nouvelle app CRM + campagnes + leads qualifiés
9. `chore(migrations)` — Génère les migrations manquantes
