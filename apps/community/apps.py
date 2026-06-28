"""
Configuration de l'app community.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommunityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.community"
    verbose_name = _("Communauté")

    def ready(self):
        pass  # Import signals here if needed
