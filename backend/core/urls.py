from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


class BrandedSwaggerView(SpectacularSwaggerView):
    template_name = "learning/swagger_ui_custom.html"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("learning.urls")),

    # OpenAPI Schema & Interactive Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", BrandedSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
