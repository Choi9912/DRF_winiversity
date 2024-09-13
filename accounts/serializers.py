from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "nickname",
            "total_study_time",
            "subscription_end_date",
        ]
        read_only_fields = ["total_study_time", "subscription_end_date"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "role",
            "nickname",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "student"),  # 기본값을 'student'로 설정
            nickname=validated_data.get("nickname", ""),
        )
        return user
