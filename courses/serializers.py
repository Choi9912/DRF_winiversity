from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Lesson
        fields = ["id", "title", "video_url", "order", "course"]
        # "amount"와 "is_paid" 필드 제거


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "name", "description", "order", "amount", "is_paid", "lessons"]
        # Course 모델에는 여전히 "amount"와 "is_paid" 필드가 있으므로 유지
