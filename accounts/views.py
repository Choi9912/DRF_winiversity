from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer

from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "accounts/home.html"


# UserViewSet 클래스는 그대로 유지
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "login", "logout", "list_view"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=["get", "post"])
    def register(self, request):
        if request.method == "GET":
            return render(request, "accounts/register.html")
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect("user-list-view")
        return render(request, "accounts/register.html", {"errors": serializer.errors})

    @action(detail=False, methods=["get", "post"])
    def login(self, request):
        if request.method == "GET":
            return render(request, "accounts/login.html")
        username = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            login(request, user)
            return redirect("user-list-view")
        return render(request, "accounts/login.html", {"error": "Invalid credentials"})

    @action(detail=False, methods=["get"])
    def logout(self, request):
        logout(request)
        return redirect("user-list-view")

    @action(detail=False, methods=["get"], url_path="list-view")
    def list_view(self, request):
        users = self.get_queryset()
        return render(request, "accounts/user_list.html", {"users": users})
