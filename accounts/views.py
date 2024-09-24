from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .models import User, Enrollment
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    EnrollmentSerializer,
)
from django.utils import timezone
from datetime import timedelta
import logging
from courses.models import Course
from courses.serializers import CourseSerializer

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "login", "logout", "list", "register"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                user.subscription_end_date = timezone.now() + timedelta(days=730)  # 2년
                user.save()
                login(request, user)
                return Response(
                    UserSerializer(user).data, status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"Error during user registration: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred during registration."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        logger.warning(f"Invalid registration data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=["post"])
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def profile(self, request):
        user = request.user
        enrollments = Enrollment.objects.filter(user=user)
        courses = Course.objects.filter(enrollment__user=user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "enrollments": EnrollmentSerializer(enrollments, many=True).data,
                "courses": CourseSerializer(courses, many=True).data,
            }
        )

    @action(detail=True, methods=["post"])
    def update_profile(self, request, pk=None):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def download_certificate(self, request, pk=None):
        user = self.get_object()
        course_id = request.query_params.get("course_id")
        enrollment = Enrollment.objects.filter(
            user=user, course_id=course_id, completed=True
        ).first()
        if enrollment:
            # 여기에 수료증 생성 로직 구현
            return Response(
                {"message": "Certificate generated", "download_url": "URL_TO_DOWNLOAD"}
            )
        return Response(
            {"error": "No completed course found"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["get"])
    def admin_dashboard(self, request):
        if request.user.role != "admin":
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        # 관리자 대시보드 데이터 준비
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        return Response(
            {
                "total_users": total_users,
                "total_courses": total_courses,
                "total_enrollments": total_enrollments,
                # 필요한 추가 통계 데이터
            }
        )


@action(detail=False, methods=["get"])
def home(self, request):
    courses = Course.objects.all().order_by("-order")
    logger.debug(f"Number of courses: {courses.count()}")
    for course in courses:
        logger.debug(f"Course: {course.name}, Order: {course.order}")
    return Response(CourseSerializer(courses, many=True).data)
