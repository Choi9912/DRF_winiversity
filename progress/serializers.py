from rest_framework import serializers
from .models import UserProgress
from courses.models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'video_url', 'order']

from rest_framework import serializers
from .models import UserProgress

class UserProgressSerializer(serializers.ModelSerializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())  # lesson 필드 수정

    class Meta:
        model = UserProgress
        fields = '__all__'
