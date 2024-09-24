from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Mission, MissionSubmission
from .serializers import MissionSerializer, MissionSubmissionSerializer
from io import StringIO
import sys


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        mission = self.get_object()
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
                return Response(
                    {"is_correct": is_correct}, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"error": "Invalid mission type"}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["post"])
    def submit_code(self, request, pk=None):
        mission = self.get_object()
        if not hasattr(mission, "code_submission"):
            return Response(
                {"error": "This is not a code submission mission."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submitted_code = request.data.get("code")
        if not submitted_code:
            return Response(
                {"error": "No code submitted."}, status=status.HTTP_400_BAD_REQUEST
            )

        is_correct, output = self.execute_and_grade_code(
            mission.code_submission, submitted_code
        )

        submission = MissionSubmission.objects.create(
            user=request.user,
            mission=mission,
            submitted_answer=submitted_code,
            is_correct=is_correct,
        )

        return Response({"is_correct": is_correct, "output": output})

    def execute_and_grade_code(self, code_mission, submitted_code):
        original_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        outputs = []
        all_correct = True

        try:
            exec(submitted_code, globals())

            for test_case in code_mission.test_cases:
                input_data = test_case["input"]
                expected_output = test_case["output"]

                try:
                    actual_output = solution(input_data)

                    if actual_output == expected_output:
                        outputs.append(
                            f"Test case passed: Input: {input_data}, Output: {actual_output}"
                        )
                    else:
                        all_correct = False
                        outputs.append(
                            f"Test case failed: Input: {input_data}, Expected: {expected_output}, Got: {actual_output}"
                        )
                except Exception as e:
                    all_correct = False
                    outputs.append(
                        f"Error in test case: Input: {input_data}, Error: {str(e)}"
                    )

        except Exception as e:
            all_correct = False
            outputs.append(f"Error occurred: {str(e)}")

        finally:
            sys.stdout = original_stdout

        return all_correct, "\n".join(outputs)


class MissionSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MissionSubmission.objects.all()
    serializer_class = MissionSubmissionSerializer
