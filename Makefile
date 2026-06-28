.PHONY: help install dev build up down logs test lint migrate shell

help:  ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Installe les dépendances
	pip install -r requirements/dev.txt
	pre-commit install

dev:  ## Lance l'environnement de dev
	docker-compose up -d --build

build:  ## Rebuild les images
	docker-compose build --no-cache

up:  ## Démarre les services
	docker-compose up -d

down:  ## Arrête les services
	docker-compose down

logs:  ## Affiche les logs
	docker-compose logs -f web celery

test:  ## Lance les tests
	docker-compose exec web pytest

lint:  ## Vérifie le code
	black apps/ core/
	isort apps/ core/
	flake8 apps/ core/
	mypy apps/ core/

migrate:  ## Applique les migrations
	docker-compose exec web python manage.py migrate

makemigrations:  ## Génère les migrations
	docker-compose exec web python manage.py makemigrations

shell:  ## Ouvre un shell Django
	docker-compose exec web python manage.py shell_plus

createsuperuser:  ## Crée un superutilisateur
	docker-compose exec web python manage.py createsuperuser

collectstatic:  ## Collecte les fichiers statiques
	docker-compose exec web python manage.py collectstatic --noinput

db-reset:  ## Réinitialise la base de données
	docker-compose down -v
	docker-compose up -d db redis
	sleep 5
	docker-compose up -d web
