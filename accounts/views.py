from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import User, Enrollment, Course
from .serializers import UserSerializer, UserRegistrationSerializer
from django.utils import timezone
from datetime import timedelta
from django.views.generic import TemplateView
import logging
from rest_framework.exceptions import PermissionDenied


logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "accounts/home.html"


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'login', 'logout', 'register']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                user.subscription_end_date = timezone.now() + timedelta(days=730)  # 2년
                user.save()
                login(request, user)
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error during user registration: {str(e)}")
                return Response({'error': 'An unexpected error occurred during registration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning(f"Invalid registration data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                return Response(UserSerializer(user).data)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('home'))

    @action(detail=False, methods=['get'])
    def profile(self, request):
        user = request.user
        enrollments = Enrollment.objects.filter(user=user)
        courses = Course.objects.filter(enrollment__user=user)
        context = {
            'user': UserSerializer(user).data,
            'enrollments': [enrollment.id for enrollment in enrollments],
            'courses': [course.id for course in courses],
        }
        return Response(context)

    @action(detail=True, methods=['patch'])
    def update_profile(self, request, pk=None):
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to update this profile.")
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to deactivate this account.")
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def download_certificate(self, request, pk=None):
        user = self.get_object()
        course_id = request.query_params.get('course_id')
        try:
            enrollment = Enrollment.objects.get(user=user, course_id=course_id, completed=True)
            # 여기에 수료증 생성 및 다운로드 로직 구현
            return Response({'message': 'Certificate downloaded'})
        except Enrollment.DoesNotExist:
            return Response({'error': 'No completed course found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def admin_dashboard(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("You don't have permission to access the admin dashboard.")
        # 관리자 대시보드 데이터 준비
        dashboard_data = {
            'total_users': User.objects.count(),
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.count(),
        }
        return Response(dashboard_data)