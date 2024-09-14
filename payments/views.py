from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        self.request.user.subscription_end_date = timezone.now() + timezone.timedelta(
            days=730
        )
        self.request.user.save()

    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.is_refunded:
            return Response(
                {"detail": "Payment already refunded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (timezone.now() - payment.payment_date).days <= 7 and getattr(
            payment.user, "course_progress", 0
        ) < 10:
            payment.is_refunded = True
            payment.save()
            return Response({"detail": "Payment refunded successfully."})
        else:
            return Response(
                {"detail": "Refund conditions not met."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def receipt(self, request, pk=None):
        payment = self.get_object()
        # Generate receipt logic here
        return Response({"detail": "Receipt generated successfully."})

    def payment_history(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    def apply_coupon(self, request):
        coupon_code = request.data.get("coupon_code")
        # Implement coupon logic here
        return Response({"detail": "Coupon applied successfully."})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.accepted_renderer.format == "html":
            return render(
                request,
                "payments/payment_detail.html",
                {"payment": instance, "user": request.user},
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
