from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Enrollment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'total_study_time', 'subscription_end_date', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'nickname', 'total_study_time', 'subscription_end_date')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'nickname')}),
    )

admin.site.register(User, CustomUserAdmin)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed', 'grade', 'completion_date')
    list_filter = ('completed', 'grade')
    search_fields = ('user__username', 'course__name')