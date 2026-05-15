"""
API v1 Filtreler.

Tarih aralığı ve field_id ile filtreleme desteği.
"""

import django_filters

from apps.analysis.models import CropRecommendation, SoilAnalysis
from apps.fields.models import Field


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
