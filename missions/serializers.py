import json
from rest_framework import serializers
from .models import Mission, MissionSubmission


class MissionSerializer(serializers.ModelSerializer):
    options = serializers.CharField(required=False)

    class Meta:
        model = Mission
        fields = [
            "id",
            "course",
            "question",
            "type",
            "exam_type",
            "options",
            "correct_answer",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["type"] = dict(Mission.MISSION_TYPES).get(
            instance.type, instance.type
        )
        representation["exam_type"] = dict(Mission.EXAM_TYPES).get(
            instance.exam_type, instance.exam_type
        )

        # options를 JSON에서 리스트로 변환
        if instance.options:
            representation["options"] = json.loads(instance.options)
        return representation

    def to_internal_value(self, data):
        # options가 문자열로 들어오면 JSON으로 변환
        if "options" in data and isinstance(data["options"], str):
            try:
                data["options"] = json.dumps(json.loads(data["options"]))
            except json.JSONDecodeError:
                # 유효한 JSON이 아니면 그대로 둡니다.
                pass
        return super().to_internal_value(data)


class MissionSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionSubmission
        fields = ["id", "user", "mission", "submission", "is_correct", "submitted_at"]
