# certificates/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet

router = DefaultRouter()
router.register(r"certificates", CertificateViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
