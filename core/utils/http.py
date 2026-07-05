"""
Shared HTTP utilities.

Replaces the duplicated ``get_client_ip`` logic that existed in
``apps.accounts.api.views.LoginView`` and inline in
``apps.payments.api.views.InitierPaiementView``.
"""


def get_client_ip(request):
    """Extract the real client IP from *request*, respecting X-Forwarded-For."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")
