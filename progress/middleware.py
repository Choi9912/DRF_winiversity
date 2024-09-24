from django.utils.deprecation import MiddlewareMixin
from .models import DailyVisitor, PageView
from django.utils import timezone
from django.conf import settings


class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        
        ip = self.get_client_ip(request)
        today = timezone.now().date()
        user = request.user if request.user.is_authenticated else None

        # 일별 접속자 수 기록
        if not DailyVisitor.objects.filter(date=today, ip_address=ip).exists():
            DailyVisitor.objects.create(date=today, ip_address=ip, user=user)

        # 페이지 조회수 기록
        PageView.objects.create(date=today, ip_address=ip, path=request.path, user=user)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
