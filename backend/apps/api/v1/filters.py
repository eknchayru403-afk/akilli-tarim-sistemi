"""
API v1 Filtreler.

Tarih aralığı ve field_id ile filtreleme desteği.
"""

import django_filters

from apps.analysis.models import CropRecommendation, SoilAnalysis
from apps.fields.models import Field, SensorData, SensorReading


class FieldFilter(django_filters.FilterSet):
    """Tarla filtreleme."""

    status = django_filters.ChoiceFilter(choices=Field.STATUS_CHOICES)
    soil_type = django_filters.ChoiceFilter(choices=Field.SOIL_TYPE_CHOICES)
    name = django_filters.CharFilter(lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Field
        fields = ['status', 'soil_type', 'name']


class SoilAnalysisFilter(django_filters.FilterSet):
    """Sensör verisi (toprak analizi) filtreleme."""

    field_id = django_filters.NumberFilter(field_name='field__id')
    source = django_filters.ChoiceFilter(choices=SoilAnalysis.SOURCE_CHOICES)
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = SoilAnalysis
        fields = ['field_id', 'source']


class CropRecommendationFilter(django_filters.FilterSet):
    """Tahmin sonuçları filtreleme."""

    field_id = django_filters.NumberFilter(field_name='analysis__field__id')
    analysis_id = django_filters.NumberFilter(field_name='analysis__id')
    crop_name = django_filters.CharFilter(lookup_expr='icontains')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    min_confidence = django_filters.NumberFilter(field_name='confidence', lookup_expr='gte')

    class Meta:
        model = CropRecommendation
        fields = ['field_id', 'analysis_id', 'crop_name']


class SensorDataFilter(django_filters.FilterSet):
    """
    SensorData filtreleme.

    Desteklenen filtreler:
      ?field_id=1
      ?date_from=2025-01-01T00:00:00
      ?date_to=2025-12-31T23:59:59
      ?min_humidity=30
      ?max_temperature=40
    """

    field_id = django_filters.NumberFilter(field_name='field__id')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    min_humidity = django_filters.NumberFilter(field_name='humidity', lookup_expr='gte')
    max_humidity = django_filters.NumberFilter(field_name='humidity', lookup_expr='lte')
    min_temperature = django_filters.NumberFilter(field_name='temperature', lookup_expr='gte')
    max_temperature = django_filters.NumberFilter(field_name='temperature', lookup_expr='lte')
    min_soil_ph = django_filters.NumberFilter(field_name='soil_ph', lookup_expr='gte')
    max_soil_ph = django_filters.NumberFilter(field_name='soil_ph', lookup_expr='lte')

    class Meta:
        model = SensorData
        fields = ['field_id']


class SensorReadingFilter(django_filters.FilterSet):
    """
    Ham MQTT sensör okuması filtreleme.

    Desteklenen filtreler:
      ?field_id=1
      ?sensor_type=humidity
      ?is_valid=true
      ?date_from=...
    """

    field_id = django_filters.NumberFilter(field_name='field__id')
    sensor_type = django_filters.CharFilter(lookup_expr='iexact')
    is_valid = django_filters.BooleanFilter()
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = SensorReading
        fields = ['field_id', 'sensor_type', 'is_valid']
