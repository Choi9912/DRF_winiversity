from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissionViewSet, MissionSubmissionViewSet

router = DefaultRouter()
router.register(r"api/missions", MissionViewSet)
router.register(r"api/submissions", MissionSubmissionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("missions/", MissionViewSet.as_view({"get": "list"}), name="mission-list"),
    path(
        "missions/<int:pk>/",
        MissionViewSet.as_view({"get": "retrieve"}),
        name="mission-detail",
    ),
    path(
        "missions/<int:pk>/submit/",
        MissionViewSet.as_view({"post": "submit"}),
        name="mission-submit",
    ),
    # API 엔드포인트는 위의 router에 의해 자동으로 생성됩니다.
]
