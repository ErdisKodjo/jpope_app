from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch


class ProfileCompletionMiddleware:
    """Redirige vers la complétion du profil si incomplet."""

    EXEMPT_PATHS = ["/admin/", "/api/", "/static/", "/media/", "/__reload__/", "/__debug__/", "/silk/", "/ws/", "/i18n/"]

    def __init__(self, get_response):
        self.get_response = get_response
        self._exempt_urls_cache = None

    def __call__(self, request):
        if request.user.is_authenticated and not self._is_exempt(request):
            if not self._profile_complete(request.user):
                try:
                    return redirect(reverse("accounts:profile_edit"))
                except NoReverseMatch:
                    pass
        return self.get_response(request)

    def _get_exempt_urls(self):
        """Calcule et cache les URLs nommées une seule fois."""
        if self._exempt_urls_cache is not None:
            return self._exempt_urls_cache

        urls = []
        for name in ["accounts:logout", "accounts:profile_edit", "accounts:login", "accounts:register"]:
            try:
                urls.append(reverse(name))
            except NoReverseMatch:
                pass
        self._exempt_urls_cache = urls
        return urls

    def _is_exempt(self, request):
        for prefix in self.EXEMPT_PATHS:
            if request.path.startswith(prefix):
                return True
        for url in self._get_exempt_urls():
            if request.path.startswith(url):
                return True
        return False

    def _profile_complete(self, user):
        return getattr(user, "profile_complete", True)