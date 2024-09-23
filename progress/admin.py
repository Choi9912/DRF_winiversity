from django.contrib import admin
from .models import UserProgress, DailyVisitor, PageView

admin.site.register(UserProgress)
admin.site.register(DailyVisitor)
admin.site.register(PageView)
