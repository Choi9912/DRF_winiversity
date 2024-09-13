from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, HomeView

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("", include(router.urls)),
    path(
        "register/",
        UserViewSet.as_view({"get": "register", "post": "register"}),
        name="user-register",
    ),
    path(
        "login/",
        UserViewSet.as_view({"get": "login", "post": "login"}),
        name="user-login",
    ),
    path("logout/", UserViewSet.as_view({"get": "logout"}), name="user-logout"),
    path(
        "users/list-view/",
        UserViewSet.as_view({"get": "list_view"}),
        name="user-list-view",
    ),
]
