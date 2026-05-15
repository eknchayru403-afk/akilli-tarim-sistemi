"""
API v1 ViewSet'ler.

Field, SoilAnalysis ve CropRecommendation için CRUD endpoint'leri.
JWT tabanlı kimlik doğrulama ile korunur.
"""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.analysis.models import CareRecommendation, CropRecommendation, SoilAnalysis
from apps.fields.models import Field

from .filters import CropRecommendationFilter, FieldFilter, SoilAnalysisFilter
from .pagination import StandardPagination
from .permissions import IsOwner
from .serializers import (
    CareRecommendationSerializer,
    CropRecommendationSerializer,
    FieldCreateUpdateSerializer,
    FieldSerializer,
    SoilAnalysisCreateSerializer,
    SoilAnalysisSerializer,
)

logger = logging.getLogger(__name__)


class FieldViewSet(viewsets.ModelViewSet):
    """
    Tarla API endpoint'i — CRUD desteği.

    GET    /api/v1/fields/          → Tarla listesi (filtreli, sayfalı)
    POST   /api/v1/fields/          → Yeni tarla oluştur
    GET    /api/v1/fields/{id}/     → Tarla detayı
    PUT    /api/v1/fields/{id}/     → Tarla güncelle
    DELETE /api/v1/fields/{id}/     → Tarla sil
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FieldFilter
    search_fields = ['name', 'location', 'current_crop']
    ordering_fields = ['created_at', 'area_decar', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return FieldCreateUpdateSerializer
        return FieldSerializer

    def get_queryset(self):
        """Sadece kullanıcının kendi tarlalarını döndürür."""
        return Field.objects.filter(
            user=self.request.user,
        ).select_related('user')

    def perform_create(self, serializer):
        """Tarla oluşturulurken user'ı otomatik ata."""
        serializer.save(user=self.request.user)
        logger.info(
            "API: Tarla oluşturuldu — %s (user: %s)",
            serializer.instance.name, self.request.user,
        )

    @action(detail=True, methods=['get'])
    def analyses(self, request, pk=None):
        """Tarlaya ait analizleri döndürür."""
        field = self.get_object()
        analyses = SoilAnalysis.objects.filter(field=field).order_by('-created_at')
        page = self.paginate_queryset(analyses)
        serializer = SoilAnalysisSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class SensorViewSet(viewsets.ModelViewSet):
    """
    Sensör verileri (SoilAnalysis) API endpoint'i — CRUD desteği.

    GET    /api/v1/sensors/         → Sensör verisi listesi
    POST   /api/v1/sensors/         → Yeni sensör verisi kaydet
    GET    /api/v1/sensors/{id}/    → Sensör verisi detayı
    PUT    /api/v1/sensors/{id}/    → Güncelle
    DELETE /api/v1/sensors/{id}/    → Sil
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SoilAnalysisFilter
    ordering_fields = ['created_at', 'temperature', 'humidity', 'ph']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return SoilAnalysisCreateSerializer
        return SoilAnalysisSerializer

    def get_queryset(self):
        """Sadece kullanıcının tarlalarına ait analizleri döndürür."""
        return SoilAnalysis.objects.filter(
            field__user=self.request.user,
        ).select_related('field')

    def perform_create(self, serializer):
        """Sensör verisi kaydedilirken tarla sahipliğini kontrol eder."""
        serializer.save()
        logger.info(
            "API: Sensör verisi kaydedildi — field=%s (user: %s)",
            serializer.instance.field.name, self.request.user,
        )


class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tahmin sonuçları (CropRecommendation) API endpoint'i — Sadece okuma.

    GET    /api/v1/predictions/         → Tahmin listesi
    GET    /api/v1/predictions/{id}/    → Tahmin detayı
    """

    serializer_class = CropRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CropRecommendationFilter
    ordering_fields = ['created_at', 'confidence', 'rank']
    ordering = ['-created_at']

    def get_queryset(self):
        """Sadece kullanıcının tahmin sonuçlarını döndürür."""
        return CropRecommendation.objects.filter(
            analysis__field__user=self.request.user,
        ).select_related('analysis', 'analysis__field')


class CareRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Bakım tavsiyeleri API endpoint'i — Sadece okuma.

    GET    /api/v1/care/         → Bakım tavsiyeleri listesi
    GET    /api/v1/care/{id}/    → Tavsiye detayı
    """

    serializer_class = CareRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """Sadece kullanıcının bakım tavsiyelerini döndürür."""
        return CareRecommendation.objects.filter(
            field__user=self.request.user,
        ).select_related('field')
