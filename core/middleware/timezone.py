import zoneinfo
from django.utils import timezone

class TimezoneMiddleware:
    """Active le fuseau horaire de l'utilisateur."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = None
        if request.user.is_authenticated:
            tzname = getattr(request.user, "timezone", "Africa/Lome")
        if tzname:
            timezone.activate(zoneinfo.ZoneInfo(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)
