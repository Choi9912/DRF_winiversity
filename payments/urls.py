from django.urls import path
from .views import PaymentViewSet

urlpatterns = [
    path(
        "",
        PaymentViewSet.as_view({"get": "list", "post": "create"}),
        name="payment-list",
    ),
    path(
        "<int:pk>/", PaymentViewSet.as_view({"get": "retrieve"}), name="payment-detail"
    ),
    path(
        "<int:pk>/refund/",
        PaymentViewSet.as_view({"post": "refund"}),
        name="payment-refund",
    ),
    path(
        "<int:pk>/receipt/",
        PaymentViewSet.as_view({"get": "receipt"}),
        name="payment-receipt",
    ),
    path(
        "payment-history/",
        PaymentViewSet.as_view({"get": "payment_history"}),
        name="payment-payment-history",
    ),
    path(
        "apply-coupon/",
        PaymentViewSet.as_view({"get": "apply_coupon", "post": "apply_coupon"}),
        name="payment-apply-coupon",
    ),
]
