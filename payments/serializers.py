from rest_framework import serializers

from courses.models import Course
from .models import Payment, Coupon


class PaymentSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "course",
            "amount",
            "payment_method",
            "payment_date",
            "is_refunded",
        ]
        read_only_fields = ["amount", "payment_date", "is_refunded"]

    def validate(self, data):
        if "course" in data:
            data["amount"] = data["course"].amount
        return data


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
