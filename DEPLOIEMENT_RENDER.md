# Déploiement AvenSU-Orienta sur Render

> **Prérequis** : compte Render (render.com), dépôt GitHub/GitLab connecté.

---

## Vue d'ensemble des services à créer

| Service Render | Type | Rôle |
|---|---|---|
| **avensu-web** | Web Service | Serveur ASGI (Daphne) — HTTP + WebSocket |
| **avensu-celery** | Background Worker | Tâches asynchrones (emails, notifs…) |
| **avensu-beat** | Background Worker | Tâches planifiées (Celery Beat) |
| **avensu-db** | PostgreSQL | Base de données principale |
| **avensu-redis** | Redis | Cache, broker Celery, Channel Layer WS |

---

## Étape 1 — Préparer le dépôt

Les fichiers suivants ont été créés/modifiés pour Render :

```
requirements.txt   ← dépendances production (daphne, channels-redis, sentry…)
build.sh           ← pip install + collectstatic + migrate
config/settings/prod.py  ← SECURE_PROXY_SSL_HEADER ajouté
```

Committer et pousser sur GitHub :

```bash
git add requirements.txt build.sh config/settings/prod.py
git commit -m "chore: add Render deployment files"
git push origin main
```

---

## Étape 2 — Créer la base PostgreSQL

1. Dashboard Render → **New → PostgreSQL**
2. Nom : `avensu-db` | Region : `Frankfurt (EU Central)` (le plus proche de Lomé)
3. Plan : **Free** (90 jours) ou **Starter** ($7/mois) pour la prod
4. **Create Database**
5. Copier la **Internal Database URL** (format `postgresql://user:pass@host/db`) → tu en auras besoin à l'étape 4

---

## Étape 3 — Créer le Redis

1. Dashboard Render → **New → Redis**
2. Nom : `avensu-redis` | Region : même que la DB
3. Plan : **Free** ou **Starter**
4. **Create Redis**
5. Copier l'**Internal Redis URL** (format `redis://red-xxx:6379`) → tu en auras besoin à l'étape 4

---

## Étape 4 — Créer le Web Service

1. Dashboard Render → **New → Web Service**
2. Connecter ton dépôt GitHub → choisir la branche `main`
3. Remplir le formulaire :

| Champ | Valeur |
|---|---|
| **Name** | `avensu-web` |
| **Region** | Frankfurt |
| **Branch** | `main` |
| **Runtime** | Python 3 |
| **Build Command** | `./build.sh` |
| **Start Command** | `daphne -b 0.0.0.0 -p $PORT config.asgi:application` |

4. Cliquer **Advanced** → **Add Environment Variables** et saisir toutes les variables (voir tableau ci-dessous)
5. **Create Web Service**

### Variables d'environnement requises

