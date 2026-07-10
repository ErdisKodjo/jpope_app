from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RoadmapConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.roadmap"
    verbose_name = _("Roadmap évolutive")
