from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Payment, Coupon
from .serializers import PaymentSerializer, CouponSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        amount = self.request.data.get("amount")  # 클라이언트로부터 금액을 받아옴
        payment = serializer.save(user=self.request.user, amount=amount)
        # 구독 기간 설정 로직은 금액에 따라 다르게 적용할 수 있습니다.
        self.request.user.subscription_end_date = timezone.now() + timezone.timedelta(
            days=730
        )
        self.request.user.save()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.accepted_renderer.format == "html":
            return render(request, "payments/payment_list.html", {"payments": queryset})
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.accepted_renderer.format == "html":
            return render(
                request, "payments/payment_detail.html", {"payment": instance}
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.is_refunded:
            return Response(
                {"detail": "Payment already refunded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment.is_refundable:
            payment.is_refunded = True
            payment.save()
            self.request.user.subscription_end_date = None
            self.request.user.save()
            return Response({"detail": "Payment refunded successfully."})
        else:
            return Response(
                {"detail": "Refund conditions not met."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        payment = self.get_object()
        if request.accepted_renderer.format == "html":
            return render(
                request, "payments/payment_receipt.html", {"payment": payment}
            )
        receipt_data = {
            "payment_id": payment.id,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "payment_method": payment.get_payment_method_display(),
        }
        return Response(receipt_data)

    @action(detail=False, methods=["get"])
    def payment_history(self, request):
        payments = Payment.objects.filter(user=request.user)
        if request.accepted_renderer.format == "html":
            return render(
                request, "payments/payment_history.html", {"payments": payments}
            )
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get", "post"])
    def apply_coupon(self, request):
        if request.method == "GET":
            return render(request, "payments/apply_coupon.html")

        coupon_code = request.data.get("coupon_code")
        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now(),
            )
            discounted_amount = 50000 * (1 - coupon.discount / 100)
            if request.accepted_renderer.format == "html":
                return render(
                    request,
                    "payments/coupon_result.html",
                    {"discounted_amount": discounted_amount},
                )
            return Response(
                {
                    "discounted_amount": discounted_amount,
                    "detail": "Coupon applied successfully.",
                }
            )
        except Coupon.DoesNotExist:
            if request.accepted_renderer.format == "html":
                return render(
                    request,
                    "payments/apply_coupon.html",
                    {"error": "Invalid or expired coupon."},
                )
            return Response(
                {"detail": "Invalid or expired coupon."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# 테스트
