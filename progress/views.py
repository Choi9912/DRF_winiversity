from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import UserProgress
from .serializers import UserProgressSerializer


class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserProgress.objects.none()  # 기본 빈 쿼리셋 추가

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return UserProgress.objects.filter(user=self.request.user)
        return UserProgress.objects.none()
