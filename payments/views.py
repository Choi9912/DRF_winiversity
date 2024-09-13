from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
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
        # Here you would implement the actual payment logic
        # For simplicity, we're just setting the subscription end date
        self.request.user.subscription_end_date = timezone.now() + timezone.timedelta(
            days=730
        )  # 2 years
        self.request.user.save()

    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.is_refunded:
            return Response(
                {"detail": "Payment already refunded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check refund conditions
        if (timezone.now() - payment.payment_date).days <= 7:  # Within 1 week
            # Here you would implement the actual refund logic
            payment.is_refunded = True
            payment.save()
            return Response({"detail": "Payment refunded successfully."})
        else:
            return Response(
                {"detail": "Refund period has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
