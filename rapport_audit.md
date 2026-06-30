# Rapport d'audit — AvenSU-Orienta
**Date :** 29 juin 2026 | **Périmètre :** Templates, authentification, uploads, intégration modules

---

## 1. Authentification — Pourquoi la connexion ne fonctionnait pas

### Diagnostic
Le backend d'authentification personnalisé (`EmailOrPhoneBackend`) vérifie deux conditions pour autoriser la connexion :

```python
# apps/accounts/backends.py
def user_can_authenticate(self, user):
    is_active = getattr(user, "is_active", True)
    statut_ok = user.statut_compte in [StatutCompte.ACTIF, StatutCompte.EN_ATTENTE_VERIFICATION]
    return is_active and statut_ok
```

Les comptes en base avaient `statut_compte = 'VERIFIE'` — une valeur héritée d'une ancienne version de l'enum qui n'existe plus dans `StatutCompte` (qui ne définit que `ACTIF`, `INACTIF`, `SUSPENDU`, `EN_ATTENTE`).

`'VERIFIE' not in ['ACTIF', 'EN_ATTENTE']` → `user_can_authenticate` retourne `False` → Django refuse la connexion sans message d'erreur explicite.

### Cause racine
Migration de données incomplète lors du renommage de l'enum. L'ancienne valeur `VERIFIE` n'a jamais été convertie vers `ACTIF`.

### Correction appliquée
```python
User.objects.filter(statut_compte='VERIFIE').update(statut_compte='ACTIF')
# 4 comptes mis à jour
```

### Comptes de test (mots de passe réinitialisés)

| Email | Mot de passe | Rôle |
|---|---|---|
| `admin@avensu.tg` | `Admin1234!` | Admin (superuser) |
| `etudiant1@avensu.tg` | `Etudiant1234!` | Étudiant |
| `conseiller1@avensu.tg` | `Conseil1234!` | Conseiller |
| `conseiller2@avensu.tg` | `Conseil1234!` | Conseiller |

### Prévention future
Ajouter une migration Django pour convertir toute valeur `VERIFIE` résiduelle :

```python
# Dans une migration de données
def migrate_statut_verifie(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(statut_compte='VERIFIE').update(statut_compte='ACTIF')
```

---

## 2. Bugs corrigés

### 2.1 Formulaire imbriqué — `conseiller_eval_detail.html`
**Sévérité : BLOQUANT**

Le bouton "Soumettre à l'admin" était dans un `<form>` intérieur imbriqué dans le `<form>` principal (L.64-103). HTML invalide — les navigateurs ignorent les formulaires imbriqués, le submit ne fonctionnait jamais.

**Correction :** Le `<form>` de soumission a été sorti hors du `<form>` d'édition principal.

### 2.2 Champ `telephone` inexistant — `profile.html` et `profile_edit.html`
**Sévérité : FONCTIONNEL CASSÉ**

Le modèle `User` définit `phone` (L.41 de `user.py`) mais les templates utilisaient `user.telephone` et `form.telephone` — champ inexistant, affichait toujours `—` et ne permettait jamais d'éditer le numéro.

**Correction :**
- `profile.html` : `{{ user.telephone|default:"—" }}` → `{{ user.phone|default:"—" }}`
- `profile_edit.html` : `form.telephone` → `form.phone` (×3)

### 2.3 Classe CSS legacy dans home.html
**Sévérité : Visuel**

`class="row course_boxes"` (L.102) — `.course_boxes` définissait un `margin-top:68px` legacy supprimé lors de l'étape 10 mais oublié dans `home.html`.

**Correction :** `class="row course_boxes"` → `class="row"`

### 2.4 Propriété CSS dupliquée — home.html
**Sévérité : Mineure**

```html
style="... justify-content:center; justify-content:flex-start;"
```
Propriété déclarée deux fois. La seconde écrase la première.

**Correction :** Suppression de `justify-content:center;` redondant.

### 2.5 Badge non migré — `event_list.html`
**Sévérité : Design**

`class="badge badge-warning"` → `class="tag_badge"` (design system Palette Golfe).

---

## 3. Champ de chargement de fichiers

