from django.db import models
from django.conf import settings
from courses.models import Course
from django.utils import timezone
import uuid  # UUID를 생성하기 위해 필요합니다.

class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    pdf_url = models.URLField(blank=True)
    verification_code = models.CharField(max_length=100, null=True, blank=True)

    def is_expired(self):
        # 예: 발행일로부터 1년 후 만료
        return timezone.now() > (self.issue_date + timezone.timedelta(days=365))

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = str(uuid.uuid4())
        super().save(*args, **kwargs)