| Clé | Valeur / Description |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
| `DJANGO_SECRET_KEY` | Clé aléatoire 50+ caractères — [générer ici](https://djecrety.ir/) |
| `DJANGO_ALLOWED_HOSTS` | `avensu-web.onrender.com` (+ ton domaine custom si tu en as un) |
| `DATABASE_URL` | *(non utilisé directement — voir variables Postgres ci-dessous)* |
| `POSTGRES_DB` | Nom de la DB (depuis Internal URL) |
| `POSTGRES_USER` | Utilisateur Postgres |
| `POSTGRES_PASSWORD` | Mot de passe Postgres |
| `POSTGRES_HOST` | Hôte interne Render (ex : `dpg-xxx.frankfurt-postgres.render.com`) |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_SSLMODE` | `require` |
| `REDIS_URL` | Internal Redis URL (ex : `redis://red-xxx:6379/0`) |
| `CELERY_BROKER_URL` | Même URL Redis avec `/1` (ex : `redis://red-xxx:6379/1`) |
| `CORS_ALLOWED_ORIGINS` | `https://avensu-web.onrender.com` |
| `DEFAULT_FROM_EMAIL` | `noreply@avensu-orienta.tg` |
| `EMAIL_HOST` | Hôte SMTP (ex : `smtp.gmail.com`) |
| `EMAIL_PORT` | `587` |
| `EMAIL_HOST_USER` | Adresse email |
| `EMAIL_HOST_PASSWORD` | Mot de passe app email |
| `AWS_ACCESS_KEY_ID` | Clé S3/MinIO pour les médias *(optionnel au départ)* |
| `AWS_SECRET_ACCESS_KEY` | Secret S3/MinIO *(optionnel au départ)* |
| `AWS_BUCKET_NAME` | Nom du bucket S3 *(optionnel au départ)* |
| `SENTRY_DSN` | DSN Sentry *(optionnel)* |
| `ANTHROPIC_API_KEY` | Clé API Anthropic pour le chatbot |

> **Astuce — décomposer l'Internal Database URL** :
> Format : `postgresql://USER:PASSWORD@HOST/DB_NAME`
> Extraire manuellement USER, PASSWORD, HOST, DB_NAME pour les 5 variables Postgres.

---

## Étape 5 — Créer le Celery Worker

1. Dashboard Render → **New → Background Worker**
2. Même dépôt, même branche
3. Remplir :

| Champ | Valeur |
|---|---|
| **Name** | `avensu-celery` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `celery -A config.celery worker --loglevel=info --concurrency=2` |

4. Ajouter **les mêmes variables d'environnement** que le Web Service
5. **Create Background Worker**

---

## Étape 6 — Créer le Celery Beat

1. Dashboard Render → **New → Background Worker**
2. Même dépôt, même branche
3. Remplir :

| Champ | Valeur |
|---|---|
| **Name** | `avensu-beat` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `celery -A config.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler` |

4. Mêmes variables d'environnement
5. **Create Background Worker**

> ⚠️ Ne lancer qu'**une seule** instance de Beat (pas de réplication) pour éviter les tâches en double.

---

## Étape 7 — Premier déploiement

Render déclenche automatiquement le build après la création.
Suivre les logs dans l'onglet **Logs** du service `avensu-web`.

Le `build.sh` exécute dans l'ordre :
1. `pip install -r requirements.txt`
2. `python manage.py collectstatic --no-input`
3. `python manage.py migrate --no-input`

Si tout va bien, le service passe en statut **Live** 🟢.

---

## Étape 8 — Créer un superutilisateur

Dans l'onglet **Shell** du service `avensu-web` (ou via un one-off job) :

```bash
python manage.py createsuperuser
```

---

## Étape 9 — Charger les données initiales (optionnel)

```bash
# Dans le Shell Render du service web :
python manage.py seed_pack --skip-images
```

> Les images médias nécessitent S3. Sans S3 configuré, utiliser `--skip-images`.

---

## Étape 10 — Domaine personnalisé (optionnel)

1. Service `avensu-web` → **Settings → Custom Domains**
2. Ajouter `avensu-orienta.tg` (ou ton domaine)
3. Configurer l'entrée CNAME chez ton registrar vers `avensu-web.onrender.com`
4. Render provisionnera le certificat SSL automatiquement (Let's Encrypt)
5. Mettre à jour `DJANGO_ALLOWED_HOSTS` : `avensu-orienta.tg,www.avensu-orienta.tg`

---

## Résolution des problèmes fréquents

### `DisallowedHost` au premier accès
Ajouter le domaine Render dans `DJANGO_ALLOWED_HOSTS` :
```
avensu-web.onrender.com
```

### Boucle de redirections HTTPS
Déjà corrigé : `SECURE_PROXY_SSL_HEADER` ajouté dans `prod.py`.

### WebSocket ne se connecte pas
Vérifier que le Start Command utilise bien **daphne** (et non gunicorn).
`daphne` supporte nativement HTTP + WebSocket.

### `channels_redis` introuvable
Déjà ajouté dans `requirements.txt`. Si l'erreur persiste, forcer un redéploiement.

### Médias (images) non affichés
Sans S3, les fichiers `media/` ne persistent pas entre redéploiements (disque éphémère sur Render Free).
→ Configurer un bucket S3 (AWS, Backblaze B2, ou Cloudflare R2) et renseigner les variables `AWS_*`.

### `ModuleNotFoundError: No module named 'modeltranslation'` en migration
S'assurer que les migrations de `modeltranslation` ont été générées localement avant de pousser :
```bash
python manage.py makemigrations
git add apps/*/migrations/
git commit -m "chore: add missing migrations"
```

---

## Architecture finale sur Render

```
Internet
   │ HTTPS
   ▼
Render Load Balancer (SSL terminé ici)
   │ HTTP + X-Forwarded-Proto: https
   ▼
avensu-web (Daphne ASGI)
   ├── HTTP → Django views / DRF
   └── WebSocket → Django Channels → channels-redis → Redis
         │
         ├── avensu-db (PostgreSQL)
         ├── avensu-redis (Cache + Broker + Channel Layer)
         ├── avensu-celery (worker)
         └── avensu-beat (scheduler)
```
