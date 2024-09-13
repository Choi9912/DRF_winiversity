from rest_framework import serializers
from .models import Mission, MissionSubmission


class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = "__all__"


class MissionSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionSubmission
        fields = "__all__"
        read_only_fields = ["is_correct", "submitted_at"]
