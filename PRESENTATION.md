# AvenSU-Orienta — Présentation du projet

---

## 1. Contexte : le pourquoi de ce projet

### Un problème réel, mal résolu

Chaque année au Togo et en Afrique de l'Ouest, des dizaines de milliers de bacheliers se retrouvent face à une même impasse : choisir une filière supérieure sans information fiable, sans accompagnement structuré, souvent sous pression familiale et avec des ressources financières limitées.

Les conséquences sont lourdes :

- **Mauvaise orientation** → décrochage en cours de première année
- **Formations choisies par défaut** plutôt que par vocation ou débouché réel
- **Coût humain et financier** des réorientations tardives pour les familles
- **Déséquilibre du marché du travail** : surinscription dans certaines filières, pénurie dans d'autres (santé, ingénierie, agri-tech)

### Ce qui existait avant

Les ressources disponibles étaient soit **éparpillées** (sites d'établissements hétérogènes, groupes Facebook, bouche-à-oreille), soit **inaccessibles** (cabinets d'orientation privés onéreux réservés à une élite). Il n'existait aucun outil numérique centralisé, gratuit et adapté au contexte togolais.

### La réponse : AvenSU-Orienta

**AvenSU-Orienta** est une plateforme web d'orientation post-bac pensée pour les étudiants d'Afrique de l'Ouest. Elle agrège en un seul endroit :

- un **catalogue vérifiable** de formations et d'établissements avec données réelles (frais, taux de réussite, débouchés, classements) ;
- des **tests psychométriques** (modèle RIASEC) pour aider l'étudiant à identifier ses dispositions naturelles ;
- un **système d'accompagnement humain** par des conseillers d'orientation certifiés ;
- des **outils de pilotage** (vœux, démarches, agenda, checklist) pour suivre sa candidature jusqu'à l'inscription définitive.

Le projet est porté comme projet final de formation en développement web fullstack, avec l'ambition d'une mise en production réelle sur le marché togolais.

---

## 2. Les fonctionnalités phares

### 2.1 Catalogue établissements & formations

Le cœur de la plateforme. Plus de **200 formations** réparties dans **20 établissements** (publics et privés), organisées par domaine, niveau (BTS → Doctorat) et filière.

Chaque fiche établissement expose :

- Frais de scolarité min/max en FCFA
- Taux de réussite et d'insertion professionnelle
- Équipements, bourses disponibles, résidences universitaires
- Note globale et classement national
- Formations associées avec leurs propres indicateurs de performance

Un **moteur de recommandation** calcule un score qualité par formation (taux de réussite × 25 % + insertion à 12 mois × 30 % + coût inversé × 20 % + importance stratégique × 15 % + salaire de sortie × 10 %).

### 2.2 Tests d'orientation RIASEC

Tests psychométriques interactifs basés sur le modèle Holland (6 profils : Réaliste, Investigateur, Artistique, Social, Entrepreneur, Conventionnel). L'étudiant obtient :

- Son profil dominant et ses scores par dimension
- Des recommandations de filières et métiers alignées avec ses résultats
- Un historique de ses passages de tests

### 2.3 Classements & comparateur

