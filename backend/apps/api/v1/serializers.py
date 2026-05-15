"""
API v1 Serializer'lar.

Field, SoilAnalysis ve CropRecommendation modelleri için
seri hale getirme sınıfları.
"""

from rest_framework import serializers

from apps.accounts.models import CustomUser
from apps.analysis.models import CareRecommendation, CropRecommendation, SoilAnalysis
from apps.fields.models import Field


class UserSerializer(serializers.ModelSerializer):
    """Kullanıcı bilgisi serializer'ı (read-only)."""

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'city')
        read_only_fields = fields


class FieldSerializer(serializers.ModelSerializer):
    """Tarla CRUD serializer'ı."""

    user = UserSerializer(read_only=True)
    area_hectare = serializers.ReadOnlyField()

    class Meta:
        model = Field
        fields = (
            'id', 'user', 'name', 'location', 'area_decar', 'area_hectare',
            'soil_type', 'status', 'current_crop', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class FieldCreateUpdateSerializer(serializers.ModelSerializer):
    """Tarla oluşturma/güncelleme serializer'ı."""

    class Meta:
        model = Field
        fields = ('name', 'location', 'area_decar', 'soil_type', 'status', 'current_crop')


class SoilAnalysisSerializer(serializers.ModelSerializer):
    """Sensör verisi (Toprak analizi) serializer'ı."""

    field_name = serializers.CharField(source='field.name', read_only=True)

    class Meta:
        model = SoilAnalysis
        fields = (
            'id', 'field', 'field_name', 'nitrogen', 'phosphorus', 'potassium',
            'temperature', 'humidity', 'ph', 'rainfall', 'source',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class SoilAnalysisCreateSerializer(serializers.ModelSerializer):
    """Sensör verisi oluşturma serializer'ı."""

    class Meta:
        model = SoilAnalysis
        fields = (
            'field', 'nitrogen', 'phosphorus', 'potassium',
            'temperature', 'humidity', 'ph', 'rainfall', 'source',
        )

    def validate_field(self, value):
        """Tarla sahipliğini kontrol eder."""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError('Bu tarla size ait değil.')
        return value


class CropRecommendationSerializer(serializers.ModelSerializer):
    """Ürün önerisi (tahmin sonucu) serializer'ı."""

    analysis_date = serializers.DateTimeField(source='analysis.created_at', read_only=True)
    field_name = serializers.CharField(source='analysis.field.name', read_only=True)

    class Meta:
        model = CropRecommendation
        fields = (
            'id', 'analysis', 'analysis_date', 'field_name',
            'crop_name', 'crop_name_tr', 'confidence',
            'estimated_yield_kg', 'estimated_revenue_tl', 'rank',
            'created_at',
        )
        read_only_fields = fields


class CareRecommendationSerializer(serializers.ModelSerializer):
    """Bakım tavsiyesi serializer'ı."""

    field_name = serializers.CharField(source='field.name', read_only=True)

    class Meta:
        model = CareRecommendation
        fields = (
            'id', 'field', 'field_name', 'recommendation_type',
            'message', 'priority', 'is_done', 'created_at',
        )
        read_only_fields = ('id', 'field', 'created_at')
