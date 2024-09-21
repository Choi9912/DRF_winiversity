from rest_framework import serializers
from .models import Certificate
from courses.models import Course


class CertificateSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)

    class Meta:
        model = Certificate
        fields = "__all__"
        read_only_fields = ["issue_date", "pdf_url", "verification_code", "course_name"]

    def validate_course(self, value):
        if not Course.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid course selected.")
        return value
