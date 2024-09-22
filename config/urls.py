
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/progress/', include('progress.urls')),
    path('api/missions/', include('missions.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/payments/', include('payments.urls')),

    # JWT 토큰 발급 및 갱신을 위한 URL 추가
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
