from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Payment, Coupon
from .serializers import PaymentSerializer, CouponSerializer
from courses.models import Course, CourseProgress


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        course_id = self.request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)
        amount = course.amount
        payment = serializer.save(user=self.request.user, amount=amount, course=course)

        # 코스 결제 후 처리 (예: 사용자에게 코스 접근 권한 부여)
        # 이 부분은 프로젝트의 요구사항에 따라 구현해야 합니다.

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
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
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def apply_coupon(self, request):
        coupon_code = request.data.get("coupon_code")
        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now(),
            )
            discounted_amount = 50000 * (1 - coupon.discount / 100)
            return Response(
                {
                    "discounted_amount": discounted_amount,
                    "detail": "Coupon applied successfully.",
                }
            )
        except Coupon.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired coupon."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def pay_for_course(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.validated_data["course"]
        amount = course.amount

        coupon_code = request.data.get("coupon_code")
        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now(),
                )
                amount *= 1 - coupon.discount / 100
            except Coupon.DoesNotExist:
                return Response(
                    {"error": "Invalid or expired coupon."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        payment = serializer.save(amount=amount, user=request.user)

        # 결제 성공 후 CourseProgress 객체 생성
        CourseProgress.objects.get_or_create(user=request.user, course=course)

        return Response(
            {
                "message": "Payment successful.",
                "payment_id": payment.id,
                "amount": amount,
                "course": course.name,
            },
            status=status.HTTP_201_CREATED,
        )
