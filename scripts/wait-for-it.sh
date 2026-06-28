#!/bin/sh
# Script simplifié pour attendre qu'un service soit disponible
HOST=$1; shift
PORT=$(echo $HOST | cut -d: -f2)
HOST=$(echo $HOST | cut -d: -f1)
TIMEOUT=30

while ! nc -z $HOST $PORT 2>/dev/null; do
    TIMEOUT=$((TIMEOUT-1))
    if [ $TIMEOUT -le 0 ]; then
        echo "❌ Timeout en attendant $HOST:$PORT"
        exit 1
    fi
    sleep 1
done
echo "✅ $HOST:$PORT disponible"
