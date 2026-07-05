"""
Shared view mixins used across multiple apps.

``PostOnlyMixin``
    Replaces the repeated ``def get(): return HttpResponseNotAllowed(["POST"])``
    pattern found in many ``View`` subclasses across orientation and dashboard.
"""
from django.http import HttpResponseNotAllowed


class PostOnlyMixin:
    """Mixin that rejects GET requests with 405 Method Not Allowed.

    Apply to ``View`` subclasses that only accept POST.  The mixin
    provides a default ``get`` implementation so each view no longer
    needs its own boilerplate.
    """

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])
