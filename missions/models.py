import json
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Mission(models.Model):
    COURSE_CHOICES = [
        ("github", "GitHub"),
        ("html_css", "HTML/CSS"),
        ("js", "JavaScript"),
        ("express", "Express"),
        ("mongodb", "MongoDB"),
        ("aws", "AWS"),
        ("project", "Project"),
    ]

    MISSION_TYPES = (
        ("multiple_choice", "5지선다형"),
        ("code_submission", "코드 제출형"),
    )

    EXAM_TYPES = (
        ("midterm", "중간고사"),
        ("final", "기말고사"),
    )

    course = models.CharField(max_length=20, choices=COURSE_CHOICES)
    question = models.TextField()
    type = models.CharField(max_length=20, choices=MISSION_TYPES)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES)


class MultipleChoiceMission(models.Model):
    mission = models.OneToOneField(
        Mission, on_delete=models.CASCADE, related_name="multiple_choice"
    )
    options = models.TextField()  # JSONField 대신 TextField 사용
    correct_answer = models.CharField(max_length=1)  # A, B, C, D, E 중 하나

    def set_options(self, options):
        self.options = json.dumps(options)

    def get_options(self):
        try:
            return json.loads(self.options)
        except json.JSONDecodeError:
            # JSON 파싱에 실패한 경우, 문자열을 직접 분할
            return [
                opt.strip()
                for opt in self.options.strip("[]").split(",")
                if opt.strip()
            ]


class MissionSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey("Mission", on_delete=models.CASCADE)
    submitted_answer = models.TextField()  # 이 필드를 추가합니다
    is_correct = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s submission for {self.mission.question}"


class MultipleChoiceSubmission(models.Model):
    submission = models.OneToOneField(
        MissionSubmission, on_delete=models.CASCADE, related_name="multiple_choice"
    )
    selected_option = models.CharField(max_length=1)  # A, B, C, D, E 중 하나


class CodeSubmissionMission(models.Model):
    mission = models.OneToOneField(
        Mission, on_delete=models.CASCADE, related_name="code_submission"
    )
    problem_description = models.TextField()
    initial_code = models.TextField()
    test_cases = models.JSONField()  # 입력과 예상 출력을 포함한 테스트 케이스

    def __str__(self):
        return f"Code Submission for {self.mission.question}"
