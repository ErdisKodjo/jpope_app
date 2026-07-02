# AvenSU-Orienta — Architecture pour la montée en charge

> Ce document décrit l'évolution progressive de l'architecture de la plateforme
> pour absorber des pics de trafic et passer de quelques centaines à des dizaines
> de milliers d'utilisateurs simultanés.

---

## 1. Architecture actuelle (Phase 0 — Monolithe)

```
Navigateur
    │
    ▼
┌─────────────────────────────────────┐
│        Serveur unique (VPS)         │
│                                     │
│  Gunicorn (4 workers)               │
│     └── Django 5.1 (WSGI)          │
│                                     │
│  Django Channels (ASGI / WS)        │
│                                     │
│  Celery Worker                      │
│  Celery Beat                        │
│                                     │
│  Redis (cache + broker Celery)      │
│  SQLite → PostgreSQL local          │
│  WhiteNoise (fichiers statiques)    │
└─────────────────────────────────────┘
```

**Limite** : un seul point de défaillance, scaling vertical uniquement (plus
de RAM/CPU sur la même machine), pas de résilience.

**Seuil avant saturation** : ~200–500 utilisateurs simultanés selon le VPS.

---

## 2. Phase 1 — Séparation des couches (500–5 000 utilisateurs)

La première étape consiste à séparer ce qui est stateless (l'app) de ce qui
est stateful (base de données, cache, files de tâches).

```
                        ┌──────────────────┐
Navigateurs  ──────────►│   Nginx (proxy)  │
                        │  + SSL termination│
                        │  + rate limiting  │
                        └────────┬─────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Gunicorn / Uvicorn    │
                    │   Django (WSGI + ASGI)  │
                    │   2–4 instances         │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────▼──────┐  ┌────────▼──────┐  ┌───────▼──────┐
     │  PostgreSQL   │  │  Redis        │  │  Celery      │
     │  (dédié)      │  │  (dédié)      │  │  Workers (2) │
     └───────────────┘  └───────────────┘  └──────────────┘
```

### Actions concrètes

**Nginx comme reverse proxy**
```nginx
upstream django_app {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    keepalive 32;
}

server {
    listen 80;
    server_name avensu.tg;

    # Fichiers statiques servis directement par Nginx (pas Django)
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    # WebSocket AvenBot
    location /ws/ {
        proxy_pass http://django_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**PostgreSQL dédié**
```python
# config/settings/production.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),      # IP du serveur DB dédié
        "PORT": "5432",
        "CONN_MAX_AGE": 60,          # connexions persistantes
        "OPTIONS": {"sslmode": "require"},
    }
}
```

**Cache Redis pour Django**
```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "TIMEOUT": 300,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Sessions en Redis (pas en DB)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

**Mise en cache des vues catalogue** (lectures fréquentes, données stables)
```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 15), name="dispatch")  # 15 min
class FormationListView(ListView):
    ...

@method_decorator(cache_page(60 * 60), name="dispatch")  # 1 h
class ClassementView(View):
    ...
```

---

## 3. Phase 2 — Réplication et load balancing (5 000–30 000 utilisateurs)

```
Internet
    │
    ▼
┌──────────────────────────────┐
│   Load Balancer (HAProxy     │
│   ou AWS ALB / Nginx stream) │
└──────┬───────────────┬───────┘
       │               │
┌──────▼──────┐ ┌──────▼──────┐
│  App Node 1 │ │  App Node 2 │   ← scaling horizontal
│  Gunicorn   │ │  Gunicorn   │     (ajouter des nœuds)
└──────┬──────┘ └──────┬──────┘
       └───────┬────────┘
               │
    ┌──────────▼──────────┐
    │   PostgreSQL        │
    │   Primary (write)   │
    │                     │
    │   ┌─────────────┐   │
    │   │  Replica 1  │   │  ← lectures lourdes (rapports,
    │   │  (read-only)│   │    classements, recherche)
    │   └─────────────┘   │
    └─────────────────────┘

    ┌─────────────────────┐
    │   Redis Cluster     │
    │   (3 nœuds)         │  ← haute disponibilité cache + broker
    └─────────────────────┘

    ┌─────────────────────┐
    │   Celery Workers    │
    │   (pool de 4–8)     │
    └─────────────────────┘
```

### Routage lecture/écriture dans Django

```python
# core/db_router.py
class ReadWriteRouter:
    READ_ONLY_APPS = {"catalog", "ranking"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.READ_ONLY_APPS:
            return "replica"
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, **hints):
        return db == "default"

# config/settings/production.py
DATABASES = {
    "default": { ... },   # PostgreSQL Primary
    "replica": {          # PostgreSQL Replica (read-only)
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("DB_REPLICA_HOST"),
        ...
        "TEST": {"MIRROR": "default"},
    },
}
DATABASE_ROUTERS = ["core.db_router.ReadWriteRouter"]
```

### Connection pooling avec PgBouncer

