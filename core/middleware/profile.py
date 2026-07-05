from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch


class ProfileCompletionMiddleware:
    """Redirige vers la complétion du profil si incomplet."""

    EXEMPT_PATHS = ["/admin/", "/api/", "/static/", "/media/", "/__reload__/", "/__debug__/", "/silk/"]
    EXEMPT_NAMES = ["accounts:logout", "accounts:profile_edit", "accounts:login", "accounts:register"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not self._is_exempt(request):
            if not self._profile_complete(request.user):
                try:
                    return redirect(reverse("accounts:profile_edit"))
                except NoReverseMatch:
                    pass
        return self.get_response(request)

    def _is_exempt(self, request):
        # Check path prefixes
        for prefix in self.EXEMPT_PATHS:
            if request.path.startswith(prefix):
                return True
        # Check named URLs
        for name in self.EXEMPT_NAMES:
            try:
                url = reverse(name)
                if request.path.startswith(url):
                    return True
            except NoReverseMatch:
                pass
        return False

    def _profile_complete(self, user):
        return getattr(user, "profile_complete", True)
