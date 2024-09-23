from rest_framework import serializers
from .models import UserProgress
from courses.models import Lesson
from courses.serializers import LessonSerializer

class UserProgressSerializer(serializers.ModelSerializer):
    # lesson 필드를 PrimaryKey로 입력받을 수 있도록 함
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    lesson_detail = LessonSerializer(source='lesson', read_only=True)  # 조회 시 상세 정보 제공

    class Meta:
        model = UserProgress
        fields = ['id', 'lesson', 'lesson_detail', 'watched_time', 'last_watched_position', 'completed', 'user']

    def create(self, validated_data):
        # 여기서 lesson_id와 user_id를 저장 처리
        return UserProgress.objects.create(**validated_data)
