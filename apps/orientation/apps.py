from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrientationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orientation"
    verbose_name = _("Orientation")
