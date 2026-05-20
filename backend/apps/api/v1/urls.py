"""
API v1 URL patterns.

Router tabanlı URL yapılandırması + JWT auth endpoint'leri.

Auth Endpoint'leri:
    POST /api/v1/auth/register/         → Yeni kullanıcı kaydı
    POST /api/v1/auth/login/            → JWT token al (özel claim'li)
    POST /api/v1/auth/refresh/          → Access token yenile
    POST /api/v1/auth/verify/           → Token geçerlilik doğrula
    POST /api/v1/auth/logout/           → Refresh token blacklist'e al
    GET  /api/v1/auth/me/               → Profil görüntüle
    PATCH /api/v1/auth/me/              → Profil güncelle
    POST /api/v1/auth/change-password/  → Şifre değiştir
    GET  /api/v1/auth/users/            → Kullanıcı listesi (admin)
    GET  /api/v1/auth/users/{id}/       → Kullanıcı detayı (admin)

Legacy Endpoint'ler (geriye uyumluluk için korundu):
    POST /api/v1/token/          → Access + Refresh token al
    POST /api/v1/token/refresh/  → Access token yenile
    POST /api/v1/token/verify/   → Token doğrula

Kaynak Endpoint'leri:
    /api/v1/fields/         → Tarla yönetimi
    /api/v1/sensors/        → Sensör verileri
    /api/v1/soil-analyses/  → Toprak analizleri
    /api/v1/predictions/    → Tahmin sonuçları
    /api/v1/care/           → Bakım tavsiyeleri
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from . import views
from .auth_views import (
    ChangePasswordView,
    CustomLoginView,
    CustomTokenRefreshView,
    LogoutView,
    MeView,
    RegisterView,
    UserDetailView,
    UserListView,
)

# ---------------------------------------------------------------------------
# Router Kayıtları
# ---------------------------------------------------------------------------
router = DefaultRouter()

# Sensör ve toprak analizi
router.register(r'sensors', views.SensorDataViewSet, basename='sensor')
router.register(r'sensors/readings', views.SensorReadingViewSet, basename='sensor-reading')
router.register(r'soil-analyses', views.SensorViewSet, basename='soil-analysis')

# Tarla yönetimi
router.register(r'fields', views.FieldViewSet, basename='field')

# Tahmin ve tavsiyeler
router.register(r'predictions', views.PredictionViewSet, basename='prediction')
router.register(r'care', views.CareRecommendationViewSet, basename='care')

# ---------------------------------------------------------------------------
# ML Custom Endpoint'leri
# ---------------------------------------------------------------------------
ml_urlpatterns = [
    path('fertilizer-optimization/', views.FertilizerOptimizationAPIView.as_view(), name='fertilizer-optimization'),
]

# ---------------------------------------------------------------------------
# Auth URL'leri
# ---------------------------------------------------------------------------
auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomLoginView.as_view(), name='auth_login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='auth_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='auth_verify'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('me/', MeView.as_view(), name='auth_me'),
    path('change-password/', ChangePasswordView.as_view(), name='auth_change_password'),
    # Admin kullanıcı yönetimi
    path('users/', UserListView.as_view(), name='auth_user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='auth_user_detail'),
]

# ---------------------------------------------------------------------------
# URL Patterns
# ---------------------------------------------------------------------------
urlpatterns = [
    # Auth endpoint'leri
    path('auth/', include(auth_urlpatterns)),

    # Legacy JWT Token endpoint'leri (geriye uyumluluk)
    # POST /api/v1/token/          → Access + Refresh token al
    # POST /api/v1/token/refresh/  → Access token yenile
    # POST /api/v1/token/verify/   → Token doğrula
    path('token/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Router URL'leri (tüm ViewSet'ler)
    path('', include(router.urls)),

    # Custom ML Endpoint'leri
    path('', include(ml_urlpatterns)),
]
