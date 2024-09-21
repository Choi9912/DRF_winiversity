from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "issue_date", "verification_code")
    list_filter = ("issue_date", "course")
    search_fields = ("user__username", "course__name", "verification_code")
    readonly_fields = ("issue_date", "verification_code")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # 이미 생성된 객체인 경우
            return self.readonly_fields + ("user", "course")
        return self.readonly_fields
