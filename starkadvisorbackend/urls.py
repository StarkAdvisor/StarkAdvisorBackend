# starkadvisorbackend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    # OpenAPI / docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    # Apps
    path("api/user_admin/", include("user_admin.urls")),
    path("api/", include("news.urls")),
    path("api/", include("stocks.urls")),
    path("api/", include("chatbot.urls")),
]

# Sólo en desarrollo
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
