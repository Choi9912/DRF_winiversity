from django.contrib import admin
from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "order")
    list_filter = ("order",)
    search_fields = ("name", "description")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "video_url", "order")
    list_filter = ("course", "order")
    search_fields = ("title", "course__name")
