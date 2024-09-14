from rest_framework import serializers
from .models import (
    Mission,
    MultipleChoiceMission,
    MissionSubmission,
    MultipleChoiceSubmission,
)


class MultipleChoiceMissionSerializer(serializers.ModelSerializer):
    options = serializers.ListField(child=serializers.CharField(), source="get_options")

    class Meta:
        model = MultipleChoiceMission
        fields = ["options", "correct_answer"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

    def create(self, validated_data):
        options = validated_data.pop("options", [])
        instance = super().create(validated_data)
        instance.set_options(options)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        options = validated_data.pop("options", None)
        instance = super().update(instance, validated_data)
        if options is not None:
            instance.set_options(options)
            instance.save()
        return instance


class MissionSerializer(serializers.ModelSerializer):
    multiple_choice = MultipleChoiceMissionSerializer(required=False)

    class Meta:
        model = Mission
        fields = ["id", "course", "question", "type", "exam_type", "multiple_choice"]

    def create(self, validated_data):
        multiple_choice_data = validated_data.pop("multiple_choice", None)
        mission = Mission.objects.create(**validated_data)
        if multiple_choice_data and mission.type == "multiple_choice":
            MultipleChoiceMission.objects.create(
                mission=mission, **multiple_choice_data
            )
        return mission

    def update(self, instance, validated_data):
        multiple_choice_data = validated_data.pop("multiple_choice", None)
        instance = super().update(instance, validated_data)
        if multiple_choice_data and instance.type == "multiple_choice":
            MultipleChoiceMission.objects.update_or_create(
                mission=instance, defaults=multiple_choice_data
            )
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.type == "multiple_choice":
            multiple_choice = instance.multiple_choice
            if multiple_choice:
                representation["multiple_choice"] = MultipleChoiceMissionSerializer(
                    multiple_choice
                ).data
        return representation


class MultipleChoiceSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceSubmission
        fields = ["selected_option"]


class MissionSubmissionSerializer(serializers.ModelSerializer):
    multiple_choice = MultipleChoiceSubmissionSerializer(required=False)

    class Meta:
        model = MissionSubmission
        fields = [
            "id",
            "user",
            "mission",
            "submitted_at",
            "is_correct",
            "multiple_choice",
        ]

    def create(self, validated_data):
        multiple_choice_data = validated_data.pop("multiple_choice", None)
        submission = MissionSubmission.objects.create(**validated_data)
        if multiple_choice_data:
            MultipleChoiceSubmission.objects.create(
                submission=submission, **multiple_choice_data
            )
        return submission
