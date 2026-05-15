"""
API v1 URL patterns.

Router tabanlı URL yapılandırması + JWT token endpoint'leri.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r'sensors', views.SensorViewSet, basename='sensor')
router.register(r'fields', views.FieldViewSet, basename='field')
router.register(r'predictions', views.PredictionViewSet, basename='prediction')
router.register(r'care', views.CareRecommendationViewSet, basename='care')

urlpatterns = [
    # JWT Token endpoint'leri
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Router URL'leri
    path('', include(router.urls)),
]
