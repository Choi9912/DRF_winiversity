from django.db import models
from django.conf import settings
from courses.models import Lesson
from django.utils import timezone


class UserProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progresses'
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='user_progresses'
    )
    watched_time = models.DurationField(default=timezone.timedelta())
    last_watched_position = models.DurationField(default=timezone.timedelta())
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {'Completed' if self.completed else 'In Progress'}"


# DailyVisitor와 PageView 모델은 미들웨어에서 사용됩니다.
class DailyVisitor(models.Model):
    date = models.DateField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('date', 'ip_address')

    def __str__(self):
        return f"{self.date} - {self.ip_address}"


class PageView(models.Model):
    date = models.DateField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.date} - {self.path}"
