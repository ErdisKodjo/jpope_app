from django.conf import settings
from django.db import models


class Counselor(models.Model):
    """Simple counselor model used for dashboard service tests.
    It links to the user representing the counselor.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboard_counselor"
    )

    def __str__(self):
        return f"Counselor {self.user_id}"
