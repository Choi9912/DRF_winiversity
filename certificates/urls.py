# certificates/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet

router = DefaultRouter()
router.register(r"", CertificateViewSet, basename="certificate")  # basename 추가

urlpatterns = [
    path("", include(router.urls)),
]
