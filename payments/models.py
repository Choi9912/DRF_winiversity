from django.db import models
from django.conf import settings
from django.utils import timezone
from courses.models import Course


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("credit_card", "신용카드"),
        ("bank_transfer", "계좌이체"),
        ("easy_payment", "간편결제"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    is_refunded = models.BooleanField(default=False)

    @property
    def is_refundable(self):
        return (timezone.now() - self.payment_date).days <= 7 and getattr(
            self.user, "course_progress", 0
        ) < 10


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
