# 🎓 AvenSU-Orienta

> Plateforme intelligente d'orientation post-baccalauréat pour l'Afrique de l'Ouest.

## 🚀 Démarrage rapide

### Prérequis
- Docker & Docker Compose
- Make (optionnel)
- Git

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-org/avensu-orienta.git
cd avensu-orienta

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 3. Lancer l'environnement de développement
make dev
# ou : docker-compose up -d --build

# 4. Créer un superutilisateur
make createsuperuser

# 5. Accéder à l'application
# Web : http://localhost:8000
# Admin : http://localhost:8000/admin/
# API Docs : http://localhost:8000/api/docs/
# Flower (Celery) : http://localhost:5555
```

## 📚 Documentation

- **API Swagger** : [AvenSu·Orienta API](http://localhost:8000/api/docs/)
- **API ReDoc** : [AvenSu·Orienta API](http://localhost:8000/api/redoc/)
- **Admin Django** : http://localhost:8000/admin/

## 🧪 Tests

```bash
make test
# ou : docker-compose exec web pytest
```

## 🏗️ Architecture

Voir la section Architecture dans le cahier des charges.

## 📝 Licence

MIT © 2026 AvenSU-Orienta
