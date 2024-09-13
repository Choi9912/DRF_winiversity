# missions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissionViewSet, MissionSubmissionViewSet

router = DefaultRouter()
router.register(r"missions", MissionViewSet)
router.register(r"submissions", MissionSubmissionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