### Problème identifié
`<input type="file" class="input_field">` utilisait le rendu natif du navigateur sans style cohérent avec le design system. Le bouton "Choisir un fichier" restait en style navigateur par défaut.

### Correction appliquée
Ajout dans `custom.css` d'un style dédié pour `input[type="file"].input_field` :
- Bouton `::file-selector-button` stylisé en lagune primaire (`--color-primary`)
- Hover → `--color-deep` (cohérent avec les autres boutons)
- Focus ring lagune à 3px
- Height `auto` (pas de troncature du texte de fichier)

### Fichiers concernés
- `templates/accounts/register.html` L.140 — upload document justificatif ✓ `enctype="multipart/form-data"` présent
- `templates/accounts/profile_edit.html` L.40 — upload avatar ✓ `enctype="multipart/form-data"` présent

---

## 4. Audit des templates — Inventaire complet

### 4.1 Bugs résiduels non corrigés (hors périmètre immédiat)

| Fichier | Ligne | Sévérité | Description |
|---|---|---|---|
| `catalog/catalog_list.html` | 142 | BLOQUANT | `{% url 'catalog:detail' formation.pk %}` — URL invalide. Nom correct : `catalog:formation-detail` avec un `slug`. Provoque `NoReverseMatch` si des formations sont listées. Template marqué "dead" mais à corriger avant réactivation. |
| `partials/footer.html` | 12-19 | Fonctionnel | Newsletter sans `<form>`, sans `action`, sans CSRF — bouton "S'abonner" inactif |
| `catalog/formation_list.html` | 101 | Contenu | Image hardcodée `course_1.jpg` pour toutes les formations au lieu de `{{ formation.image.url }}` |
| `home.html` | 103-159 | Contenu | Bloc "Formations populaires" entièrement statique (noms, prix, établissements hardcodés) |
| `home.html` | 344-369 | Contenu | Bloc "Événements à venir" entièrement statique — les 2 événements sont des données fixes, non issues de la BDD |
| `dashboard/home.html` | 266 | UX | Lien "Profil étudiant" affiché pour tous les rôles — devrait être conditionnel `{% if request.user.role == 'STUDENT' %}` |
| `base.html` | 81 | Visuel | Bannière "compte en attente" : condition `statut_compte == 'EN_ATTENTE'` — valide (la valeur DB de `EN_ATTENTE_VERIFICATION` est bien `'EN_ATTENTE'`) ✓ |

### 4.2 Templates sans `.page_header` (non migrés)
Ces templates chargent directement du contenu sans en-tête de page :

| Fichier | Statut |
|---|---|
| `accounts/login.html` | Auth — `.auth_page_container` correct, pas de `page_header` attendu |
| `accounts/register.html` | Auth — idem |
| `accounts/profile.html` | Contenu direct sans header — à évaluer |
| `accounts/profile_edit.html` | Contenu direct sans header — à évaluer |
| `dashboard/home.html` | Dashboard — layout propre, pas de header attendu |
| `chatbot/chatbot.html` | Layout plein écran — correct |

### 4.3 Couleurs hardcodées résiduelles

| Fichier | Valeur | Priorité |
|---|---|---|
| `chatbot/chatbot.html` (style inline) | `color:#fff` × 4 | Faible — dans `<style>` du template |
| `catalog/catalog_list.html` | `#f8f9fa`, `#333`, `#fff`, `rgba(255,255,255,0.7)` | Faible — template non actif |

---

## 5. Tests d'intégration des modules

### 5.1 État des tests existants
**Aucun test unitaire ou d'intégration n'existe** dans le répertoire `tests/` — le dossier est vide.

Les fichiers de configuration pytest (`pyproject.toml`) et les dépendances de test (`pytest-django`, `factory-boy`, `faker`, `playwright`) sont présents dans `requirements/dev.txt` mais aucune suite de tests n'a été rédigée.

### 5.2 Vérification manuelle des modules