Classement national et régional des établissements sur critères multicritères (qualité d'enseignement, insertion, recherche, infrastructure, vie étudiante, accessibilité financière). Outil de comparaison côte à côte d'établissements ou de formations, et simulateur de coût total d'une formation.

### 2.4 Accompagnement par conseillers

Système complet de mise en relation étudiant–conseiller :

- **Demande d'accompagnement** : l'étudiant envoie une demande à un conseiller spécialisé
- **Chat intégré** pour les échanges pendant le suivi
- **Système de rendez-vous** : proposition, confirmation, formats visio/présentiel/téléphone avec lien de réunion
- **Évaluation du conseiller** à l'issue de la session
- **Ristournes conseillers** : redistribution d'une commission sur les consultations payantes

### 2.5 Tableau de bord personnel

Espace privé de chaque étudiant regroupant :

- **Vœux** : liste de formations souhaitées avec statuts (En attente, Accepté, Refusé)
- **Démarches** : suivi des candidatures (retrait dossier, dépôt, tests, résultats)
- **Favoris** : sauvegardes de formations et établissements
- **Agenda** : rendez-vous et événements personnels
- **Checklist** : tâches à accomplir avant la rentrée
- **Notes personnelles** : prise de notes libre

### 2.6 Événements d'orientation

Calendrier des événements liés à l'orientation : journées portes ouvertes, salons, conférences, webinaires, concours d'entrée, ateliers. Chaque événement propose un système d'inscription avec gestion de capacité et rappels automatiques.

### 2.7 Communauté & forums

Forums thématiques par domaine, par établissement, et par centre d'intérêt (emploi, international, entraide). Les étudiants peuvent créer des discussions, commenter, et s'abonner aux fils qui les intéressent.

### 2.8 AvenBot — Assistant IA

Chatbot conversationnel intégré via WebSocket (Django Channels) pour répondre aux questions des étudiants sur les formations, les procédures et les débouchés en langage naturel.

### 2.9 Notifications

Système de notifications en temps réel couvrant l'ensemble des événements plateforme : nouvelles demandes d'accompagnement, réponses de conseillers, rappels de rendez-vous, réponses du forum, mises à jour de statut de vœux.

---

## 3. Les outils et leurs rôles

### 3.1 Backend

| Outil | Version | Rôle |
|---|---|---|
| **Django** | 5.1.3 | Framework web principal — ORM, vues, templates, admin, migrations |
| **Django REST Framework** | 3.x | API RESTful exposant catalog, orientation, accounts et dashboard |
| **djangorestframework-simplejwt** | — | Authentification JWT pour l'API (tokens access + refresh) |
| **Celery** | — | Tâches asynchrones : envoi d'emails, calcul de recommandations, rappels d'événements |
| **Redis** | — | Broker Celery + cache des sessions |
| **Django Channels** | — | WebSocket pour le chatbot AvenBot en temps réel |
| **drf-spectacular** | — | Documentation Swagger / ReDoc auto-générée de l'API |
| **Pillow** | — | Traitement des images (logos, bannières, avatars) |
| **django-import-export** | — | Import/export CSV et Excel dans l'admin |
| **WhiteNoise** | — | Service des fichiers statiques sans Nginx en développement |

### 3.2 Base de données

| Environnement | SGBD | Raison |
|---|---|---|
| **Production** | PostgreSQL | Robustesse, indexation avancée, JSONField natif, full-text search |
| **Développement / Tests** | SQLite | Zéro configuration, idéal CI/CD |

Tous les modèles utilisent des **UUID** comme clé primaire pour éviter l'exposition d'identifiants incrémentaux et faciliter une future migration distribuée.

### 3.3 Frontend

| Outil | Rôle |
|---|---|
| **Bootstrap 4** | Grille responsive, composants UI de base (modals, dropdowns, alertes) |
| **FontAwesome 5** | Bibliothèque d'icônes vectorielles (navbar, cards, badges) |
| **Palette Golfe Design System** | Système de tokens CSS maison (`design_tokens.css`) — palette Lagune + Safran + Nuit |
| **CSS Variables (custom properties)** | 80+ tokens de couleur, typographie, espacement, ombres, z-index |
| **Vanilla JS** | Interactions légères (toggle menus, fetch API, chatbot WebSocket) |
| **OwlCarousel 2** | Carrousel images (partiellement remplacé par animation CSS) |

### 3.4 Infrastructure & DevOps

| Outil | Rôle |
|---|---|
| **Python 3.13** | Runtime du projet |
| **pip + venv** | Gestion des dépendances |
| **pytest + pytest-django** | Suite de tests (108 tests, couverture models + API + vues) |
| **factory_boy + Faker** | Génération de données de test réalistes |
| **Git** | Versioning du code, branches feature |
| **django-environ** | Gestion des variables d'environnement (`.env`) |

### 3.5 Architecture des 11 apps Django

```
accounts      → Utilisateurs (STUDENT / COUNSELOR / ADMIN), profils, authentification
catalog       → Domaines, Établissements, Formations, Métiers, classements, comparateur
ranking       → Classements nationaux et régionaux des établissements
orientation   → Tests RIASEC, résultats, recommandations, accompagnements, RDV
dashboard     → Vœux, démarches, favoris, agenda, checklist, notes personnelles
events        → Événements d'orientation, inscriptions
community     → Forums, threads, messages, mentorat, messagerie privée
chatbot       → Conversations AvenBot (WebSocket)
notifications → Notifications in-app multi-canal
analytics     → Suivi d'usage et statistiques plateforme
payments      → Consultations payantes conseillers, ristournes
```

---

## 4. Perspectives

### 4.1 Court terme — Déjà réalisé ✓

- **Système de rendez-vous** entre étudiants et conseillers (visio, présentiel, téléphone)
- **Page publique des conseillers** avec profil, spécialités, note et tarif
- **Tableau personnel des rendez-vous** (à venir / passés) avec confirmation / annulation en ligne
- **Forums communautaires** par domaine et par établissement
- **Notifications temps réel** sur l'ensemble des flux
- **Seed Pack** : 20 établissements, 200 formations, 32 métiers, 8 événements, 5 conseillers

### 4.2 Moyen terme — À venir (6-18 mois)

**Module de candidature directe**
Permettre aux étudiants de soumettre leur dossier de candidature directement depuis la plateforme (PDF, relevés de notes, lettres de motivation) et aux établissements de gérer les candidatures reçues.

**Intégration des systèmes d'admission officiels**
Connexion avec les portails d'admission des universités publiques togolaises et, à terme, du MESRS (Ministère de l'Enseignement Supérieur).

