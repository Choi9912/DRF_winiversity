from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Your Project API",
        default_version="v1",
        description="API documentation for your project",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include([
        path("accounts/", include("accounts.urls")),
        path("courses/", include("courses.urls")),
        path("progress/", include("progress.urls")),
        path("missions/", include("missions.urls")),
        path("certificates/", include("certificates.urls")),
        path("payments/", include("payments.urls")),
    ])),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),



]
