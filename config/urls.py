"""
URLs racines du projet AvenSU-Orienta.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Admin sur-mesure
admin.site.site_header = "AvenSU-Orienta — Administration"
admin.site.site_title = "AvenSU Admin"
admin.site.index_title = "Tableau de bord"

# URLs non traduites (API, admin)
urlpatterns = [
    # API REST versionnée
    path("api/v1/", include(("apps.accounts.api.urls", "accounts-api"), namespace="accounts-api")),
    path("api/v1/", include(("apps.catalog.api.urls", "catalog-api"), namespace="catalog-api")),
    path("api/v1/", include(("apps.ranking.api.urls", "ranking-api"), namespace="ranking-api")),
    path("api/v1/", include(("apps.orientation.api.urls", "orientation-api"), namespace="orientation-api")),
    path("api/v1/", include(("apps.dashboard.api.urls", "dashboard-api"), namespace="dashboard-api")),
    path("api/v1/", include(("apps.events.api.urls", "events-api"), namespace="events-api")),
    path("api/v1/", include(("apps.chatbot.api.urls", "chatbot-api"), namespace="chatbot-api")),
    path("api/v1/", include(("apps.notifications.api.urls", "notifications-api"), namespace="notifications-api")),
    path("api/v1/", include(("apps.payments.api.urls", "payments-api"), namespace="payments-api")),

    # Documentation API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Admin
    path("admin/", admin.site.urls),

    # i18n
    path("i18n/", include("django.conf.urls.i18n")),
]

# URLs traduites (front web)
urlpatterns += i18n_patterns(
    path("", include("apps.accounts.urls", namespace="accounts")),
    path("catalogue/", include("apps.catalog.urls", namespace="catalog")),
    path("orientation/", include("apps.orientation.urls", namespace="orientation")),
    path("tableau-de-bord/", include("apps.dashboard.urls", namespace="dashboard")),
    path("evenements/", include("apps.events.urls", namespace="events")),
    path("communaute/", include("apps.community.urls", namespace="community")),
    prefix_default_language=False,
)

# Debug / dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    if "django_browser_reload" in settings.INSTALLED_APPS:
        urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
    if "silk" in settings.INSTALLED_APPS:
        urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
