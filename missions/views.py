from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.shortcuts import get_object_or_404
from .models import Mission, MissionSubmission
from .serializers import MissionSerializer, MissionSubmissionSerializer


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if request.accepted_renderer.format == "html":
            return Response(
                {"missions": queryset}, template_name="missions/mission_list.html"
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        mission = self.get_object()
        if request.accepted_renderer.format == "html":
            return Response(
                {"mission": mission}, template_name="missions/mission_detail.html"
            )
        serializer = self.get_serializer(mission)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        mission = self.get_object()
        user = request.user

        if mission.type == "multiple_choice":
            selected_option = request.data.get("selected_option")
            if not selected_option:
                return Response(
                    {"error": "Selected option is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            is_correct = int(
                selected_option
            ) == mission.multiple_choice.get_options().index(
                mission.multiple_choice.correct_answer
            )
            submission_data = {
                "user": user.id,
                "mission": mission.id,
                "is_correct": is_correct,
                "multiple_choice": {"selected_option": selected_option},
            }

            serializer = MissionSubmissionSerializer(data=submission_data)
            if serializer.is_valid():
                serializer.save()
                if request.accepted_renderer.format == "html":
                    return Response(
                        {
                            "mission": mission,
                            "submission_result": {"is_correct": is_correct},
                        },
                        template_name="missions/mission_detail.html",
                    )
                return Response(
                    {"is_correct": is_correct}, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"error": "Invalid mission type"}, status=status.HTTP_400_BAD_REQUEST
        )


class MissionSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MissionSubmission.objects.all()
    serializer_class = MissionSubmissionSerializer
