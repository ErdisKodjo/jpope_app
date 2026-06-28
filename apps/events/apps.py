"""
Configuration de l'app events.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.events"
    verbose_name = _("Événements")

    def ready(self):
        pass  # Import signals here if needed
