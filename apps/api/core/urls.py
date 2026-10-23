from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("posts/", include(("posts.urls", "posts"), namespace="posts")),
    path("", include(("feed.urls", "feed"), namespace="feed")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
