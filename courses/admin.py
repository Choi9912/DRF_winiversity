from django.contrib import admin
from .models import Course, Lesson, CourseProgress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "amount", "is_paid")
    list_filter = ("is_paid",)
    search_fields = ("name", "description")
    ordering = ("order",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__name")
    ordering = ("course", "order")


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "completed_lessons_count")
    list_filter = ("course",)
    search_fields = ("user__username", "course__name")

    def completed_lessons_count(self, obj):
        return obj.completed_lessons.count()

    completed_lessons_count.short_description = "Completed Lessons"
