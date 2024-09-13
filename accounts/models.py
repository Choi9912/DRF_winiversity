from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLES = (
        ("student", "Student"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=10, choices=ROLES, default="student")
    nickname = models.CharField(max_length=50, blank=True)
    total_study_time = models.DurationField(default=timezone.timedelta())
    subscription_end_date = models.DateTimeField(null=True, blank=True)