Chaque nœud Django ouvre de nombreuses connexions PostgreSQL. PgBouncer
les mutualise pour éviter de saturer le serveur DB.

```
App Nodes ──► PgBouncer (port 5432) ──► PostgreSQL Primary
               pool_size = 20
               max_client_conn = 200
```

---

## 4. Phase 3 — Conteneurisation Docker + Orchestration (30 000+ utilisateurs)

```
                     ┌─────────────────────────────┐
                     │   Kubernetes Cluster         │
                     │                             │
                     │  ┌──────────────────────┐   │
                     │  │  Ingress Controller  │   │ ← Nginx ou Traefik
                     │  │  + Cert-Manager TLS  │   │
                     │  └──────────┬───────────┘   │
                     │             │               │
                     │  ┌──────────▼───────────┐   │
                     │  │  Django Deployment   │   │
                     │  │  replicas: 3–10      │   │ ← auto-scaling HPA
                     │  │  (Gunicorn + ASGI)   │   │
                     │  └──────────────────────┘   │
                     │                             │
                     │  ┌──────────────────────┐   │
                     │  │  Celery Deployment   │   │
                     │  │  replicas: 2–5       │   │
                     │  └──────────────────────┘   │
                     │                             │
                     │  ┌──────────────────────┐   │
                     │  │  Celery Beat (1)     │   │
                     │  └──────────────────────┘   │
                     └──────────────┬──────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
   ┌──────────▼────────┐  ┌─────────▼────────┐  ┌────────▼────────┐
   │  PostgreSQL        │  │   Redis Cluster  │  │   CDN (Cloudflare│
   │  (RDS / Cloud SQL) │  │   (ElastiCache)  │  │   / BunnyCDN)    │
   └───────────────────┘  └──────────────────┘  └─────────────────┘
```

### docker-compose.prod.yml (simplifié)

```yaml
version: "3.9"

services:
  web:
    build: .
    command: gunicorn config.asgi:application -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
    depends_on:
      - db
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "1"
          memory: 512M

  celery:
    build: .
    command: celery -A config worker -l info -c 4
    deploy:
      replicas: 2

  celery-beat:
    build: .
    command: celery -A config beat -l info
    deploy:
      replicas: 1   # UN SEUL beat scheduler

  nginx:
    image: nginx:alpine
    volumes:
      - ./docker/nginx/prod.conf:/etc/nginx/conf.d/default.conf
      - staticfiles:/app/staticfiles
    ports:
      - "80:80"
      - "443:443"

  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  pgdata:
  staticfiles:
```

### Horizontal Pod Autoscaler (Kubernetes)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: django-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: django
  minReplicas: 2
  maxReplicas: 12
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65      # scale-out si CPU > 65%
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 75
```

---

## 5. Stratégie de cache multi-niveaux

```
Requête utilisateur
        │
        ▼
┌───────────────────┐
│  CDN (edge cache) │  ← pages publiques statiques (home, liste formations)
│  TTL: 5–60 min    │    sans authentification → servi depuis 30+ PoP
└───────┬───────────┘
        │ (cache miss)
        ▼
┌───────────────────┐
│  Nginx (proxy     │  ← micro-cache 30s pour les listes (absorbe les bursts)
│  cache 30s)       │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  Django + Redis   │  ← vues cachées (15 min), sessions, résultats RIASEC
│  (cache views)    │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  PostgreSQL       │  ← source de vérité, touché le moins possible
│  + PgBouncer      │
└───────────────────┘
```

### Ce qu'il faut cacher en priorité

| Données | TTL | Justification |
|---|---|---|
| Liste formations / établissements | 15 min | Lecture seule, peu de mises à jour |
| Classements nationaux | 1 h | Calcul lourd, mise à jour quotidienne |
| Stats globales (domaine_list) | 30 min | Agrégats coûteux |
| Résultats RIASEC de l'utilisateur | 24 h | Immuables après calcul |
| Pages d'accueil (visiteurs) | 5 min | Trafic entrant massif |

### Invalidation du cache

```python
# apps/catalog/signals.py
from django.db.models.signals import post_save
from django.core.cache import cache

def invalidate_formation_cache(sender, instance, **kwargs):
    cache.delete_pattern("views.decorators.cache.cache_page.*formation*")
    cache.delete("stats_globales")

post_save.connect(invalidate_formation_cache, sender=Formation)
```

---

## 6. Gestion des WebSockets (AvenBot) à grande échelle

Django Channels utilise un **Channel Layer Redis** pour distribuer les messages
entre plusieurs instances de l'application.

```python
# config/settings/production.py
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (env("REDIS_HOST_1"), 6379),
                (env("REDIS_HOST_2"), 6379),  # Redis Cluster
            ],
            "capacity": 1500,
            "expiry": 10,
        },
    }
}
```

Ainsi, un message envoyé à AvenBot connecté au nœud 1 peut être reçu par le
consumer tournant sur le nœud 2 — la connexion WebSocket n'est plus liée à
une instance particulière.

---

## 7. Files de tâches Celery — priorisation

Différentes queues pour éviter que les tâches lentes bloquent les critiques.

```python
# config/celery.py
CELERY_TASK_ROUTES = {
    "apps.notifications.tasks.send_email":       {"queue": "high"},
    "apps.notifications.tasks.send_push":        {"queue": "high"},
    "apps.analytics.tasks.record_event":         {"queue": "low"},
    "apps.ranking.tasks.recalculate_rankings":   {"queue": "low"},
    "apps.chatbot.tasks.process_message":        {"queue": "default"},
}

