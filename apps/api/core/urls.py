from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.renderers import OpenApiJsonRenderer2
from drf_spectacular.views import SpectacularAPIView
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from core.health import HealthView

SpectacularAPIView.renderer_classes = [
    OpenApiJsonRenderer2,
    *SpectacularAPIView.renderer_classes,
]


class _UnregisteredApiRoute(APIView):
    def initial(self, request, *args, **kwargs):
        raise NotFound()


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("posts/", include(("posts.urls", "posts"), namespace="posts")),
    path("", include(("feed.urls", "feed"), namespace="feed")),
    # API routes must be registered before this catch-all.
    path("api/health", HealthView.as_view()),
    path("api/auth/", include("accounts.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/<path:path>", _UnregisteredApiRoute.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
