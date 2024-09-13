import json
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, permissions, status
from django.shortcuts import render, get_object_or_404, redirect
from .models import Mission, MissionSubmission
from .serializers import MissionSerializer, MissionSubmissionSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
import logging
import subprocess

logger = logging.getLogger(__name__)


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def list(self, request, *args, **kwargs):
        missions = self.get_queryset()
        if request.accepted_renderer.format == "html":
            return Response(
                {"missions": missions}, template_name="missions/mission_list.html"
            )
        serializer = self.get_serializer(missions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def list_view(self, request):
        return self.list(request)

    def retrieve(self, request, *args, **kwargs):
        mission = self.get_object()
        options = json.loads(mission.options) if mission.options else []
        if request.accepted_renderer.format == "html":
            return Response(
                {"mission": mission, "options": options},
                template_name="missions/mission_detail.html",
            )
        serializer = self.get_serializer(mission)
        return Response(serializer.data)

    @action(detail=False, methods=["get", "post"])
    def create_view(self, request):
        if request.method == "POST":
            data = request.data.copy()
            logger.debug(f"Received data: {data}")  # 로깅 추가

            # options 처리
            if "options" in data:
                options = json.loads(data["options"])
                data["options"] = json.dumps(options)
            logger.debug(f"Processed data: {data}")  # 로깅 추가

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                if request.accepted_renderer.format == "html":
                    return redirect("mission_list")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # 유효성 검사 실패 시 에러 메시지 표시
                course_choices = dict(Mission.COURSE_CHOICES)
                mission_types = dict(Mission.MISSION_TYPES)
                exam_types = dict(Mission.EXAM_TYPES)

                return Response(
                    {
                        "serializer": serializer,
                        "mission_types": mission_types,
                        "exam_types": exam_types,
                        "course_choices": course_choices,  # 여기에도 추가
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                    template_name="missions/mission_create.html",
                )
        else:
            serializer = self.get_serializer()

        course_choices = dict(Mission.COURSE_CHOICES)
        mission_types = dict(Mission.MISSION_TYPES)
        exam_types = dict(Mission.EXAM_TYPES)
        return Response(
            {
                "serializer": serializer,
                "mission_types": mission_types,
                "exam_types": exam_types,
                "course_choices": course_choices,
            },
            template_name="missions/mission_create.html",
        )


class MissionSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MissionSubmission.objects.all()
    serializer_class = MissionSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        mission = serializer.validated_data["mission"]
        submission = serializer.validated_data["submission"]

        if mission.type == "multiple_choice":
            is_correct = submission == mission.correct_answer
        else:  # code_submission
            is_correct = self.evaluate_code(submission, mission.correct_answer)

        serializer.save(user=self.request.user, is_correct=is_correct)

    def evaluate_code(self, submitted_code, expected_output):
        # 실제 코드 실행 및 평가 로직을 구현해야 합니다.
        return False  # 임시로 False 반환


from django.contrib.auth.decorators import login_required


@login_required
def mission_submit(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    if request.method == "POST":
        if mission.type == "multiple_choice":
            selected_options = request.POST.getlist("options")
            # 선택된 옵션을 JSON 형식으로 저장
            submission = MissionSubmission.objects.create(
                mission=mission,
                user=request.user,  # User 필드 설정
                selected_options=selected_options,
            )

            # 정답 확인 로직
            correct_answer = (
                mission.correct_answer.split(",") if mission.correct_answer else []
            )
            is_correct = selected_options == correct_answer
            submission.is_correct = is_correct
            submission.save()

            return JsonResponse({"is_correct": is_correct})

        elif mission.type == "code_submission":
            submitted_code = request.POST.get("submitted_code")
            # 코드 제출형 문제 처리 로직
            submission = MissionSubmission.objects.create(
                mission=mission,
                user=request.user,  # User 필드 설정
                submitted_code=submitted_code,
            )

            # 코드 실행 및 정답 확인 로직 (예시)
            try:
                result = subprocess.run(
                    ["node", "-e", submitted_code],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                output = result.stdout.strip()
                is_correct = output == mission.correct_answer
            except subprocess.TimeoutExpired:
                is_correct = False

            submission.is_correct = is_correct
            submission.save()

            return JsonResponse({"is_correct": is_correct})
    return HttpResponse("Invalid request method", status=405)
