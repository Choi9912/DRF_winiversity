from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import ProtectedError
from .models import Course, Lesson, CourseProgress
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.exceptions import PermissionDenied


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("order")
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]  # 임시로 모든 접근 허용

    @action(detail=True, methods=["get"])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all().order_by("order")
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        lessons_data = data.pop("lessons", [])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        course = serializer.instance

        for lesson_data in lessons_data:
            lesson_data["course"] = course.id
            lesson_serializer = LessonSerializer(data=lesson_data)
            if lesson_serializer.is_valid():
                lesson_serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        try:
            course.delete()
            return Response(
                {"detail": "Course successfully deleted."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except ProtectedError:
            return Response(
                {"detail": "This course cannot be deleted as it has related data."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all().order_by("order")
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        if not lesson.is_available_for_user(request.user):
            raise PermissionDenied("You cannot access this lesson yet.")
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        lesson = self.get_object()
        progress, _ = CourseProgress.objects.get_or_create(
            user=request.user, course=lesson.course
        )
        progress.completed_lessons.add(lesson)
        return Response({"status": "lesson marked as completed"})

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        if not course_id:
            return Response(
                {"error": "course is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        lesson = self.get_object()
        course = lesson.course
        try:
            if Lesson.objects.filter(prerequisite=lesson).exists():
                return Response(
                    {
                        "detail": "This lesson cannot be deleted as it is a prerequisite for other lessons."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            CourseProgress.objects.filter(last_completed_lesson=lesson).update(
                last_completed_lesson=lesson.prerequisite
            )

            lesson.delete()

            remaining_lessons = course.lessons.all().order_by("order")
            for index, remaining_lesson in enumerate(remaining_lessons, start=1):
                remaining_lesson.order = index
                remaining_lesson.save()

            return Response(
                {"detail": "Lesson successfully deleted."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
