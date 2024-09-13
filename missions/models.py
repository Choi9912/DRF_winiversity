from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Mission(models.Model):
    COURSE_CHOICES = [
        ("math", "수학"),
        ("science", "과학"),
        ("history", "역사"),
        ("literature", "문학"),
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
    # course 만들어지면 foreignkey로 변경할예정
    # course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    type = models.CharField(max_length=20, choices=MISSION_TYPES)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES)
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.CharField(
        max_length=200, blank=True, null=True
    )  # 문자열로 저장
    code_template = models.TextField(
        blank=True, null=True
    )  # 코드 제출형 문제를 위한 필드


class MissionSubmission(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_options = models.JSONField(blank=True, null=True)
    submitted_code = models.TextField(
        blank=True, null=True
    )  # 코드 제출형 문제를 위한 필드
    is_correct = models.BooleanField(default=False)  # 정답 여부를 저장