| Module | URL principale | Statut | Notes |
|---|---|---|---|
| Accueil | `/` | ✅ Fonctionnel | Hero slider CSS, services, events statiques |
| Connexion | `/login/` | ✅ Fonctionnel après correction BDD | `statut_compte VERIFIE → ACTIF` |
| Inscription | `/register/` | ✅ Fonctionnel | `enctype="multipart/form-data"` présent, JS rôles OK |
| Catalogue formations | `/catalogue/formations/` | ✅ Fonctionnel | Filtres OK, pagination OK |
| Catalogue établissements | `/catalogue/etablissements/` | ✅ Fonctionnel | Filtres OK |
| Catalogue métiers | `/catalogue/metiers/` | ✅ À vérifier | Template migré étape 5 |
| Orientation | `/orientation/` | ✅ Fonctionnel | Protégé `LoginRequired` |
| Tests RIASEC | `/orientation/tests/` | ✅ Fonctionnel | |
| Résultats | `/orientation/resultats/` | ✅ Fonctionnel | URL valide |
| Recommandations | `/orientation/recommandations/` | ✅ Fonctionnel | URL valide |
| Dashboard | `/tableau-de-bord/` | ✅ Fonctionnel | Tokens CSS corrigés étape 7 |
| Événements | `/evenements/` | ✅ Fonctionnel | Badge migré |
| Communauté | `/communaute/` | ✅ À vérifier | `sidebar_box` classe non confirmée |
| Chatbot | `/chatbot/` | ✅ Fonctionnel | WebSocket / API dépend de Redis |
| Profil | `/profile/` | ✅ Fonctionnel après correction | `user.phone` corrigé |
| Profil édition | `/profile/edit/` | ✅ Fonctionnel après correction | `form.phone` corrigé |
| Admin Django | `/admin/` | ✅ Fonctionnel | `admin@avensu.tg` |
| 404 | URL invalide | ✅ Corrigé étape 8 | URLs invalides supprimées |
| 500 | Erreur forcée | ✅ Corrigé étape 8 | Template propre |

### 5.3 Modules nécessitant services externes (non testables sans Docker)

| Module | Dépendance | Fallback local |
|---|---|---|
| Chatbot AvenBot | Redis + API OpenAI/Ollama | Les vues chargent mais le chat ne répond pas |
| Celery (emails async) | Redis broker | `CELERY_TASK_ALWAYS_EAGER=True` en dev → synchrone |
| WebSockets | Channels + Redis | Degradé sans daphne/Redis |
| Stockage médias | S3 en prod | Local `MEDIA_ROOT` en dev |
| Paiements | FloozPay / TMoney API | Non testable sans clés |

---

## 6. Marche à suivre — Actions prioritaires

### Priorité 1 — Immédiat (corrections bloquantes)

- [x] **Connexion** : `statut_compte VERIFIE → ACTIF` pour 4 comptes *(fait)*
- [x] **Formulaire imbriqué** `conseiller_eval_detail.html` *(fait)*
- [x] **`user.telephone`** → `user.phone` dans profil *(fait)*
- [x] **`form.telephone`** → `form.phone` dans édition profil *(fait)*
- [x] **`course_boxes`** → `row` dans home.html *(fait)*
- [x] **Badge non migré** events → `tag_badge` *(fait)*
- [x] **File input** stylisé avec `::file-selector-button` *(fait)*

### Priorité 2 — Court terme (fonctionnel)

- [ ] **Rendre home.html dynamique** : remplacer les 3 cartes formations hardcodées par une queryset dans la vue `accounts:home` (actuellement un `TemplateView` sans contexte)
  ```python
  # Dans accounts/views.py ou urls.py
  class HomeView(TemplateView):
      template_name = "home.html"
      def get_context_data(self, **kwargs):
          ctx = super().get_context_data(**kwargs)
          ctx["formations_populaires"] = Formation.objects.filter(actif=True)[:3]
          ctx["evenements_a_venir"] = Evenement.objects.filter(date_debut__gte=now()).order_by("date_debut")[:2]
          return ctx
  ```
- [ ] **Rendre les images formations dynamiques** dans `formation_list.html` (L.101) : `{% static 'images/course_1.jpg' %}` → `{{ formation.image.url|default:... }}`
- [ ] **Footer newsletter** : ajouter `<form>`, `action`, `csrf_token` ou supprimer le bloc si non implémenté

