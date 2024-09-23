from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField()
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    is_paid = models.BooleanField(default=False)


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    order = models.IntegerField()
    # amount와 is_paid 필드 제거

    def is_available_for_user(self, user):
        try:
            progress = CourseProgress.objects.get(user=user, course=self.course)
            if self.order == 1:  # 첫 번째 레슨은 항상 접근 가능
                return True
            previous_lesson = self.course.lessons.filter(order=self.order - 1).first()
            return (
                previous_lesson
                and progress.completed_lessons.filter(id=previous_lesson.id).exists()
            )
        except CourseProgress.DoesNotExist:
            return self.order == 1  # 진행 상황이 없으면 첫 번째 레슨만 접근 가능


class CourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_lessons = models.ManyToManyField(Lesson, blank=True)

    class Meta:
        unique_together = ("user", "course")
