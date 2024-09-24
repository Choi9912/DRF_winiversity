from rest_framework import viewsets, permissions
from .models import UserProgress
from .serializers import UserProgressSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Sum
from rest_framework.permissions import IsAdminUser
from courses.models import Course
from payments.models import Payment

class UserProgressViewSet(viewsets.ModelViewSet):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # 관리자는 모든 유저의 progress 조회 가능, 일반 유저는 자신의 것만 조회 가능
        if user.is_staff or user.is_superuser:
            return UserProgress.objects.all().order_by('id')  # 정렬 추가
        return UserProgress.objects.filter(user=user)  # 정렬 추가


    def perform_create(self, serializer):
        user = self.request.user
        lesson = serializer.validated_data.get('lesson')

        # get_or_create 사용하여 중복 방지 및 자동 업데이트
        progress, created = UserProgress.objects.get_or_create(user=user, lesson=lesson)
        serializer.instance = progress
        serializer.save()



    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def admin_dashboard(self, request):
        today = timezone.now()
        last_week = today - timezone.timedelta(days=7)

        # 과목별 평균 진행률
        courses = Course.objects.all()
        course_progress = []
        for course in courses:
            # 쿼리 최적화: select_related 추가
            avg_progress = UserProgress.objects.select_related('lesson').filter(
                lesson__course=course
            ).aggregate(avg_completed=Avg('completed'))['avg_completed'] or 0.0
            average_progress = round(avg_progress * 100, 2)  # 퍼센트로 변환
            course_progress.append({
                'course_name': course.name,
                'average_progress': average_progress
            })

        # 일별 결제 금액
        payments = list(Payment.objects.filter(
            date__range=[last_week, today]
        ).values('date').annotate(total_amount=Sum('amount')))

        data = {
            'course_progress': course_progress,
            'payments': payments,
            # 'visitors': visitors_data,  # 추후 구현 필요
            # 'page_views': page_views_data,  # 추후 구현 필요
        }
        return Response(data)
