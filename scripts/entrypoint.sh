#!/bin/sh
set -e

echo "⏳ Attente de PostgreSQL..."
/app/scripts/wait-for-it.sh ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432} --timeout=30 --strict

echo "⏳ Attente de Redis..."
/app/scripts/wait-for-it.sh redis:6379 --timeout=30 --strict

echo "🔄 Application des migrations..."
python manage.py migrate --noinput

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "✅ Démarrage du serveur..."
exec "$@"
