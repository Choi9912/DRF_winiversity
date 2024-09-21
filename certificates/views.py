from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Certificate
from .serializers import CertificateSerializer
from courses.models import Course
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import uuid
from django.utils import timezone  # 이 줄을 추가하세요


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        verification_code = uuid.uuid4().hex
        serializer.save(user=self.request.user, verification_code=verification_code)

    @action(detail=True, methods=["get"])
    def download_pdf(self, request, pk=None):
        certificate = self.get_object()
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # PDF 생성 로직
        p.drawString(100, 750, f"Certificate of Completion")
        p.drawString(100, 700, f"This is to certify that")
        p.drawString(100, 650, f"{certificate.user.get_full_name()}")
        p.drawString(100, 600, f"has successfully completed the course")
        p.drawString(100, 550, f"{certificate.course.name}")
        p.drawString(
            100, 500, f"Issue Date: {certificate.issue_date.strftime('%Y-%m-%d')}"
        )
        p.drawString(100, 450, f"Verification Code: {certificate.verification_code}")

        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename=f"certificate_{certificate.id}.pdf"
        )

    @action(detail=False, methods=["get"])
    def verify(self, request):
        code = request.query_params.get("code", None)
        if code:
            try:
                certificate = Certificate.objects.get(verification_code=code)
                return Response(
                    {
                        "valid": True,
                        "user": certificate.user.get_full_name(),
                        "course": certificate.course.name,  # 'title'을 'name'으로 변경
                        "issue_date": certificate.issue_date,
                    }
                )
            except Certificate.DoesNotExist:
                pass
        return Response({"valid": False}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        # 예: 30일 이내 만료 예정인 수료증
        soon = timezone.now() + timezone.timedelta(days=30)
        certificates = self.get_queryset().filter(
            issue_date__lte=soon - timezone.timedelta(days=365)
        )
        serializer = self.get_serializer(certificates, many=True)
        return Response(serializer.data)
