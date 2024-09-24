from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    nickname = models.CharField(max_length=50, blank=True)
    total_study_time = models.IntegerField(default=0)
    subscription_end_date = models.DateTimeField(null=True, blank=True)


class Course(models.Model):
    name = models.CharField(max_length=100)
    # 기타 필요한 필드들...


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    grade = models.CharField(max_length=2, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)