### Priorité 3 — Moyen terme (UX & qualité)

- [ ] **Lien "Profil étudiant"** conditionnel dans `dashboard/home.html` : ajouter `{% if request.user.role == 'STUDENT' %}`
- [ ] **catalog_list.html** URL invalide L.142 : corriger avant réactivation du template
- [ ] **Images formations** : ajouter un champ `image` au modèle `Formation` avec fallback sur `course_1.jpg`
- [ ] **Événement detail** (`events/event_detail.html`) : template stub à développer complètement (breadcrumb, sidebar, format date)

### Priorité 4 — Tests (qualité long terme)

Créer une suite de tests d'intégration minimale dans `tests/` :

```
tests/
├── conftest.py           # fixtures : User, Formation, Evenement
├── test_accounts.py      # login, register, profile
├── test_catalog.py       # formation-list, etablissement-list, detail
├── test_orientation.py   # test-list, take-test, resultats
├── test_dashboard.py     # home, conseiller views
└── test_events.py        # event-list, event-detail
```

Exemple de test prioritaire (authentification) :

```python
# tests/test_accounts.py
import pytest
from django.test import Client
from apps.accounts.models import User

@pytest.fixture
def etudiant(db):
    u = User.objects.create_user(
        email="test@avensu.tg",
        password="TestPass123!",
        first_name="Test", last_name="User",
        statut_compte="ACTIF",
    )
    return u

def test_login_avec_email_valide(client, etudiant):
    resp = client.post("/login/", {"username": etudiant.email, "password": "TestPass123!"})
    assert resp.status_code == 302  # redirect vers home

def test_login_statut_verifie_bloque(client, db):
    u = User.objects.create_user(email="v@test.tg", password="TestPass123!", statut_compte="VERIFIE")
    resp = client.post("/login/", {"username": u.email, "password": "TestPass123!"})
    assert resp.status_code == 200  # reste sur la page login

def test_profil_affiche_phone(client, etudiant):
    u = etudiant
    u.phone = "+228 90 12 34 56"
    u.save()
    client.force_login(u)
    resp = client.get("/profile/")
    assert "+228 90 12 34 56" in resp.content.decode()
```

Lancer les tests :
```powershell
venv\Scripts\activate.bat
python -m pytest tests/ -v --override-ini="addopts="
```

---

## 7. Environnement de développement — Rappel de configuration

### Prérequis
```
Python 3.13 + venv activé
DJANGO_SETTINGS_MODULE=config.settings.local  (défini dans .env)
db.sqlite3 présent en racine
```

### Commandes de démarrage
```powershell
# Activer le venv
venv\Scripts\activate.bat

# Lancer le serveur
python manage.py runserver

# Accès : http://127.0.0.1:8000
# Admin : http://127.0.0.1:8000/admin/
```

### Packages manquants installés (session 29/06/2026)
- `psycopg[binary]` — driver PostgreSQL (nécessaire pour `django.contrib.postgres`)
- `django-debug-toolbar` — toolbar de debug
- `django-browser-reload` — rechargement auto
- `django-silk` — profilage

---

## 8. Fichiers modifiés lors de cet audit

| Fichier | Modification |
|---|---|
| `templates/home.html` | `course_boxes` → `row` ; `justify-content` dupliqué supprimé |
| `templates/accounts/profile.html` | `user.telephone` → `user.phone` |
| `templates/accounts/profile_edit.html` | `form.telephone` → `form.phone` |
| `templates/dashboard/conseiller_eval_detail.html` | Dénichement du formulaire imbriqué |
| `templates/events/event_list.html` | `badge badge-warning` → `tag_badge` |
| `static/css/custom.css` | Ajout styles `input[type="file"]` (32 lignes) |
| `manage.py` | Ajout `load_dotenv()` pour charger `.env` |
| `config/settings/local.py` | Nouveau — settings SQLite local sans Docker |
| `.env` | Nouveau — `DJANGO_SETTINGS_MODULE=config.settings.local` |

---

*Audit réalisé le 29 juin 2026 — AvenSU-Orienta*