**Tableaux de bord établissements**
Espace dédié aux représentants d'établissements pour mettre à jour leurs fiches, gérer leurs formations, publier des événements et consulter les statistiques de visibilité.

**Messagerie privée enrichie**
Système de messagerie directe entre utilisateurs (étudiant–étudiant, étudiant–conseiller) avec pièces jointes et partage de documents.

**Application mobile (PWA)**
Progressive Web App pour rendre la plateforme utilisable offline et installable sur smartphone sans passer par un app store.

### 4.3 Long terme — Vision 3-5 ans

**Machine Learning pour les recommandations**
Remplacement du moteur de score statique par un modèle de recommandation collaboratif (filtrage basé sur les profils RIASEC + historiques de vœux + données d'insertion réelles).

**Sessions vidéo intégrées**
Intégration d'une solution vidéo propriétaire (Jitsi Meet self-hosted ou WebRTC natif) pour les consultations conseiller, en remplacement des liens Zoom externes.

**Expansion géographique**
Déploiement dans les pays voisins (Bénin, Ghana, Côte d'Ivoire) avec adaptation des données (établissements, FCFA vs FCFA CFA vs Cedi, systèmes éducatifs nationaux).

**Partenariats institutionnels**
- Conventions avec les universités pour la mise à jour automatique des données de formation
- Partenariats avec l'ANPE (Agence Nationale pour l'Emploi) pour les données d'insertion
- Intégration des bourses d'État dans le moteur de recherche

**API ouverte**
Ouverture d'une API publique documentée permettant à des tiers (lycées, maisons de jeunes, ONG) de consommer les données d'orientation et de développer leurs propres outils.

---

## 5. Évaluation financière

### 5.1 Modèle économique

AvenSU-Orienta adopte un modèle **freemium** ciblant plusieurs segments :

| Segment | Offre | Prix |
|---|---|---|
| Étudiant standard | Accès gratuit au catalogue, tests RIASEC, forums | Gratuit |
| Étudiant premium | Tests avancés, recommandations personnalisées, suivi illimité | 2 000 – 5 000 FCFA/mois |
| Consultation conseiller | Session 30-60 min avec un conseiller certifié | 10 000 – 25 000 FCFA/session |
| Établissement partenaire | Fiche vérifiée mise en avant, accès aux candidatures | 150 000 – 500 000 FCFA/an |
| Publicité ciblée | Bandeaux sur pages catalogue (non intrusifs) | CPM négocié |

**Commission plateforme** : 15 à 20 % prélevé sur chaque consultation conseiller (modèle ristourne intégré dans le code via `payments.RistourneConseiller`).

---

### 5.2 Estimation des coûts d'infrastructure

| Poste | Fréquence | Coût estimé (FCFA/mois) |
|---|---|---|
| Hébergement VPS (2 vCPU, 4 Go RAM, 80 Go SSD) | Mensuel | 15 000 – 30 000 |
| Base de données PostgreSQL managée | Mensuel | 10 000 – 20 000 |
| Serveur Redis (cache + Celery) | Mensuel | 5 000 – 10 000 |
| CDN + stockage média (S3-compatible) | Mensuel | 5 000 – 15 000 |
| Nom de domaine + SSL | Annuel | ~12 000 (~1 000/mois) |
| Service d'emails transactionnels (Mailgun/Brevo) | Mensuel | 3 000 – 8 000 |
| SMS rappels (facultatif) | À l'usage | 0 – 10 000 |
| **Total infrastructure** | | **39 000 – 94 000 FCFA/mois** |

---

### 5.3 Projection de revenus (scénario modéré — Année 1)

| Source | Hypothèse | Revenu estimé (FCFA/an) |
|---|---|---|
| Abonnements étudiants premium | 200 étudiants × 3 000 FCFA/mois | 7 200 000 |
| Consultations conseillers (commission 15 %) | 50 sessions/mois × 15 000 FCFA × 15 % | 1 350 000 |
| Fiches établissements partenaires | 5 établissements × 250 000 FCFA/an | 1 250 000 |
| Publicité catalogue | CPM faible — démarrage | 500 000 |
| **Total revenus** | | **≈ 10 300 000 FCFA/an** |

---

### 5.4 Point d'équilibre (Break-even)

| Poste | Coût annuel estimé (FCFA) |
|---|---|
| Infrastructure (moyenne) | 800 000 |
| Maintenance technique (développeur 0,5 ETP) | 3 000 000 |
| Marketing digital (réseaux, SEO) | 1 000 000 |
| Frais divers (juridique, bancaire) | 500 000 |
| **Total charges** | **5 300 000** |

Le seuil de rentabilité est atteint dès **~100 abonnements premium actifs** ou **~35 établissements partenaires**, ce qui est réaliste dès la fin de la première année d'exploitation active.

---

### 5.5 Potentiel de montée en charge

| Scénario | Étudiants actifs | Revenus estimés |
|---|---|---|
| Démarrage (an 1) | 500 | 10 M FCFA |
| Croissance (an 2) | 3 000 | 55 M FCFA |
| Maturité (an 3-5) | 15 000+ | 250 M FCFA+ |

À titre de comparaison, le Togo compte environ **80 000 nouveaux bacheliers par an** — capturer 5 % du marché représente déjà un vivier de 4 000 utilisateurs potentiels, sans compter les pays voisins.

---

## 6. Conclusion

AvenSU-Orienta répond à un besoin réel et urgent : donner aux jeunes togolais et ouest-africains les mêmes outils d'orientation que ceux disponibles dans les pays du Nord, adaptés à leur contexte économique, culturel et éducatif.

La plateforme est construite sur une architecture solide (Django 5, API REST, WebSocket, tests automatisés à 108 cas) capable de tenir la charge jusqu'à plusieurs milliers d'utilisateurs simultanés, et conçue pour évoluer en micro-services si la croissance le justifie.

Ce qui distingue AvenSU-Orienta des initiatives existantes, c'est la **combinaison** d'un catalogue de données vérifiées, d'un moteur de recommandation objectif, d'un accompagnement humain structuré et d'outils de suivi de candidature — le tout dans une interface pensée pour le mobile first et accessible sans connexion haut débit.

Le projet n'est pas une expérience de laboratoire. Il est conçu dès le départ pour être mis en production, générer des revenus et devenir un acteur de référence de l'orientation post-bac en Afrique de l'Ouest francophone.

---

*Document rédigé le 3 juillet 2026 — AvenSU-Orienta v1.0*
