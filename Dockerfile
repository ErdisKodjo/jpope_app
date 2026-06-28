# ──────────── Stage de base ────────────
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ──────────── Dépendances Python ────────────
FROM base AS python-deps

COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# ──────────── Image finale ────────────
FROM base AS production

COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

COPY . /app/

RUN chmod +x /app/scripts/entrypoint.sh /app/scripts/wait-for-it.sh \
    && addgroup --system django && adduser --system --group django --home /app \
    && chown -R django:django /app

USER django

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120"]
