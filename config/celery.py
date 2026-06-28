import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("avensu_orienta")

# Charger la config depuis Django settings, namespace CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-découverte des tâches dans toutes les apps installées
app.autodiscover_tasks()

# Tâches périodiques (beat)
app.conf.beat_schedule = {
    "recalculer-classements-annuels": {
        "task": "apps.ranking.tasks.recalculer_classements",
        "schedule": crontab(day_of_month=1, month_of_year=1, hour=3, minute=0),
    },
    "envoyer-rappels-evenements": {
        "task": "apps.notifications.tasks.envoyer_rappels_j_1",
        "schedule": crontab(hour=8, minute=0),
    },
    "nettoyer-sessions-expirees": {
        "task": "apps.accounts.tasks.nettoyer_sessions",
        "schedule": crontab(hour=4, minute=0),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
