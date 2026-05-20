"""
API v1 ViewSet'ler.

Field, SensorData, SensorReading, SoilAnalysis ve CropRecommendation için
CRUD ve read-only endpoint'ler. JWT tabanlı kimlik doğrulama ile korunur.
"""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.analysis.models import CareRecommendation, CropRecommendation, SoilAnalysis
from apps.fields.models import Field, SensorData, SensorReading

from .filters import (
    CropRecommendationFilter,
    FieldFilter,
    SensorDataFilter,
    SensorReadingFilter,
    SoilAnalysisFilter,
)
from .pagination import StandardPagination
from .permissions import IsOwner
from .serializers import (
    CareRecommendationSerializer,
    CropRecommendationSerializer,
    FieldCreateUpdateSerializer,
    FieldSerializer,
    SensorDataCreateSerializer,
    SensorDataSerializer,
    SensorReadingSerializer,
    SoilAnalysisCreateSerializer,
    SoilAnalysisSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tarla (Field)
# ---------------------------------------------------------------------------

class FieldViewSet(viewsets.ModelViewSet):
    """
    Tarla API endpoint'i — Tam CRUD desteği.

    GET    /api/v1/fields/          → Tarla listesi (filtreli, sayfalı)
    POST   /api/v1/fields/          → Yeni tarla oluştur
    GET    /api/v1/fields/{id}/     → Tarla detayı
    PUT    /api/v1/fields/{id}/     → Tarla güncelle (tam)
    PATCH  /api/v1/fields/{id}/     → Tarla güncelle (kısmi)
    DELETE /api/v1/fields/{id}/     → Tarla sil

    Özel:
    GET    /api/v1/fields/{id}/analyses/   → Tarlaya ait toprak analizleri
    GET    /api/v1/fields/{id}/sensors/    → Tarlaya ait sensör verileri
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

    @action(detail=True, methods=['get'], url_path='analyses')
    def analyses(self, request, pk=None):
        """
        Tarlaya ait toprak analizlerini döndürür.

        GET /api/v1/fields/{id}/analyses/
        """
        field = self.get_object()
        queryset = SoilAnalysis.objects.filter(field=field).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        serializer = SoilAnalysisSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='sensors')
    def sensors(self, request, pk=None):
        """
        Tarlaya ait sensör verilerini döndürür.

        GET /api/v1/fields/{id}/sensors/
        """
        field = self.get_object()
        queryset = SensorData.objects.filter(field=field).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        serializer = SensorDataSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='predictions')
    def predictions(self, request, pk=None):
        """
        Tarlaya ait tahmin sonuçlarını döndürür.

        GET /api/v1/fields/{id}/predictions/
        """
        field = self.get_object()
        queryset = CropRecommendation.objects.filter(
            analysis__field=field,
        ).select_related('analysis').order_by('-created_at')
        page = self.paginate_queryset(queryset)
        serializer = CropRecommendationSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


# ---------------------------------------------------------------------------
# Sensör Verisi (SensorData)
# ---------------------------------------------------------------------------

class SensorDataViewSet(viewsets.ModelViewSet):
    """
    Sensör verisi API endpoint'i — Tam CRUD desteği.

    GET    /api/v1/sensors/          → Sensör verisi listesi (filtreli, sayfalı)
    POST   /api/v1/sensors/          → Yeni sensör verisi oluştur
    GET    /api/v1/sensors/{id}/     → Tekil sensör verisi detayı
    PUT    /api/v1/sensors/{id}/     → Sensör verisi güncelle (tam)
    PATCH  /api/v1/sensors/{id}/     → Sensör verisi güncelle (kısmi)
    DELETE /api/v1/sensors/{id}/     → Sensör verisi sil

    Özel:
    POST   /api/v1/sensors/data/     → Hızlı veri gönderme endpoint'i
    GET    /api/v1/sensors/latest/   → Her tarladan en son sensör verisi
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SensorDataFilter
    ordering_fields = ['created_at', 'temperature', 'humidity', 'soil_ph']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update', 'data'):
            return SensorDataCreateSerializer
        return SensorDataSerializer

    def get_queryset(self):
        """Sadece kullanıcının tarlalarına ait sensör verilerini döndürür."""
        return SensorData.objects.filter(
            field__user=self.request.user,
        ).select_related('field')

    def perform_create(self, serializer):
        """Sensör verisi kaydederken logla."""
        serializer.save()
        logger.info(
            "API: Sensör verisi kaydedildi — field=%s (user: %s)",
            serializer.instance.field.name, self.request.user,
        )

    @action(detail=False, methods=['post'], url_path='data')
    def data(self, request):
        """
        Hızlı sensör verisi gönderme endpoint'i.

        POST /api/v1/sensors/data/

        Body:
        {
            "field": 1,
            "humidity": 65.5,
            "temperature": 22.3,
            "soil_moisture": 40.0,
            "plant_water_consumption": 3.5,
            "soil_ph": 6.8,
            "light_intensity": 12000
        }
        """
        serializer = SensorDataCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            instance = serializer.save()
            logger.info(
                "API: Sensör verisi (data endpoint) — field=%s (user: %s)",
                instance.field.name, request.user,
            )
            return Response(
                SensorDataSerializer(instance, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='latest')
    def latest(self, request):
        """
        Kullanıcının her tarlasından en son sensör verisini döndürür.

        GET /api/v1/sensors/latest/
        """
        fields = Field.objects.filter(user=request.user)
        results = []
        for field in fields:
            latest = SensorData.objects.filter(field=field).order_by('-created_at').first()
            if latest:
                results.append(SensorDataSerializer(latest, context={'request': request}).data)

        return Response({
            'count': len(results),
            'results': results,
        })


# ---------------------------------------------------------------------------
# Ham Sensör Okuması (SensorReading — MQTT)
# ---------------------------------------------------------------------------

class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ham MQTT sensör okumaları — Sadece okuma.

    GET /api/v1/sensors/readings/         → Ham okuma listesi (filtreli)
    GET /api/v1/sensors/readings/{id}/    → Tekil ham okuma
    """

    serializer_class = SensorReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SensorReadingFilter
    ordering_fields = ['created_at', 'sensor_type', 'value']
    ordering = ['-created_at']

    def get_queryset(self):
        """Sadece kullanıcının tarlalarına ait okumaları döndürür."""
        return SensorReading.objects.filter(
            field__user=self.request.user,
        ).select_related('field')


# ---------------------------------------------------------------------------
# Toprak Analizi (SoilAnalysis)
# ---------------------------------------------------------------------------

class SensorViewSet(viewsets.ModelViewSet):
    """
    Toprak analiz verisi (SoilAnalysis) API endpoint'i — CRUD desteği.

    GET    /api/v1/soil-analyses/         → Toprak analizi listesi
    POST   /api/v1/soil-analyses/         → Yeni toprak analizi oluştur
    GET    /api/v1/soil-analyses/{id}/    → Analiz detayı
    PUT    /api/v1/soil-analyses/{id}/    → Güncelle
    DELETE /api/v1/soil-analyses/{id}/    → Sil
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
            "API: Toprak analizi kaydedildi — field=%s (user: %s)",
            serializer.instance.field.name, self.request.user,
        )


# ---------------------------------------------------------------------------
# Tahmin Sonuçları (CropRecommendation)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Bakım Tavsiyeleri (CareRecommendation)
# ---------------------------------------------------------------------------

class CareRecommendationViewSet(viewsets.ModelViewSet):
    """
    Bakım tavsiyeleri API endpoint'i.

    GET    /api/v1/care/         → Bakım tavsiyeleri listesi
    GET    /api/v1/care/{id}/    → Tavsiye detayı
    PATCH  /api/v1/care/{id}/   → is_done alanını güncelle (tamamlandı işaretle)
    """

    serializer_class = CareRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    http_method_names = ['get', 'patch', 'head', 'options']  # POST ve DELETE yok

    def get_queryset(self):
        """Sadece kullanıcının bakım tavsiyelerini döndürür."""
        return CareRecommendation.objects.filter(
            field__user=self.request.user,
        ).select_related('field')
