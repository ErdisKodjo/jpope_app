"""
Tests unitaires pour apps.notifications.utils.notify.
"""

import pytest

from apps.accounts.tests.factories import StudentFactory
from apps.notifications.models import Notification, TypeNotification
from apps.notifications.utils import notify


@pytest.mark.django_db
class TestNotify:
    def test_cree_notification(self):
        user = StudentFactory()
        notify(user, "Titre", "Message")
        notif = Notification.objects.get(user=user)
        assert notif.titre == "Titre"
        assert notif.message == "Message"
        assert notif.type_notification == TypeNotification.INFO

    def test_type_personnalise(self):
        user = StudentFactory()
        notify(user, "T", "M", type_notif=TypeNotification.SUCCESS)
        notif = Notification.objects.get(user=user)
        assert notif.type_notification == TypeNotification.SUCCESS

    def test_action_url_enregistree(self):
        user = StudentFactory()
        notify(user, "T", "M", action_url="/dashboard/")
        notif = Notification.objects.get(user=user)
        assert notif.action_url == "/dashboard/"

    def test_retourne_none(self):
        user = StudentFactory()
        assert notify(user, "T", "M") is None

    def test_nechoue_jamais_si_user_invalide(self):
        """notify() avale les exceptions et ne lève rien."""
        assert notify(None, "T", "M") is None
