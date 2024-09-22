from rest_framework import viewsets, permissions
from .models import UserProgress
from .serializers import UserProgressSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Sum
from rest_framework.permissions import IsAdminUser


class UserProgressViewSet(viewsets.ModelViewSet):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def admin_dashboard(self, request):
        today = timezone.now().date()
        last_week = today - timezone.timedelta(days=7)

        # 일별 접속자 수 및 조회수는 미들웨어나 다른 모델을 통해 수집된다고 가정합니다.

        # 과목별 평균 진행률
        from courses.models import Course
        courses = Course.objects.all()
        course_progress = []
        for course in courses:
            avg_progress = UserProgress.objects.filter(
                lesson__course=course
            ).aggregate(avg=Avg('completed'))['avg'] or 0.0
            course_progress.append({
                'course_name': course.name,
                'average_progress': round(avg_progress * 100, 2)  # 완료 여부를 평균내어 퍼센트로 표시
            })

        # 일별 결제 금액
        from payments.models import Payment
        payments = Payment.objects.filter(
            date__range=[last_week, today]
        ).values('date').annotate(total_amount=Sum('amount'))

        data = {
            'course_progress': course_progress,
            'payments': payments,
            # 'visitors': visitors_data,
            # 'page_views': page_views_data,
        }
        return Response(data)
