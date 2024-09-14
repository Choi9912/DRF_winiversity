from django.db import models
from django.conf import settings
from django.utils import timezone


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    is_refunded = models.BooleanField(default=False)

    @property
    def is_refundable(self):
        return (timezone.now() - self.payment_date).days <= 7 and getattr(
            self.user, "course_progress", 0
        ) < 10
