from django.db import models
from django.conf import settings
from courses.models import Lesson
from django.utils import timezone


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    watched_time = models.DurationField(default=timezone.timedelta())
    last_watched_position = models.DurationField(default=timezone.timedelta())
    completed = models.BooleanField(default=False)
