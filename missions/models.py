from django.db import models
from django.conf import settings
from courses.models import Course


class Mission(models.Model):
    TYPES = (
        ("multiple_choice", "Multiple Choice"),
        ("code_submission", "Code Submission"),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPES)
    question = models.TextField()
    options = models.JSONField(null=True, blank=True)  # For multiple choice questions
    correct_answer = models.TextField()


class MissionSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    submission = models.TextField()
    is_correct = models.BooleanField(null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
