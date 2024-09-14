from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
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
        "history/",
        PaymentViewSet.as_view({"get": "payment_history"}),
        name="payment-history",
    ),
    path(
        "apply-coupon/",
        PaymentViewSet.as_view({"post": "apply_coupon"}),
        name="apply-coupon",
    ),
]
