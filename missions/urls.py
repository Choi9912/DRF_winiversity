from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissionViewSet, MissionSubmissionViewSet, mission_submit

router = DefaultRouter()
router.register(r"", MissionViewSet, basename="mission")
router.register(r"submissions", MissionSubmissionViewSet)

urlpatterns = [
    path(
        "create/",
        MissionViewSet.as_view({"get": "create_view", "post": "create_view"}),
        name="mission_create",
    ),
    path("<int:mission_id>/submit/", mission_submit, name="mission_submit"),
    path(
        "<int:pk>/", MissionViewSet.as_view({"get": "retrieve"}), name="mission_detail"
    ),
    path("list/", MissionViewSet.as_view({"get": "list"}), name="mission_list"),
    path("", include(router.urls)),
]