CELERY_TASK_QUEUES = {
    "high":    {"exchange": "high",    "routing_key": "high"},
    "default": {"exchange": "default", "routing_key": "default"},
    "low":     {"exchange": "low",     "routing_key": "low"},
}
```

```bash
# Démarrer 3 workers spécialisés
celery -A config worker -Q high    -c 4 --loglevel=info &
celery -A config worker -Q default -c 2 --loglevel=info &
celery -A config worker -Q low     -c 1 --loglevel=info &
```

---

## 8. CDN pour les fichiers statiques et médias

Les images, CSS et JS servis par WhiteNoise sont corrects en phase 0. Dès la
phase 1, les confier à un CDN réduit la charge sur les serveurs applicatifs
et améliore la latence depuis n'importe quelle ville d'Afrique.

```
static/images/logo.png
        │
        ▼
  Upload sur S3 / Cloudflare R2 / MinIO
        │
        ▼
  CDN PoP le plus proche de l'utilisateur
  (Lagos, Abidjan, Dakar, Accra)
        │
        ▼
  Réponse en ~20ms au lieu de ~200ms
```

```python
# config/settings/production.py
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE  = "storages.backends.s3boto3.S3StaticStorage"

AWS_STORAGE_BUCKET_NAME = env("AWS_BUCKET")
AWS_S3_CUSTOM_DOMAIN    = env("CDN_DOMAIN")   # cdn.avensu.tg
AWS_S3_FILE_OVERWRITE   = False
AWS_DEFAULT_ACL         = "public-read"
```

---

## 9. Observabilité — Surveiller avant de subir

```
Django app
    │
    ├── Sentry (erreurs 500, exceptions, tracebacks)
    │
    ├── Prometheus + Grafana
    │       ├── Temps de réponse par endpoint (P50 / P95 / P99)
    │       ├── Nombre de workers Celery actifs
    │       ├── Taux de hit/miss du cache Redis
    │       └── Connexions PostgreSQL actives
    │
    └── Loki (agrégation des logs Django + Nginx + Celery)
```

```python
# Middleware de métriques
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    ...
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]
```

**Alertes à configurer dès le départ**

| Métrique | Seuil d'alerte |
|---|---|
| Temps de réponse P95 | > 800ms |
| Taux d'erreur 5xx | > 1% |
| CPU application | > 80% pendant 5 min |
| Connexions DB actives | > 80% du pool |
| File Celery `high` | > 500 tâches en attente |

---

## 10. Feuille de route — Quand passer à la phase suivante ?

| Seuil observé | Action |
|---|---|
| Temps de réponse P95 > 500ms | Activer le cache Redis sur les vues lourdes |
| CPU > 70% en continu | Ajouter un nœud applicatif (phase 1 → 2) |
| DB connexions saturées (>90%) | Ajouter PgBouncer + réplica lecture |
| Déploiements causent des coupures | Passer à Docker + rolling updates |
| Pics imprédictibles de trafic | Kubernetes + HPA |
| Latence media > 300ms | Activer CDN |

---

## Résumé — Stack cible en production haute disponibilité

```
┌─────────────────────────────────────────────────────────┐
│                    Utilisateurs                         │
└─────────────────────────────┬───────────────────────────┘
                              │ HTTPS
                              ▼
                    ┌─────────────────┐
                    │  Cloudflare CDN │  ← DDoS protection + Edge cache
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Load Balancer  │  ← HAProxy / AWS ALB
                    └──┬──────────┬──┘
                       │          │
              ┌────────▼──┐  ┌────▼────────┐
              │  App #1   │  │  App #2..N  │  ← Auto-scaling
              │  Django   │  │  Django     │
              └────┬──────┘  └──────┬──────┘
                   └────────┬───────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
 ┌────────▼───────┐ ┌───────▼──────┐ ┌───────▼───────┐
 │  PostgreSQL    │ │  Redis       │ │  Celery Pool  │
 │  Primary       │ │  Cluster     │ │  + Beat       │
 │  + Replica(s)  │ │  (cache +    │ │               │
 │  + PgBouncer   │ │   broker +   │ │               │
 └────────────────┘ │   channels)  │ └───────────────┘
                    └──────────────┘

          ┌─────────────────────────────────┐
          │  Observabilité                  │
          │  Sentry + Prometheus + Grafana  │
          └─────────────────────────────────┘
```
