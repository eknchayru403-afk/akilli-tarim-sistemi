"""
API v1 Serializer'lar.

Field, SoilAnalysis, SensorData, SensorReading ve CropRecommendation
modelleri için seri hale getirme sınıfları.
"""

from rest_framework import serializers

from apps.accounts.models import CustomUser
from apps.analysis.models import CareRecommendation, CropRecommendation, SoilAnalysis
from apps.fields.models import Field, SensorData, SensorReading


# ---------------------------------------------------------------------------
# Kullanıcı
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    """Kullanıcı bilgisi serializer'ı (read-only)."""

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'city')
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Tarla (Field)
# ---------------------------------------------------------------------------

class FieldSerializer(serializers.ModelSerializer):
    """Tarla detay serializer'ı — GET işlemleri."""

    user = UserSerializer(read_only=True)
    area_hectare = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    soil_type_display = serializers.CharField(source='get_soil_type_display', read_only=True)

    class Meta:
        model = Field
        fields = (
            'id', 'user', 'name', 'location', 'area_decar', 'area_hectare',
            'soil_type', 'soil_type_display', 'status', 'status_display',
            'current_crop', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'user', 'area_hectare', 'created_at', 'updated_at')


class FieldCreateUpdateSerializer(serializers.ModelSerializer):
    """Tarla oluşturma/güncelleme serializer'ı — POST/PUT/PATCH."""

    class Meta:
        model = Field
        fields = ('name', 'location', 'area_decar', 'soil_type', 'status', 'current_crop')

    def validate_area_decar(self, value):
        """Alan değeri pozitif olmalı."""
        if value <= 0:
            raise serializers.ValidationError('Tarla alanı pozitif bir değer olmalıdır.')
        return value


# ---------------------------------------------------------------------------
# Sensör Verisi (SensorData)
# ---------------------------------------------------------------------------

class SensorDataSerializer(serializers.ModelSerializer):
    """
    Sensör verisi serializer'ı — GET/POST.

    GET /api/v1/sensors/           → Tüm sensör verileri (sayfalı)
    GET /api/v1/sensors/{id}/      → Tekil sensör verisi
    POST /api/v1/sensors/data/     → Yeni sensör verisi kaydet
    """

    field_name = serializers.CharField(source='field.name', read_only=True)
    field_location = serializers.CharField(source='field.location', read_only=True)

    class Meta:
        model = SensorData
        fields = (
            'id',
            'field', 'field_name', 'field_location',
            'humidity', 'temperature', 'soil_moisture',
            'plant_water_consumption', 'soil_ph', 'light_intensity',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'field_name', 'field_location', 'created_at', 'updated_at')

    def validate_field(self, value):
        """Sensör verisinin kaydedileceği tarlanın istek sahibine ait olduğunu doğrular."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and value.user != request.user:
            raise serializers.ValidationError('Bu tarla size ait değil.')
        return value

    def validate_humidity(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError('Nem değeri 0-100 arasında olmalıdır.')
        return value

    def validate_soil_ph(self, value):
        if not (0 <= value <= 14):
            raise serializers.ValidationError('pH değeri 0-14 arasında olmalıdır.')
        return value

    def validate_temperature(self, value):
        if not (-50 <= value <= 60):
            raise serializers.ValidationError('Sıcaklık değeri -50 ile 60 °C arasında olmalıdır.')
        return value


class SensorDataCreateSerializer(serializers.ModelSerializer):
    """
    Yeni sensör verisi oluşturma serializer'ı.

    POST /api/v1/sensors/data/ için kullanılır.
    """

    class Meta:
        model = SensorData
        fields = (
            'field',
            'humidity', 'temperature', 'soil_moisture',
            'plant_water_consumption', 'soil_ph', 'light_intensity',
        )

    def validate_field(self, value):
        """Tarla sahipliğini kontrol eder."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and value.user != request.user:
            raise serializers.ValidationError('Bu tarla size ait değil.')
        return value

    def validate_humidity(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError('Nem değeri 0-100 arasında olmalıdır.')
        return value

    def validate_soil_ph(self, value):
        if not (0 <= value <= 14):
            raise serializers.ValidationError('pH değeri 0-14 arasında olmalıdır.')
        return value

    def validate_temperature(self, value):
        if not (-50 <= value <= 60):
            raise serializers.ValidationError('Sıcaklık değeri -50 ile 60 °C arasında olmalıdır.')
        return value


# ---------------------------------------------------------------------------
# Ham Sensör Okuması (SensorReading — MQTT)
# ---------------------------------------------------------------------------

class SensorReadingSerializer(serializers.ModelSerializer):
    """
    MQTT tabanlı ham sensör okuması serializer'ı.

    GET /api/v1/sensors/readings/  → Ham okumaların listesi
    """

    field_name = serializers.CharField(source='field.name', read_only=True)

    class Meta:
        model = SensorReading
        fields = (
            'id',
            'field', 'field_name',
            'sensor_type', 'value', 'topic', 'raw_payload', 'is_valid',
            'created_at',
        )
        read_only_fields = ('id', 'field_name', 'created_at')


# ---------------------------------------------------------------------------
# Toprak Analizi (SoilAnalysis)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Tahmin Sonuçları (CropRecommendation)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Bakım Tavsiyeleri (CareRecommendation)
# ---------------------------------------------------------------------------

class CareRecommendationSerializer(serializers.ModelSerializer):
    """Bakım tavsiyesi serializer'ı."""

    field_name = serializers.CharField(source='field.name', read_only=True)
    recommendation_type_display = serializers.CharField(
        source='get_recommendation_type_display', read_only=True,
    )
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = CareRecommendation
        fields = (
            'id', 'field', 'field_name',
            'recommendation_type', 'recommendation_type_display',
            'message',
            'priority', 'priority_display',
            'is_done', 'created_at',
        )
        read_only_fields = ('id', 'field', 'created_at')


# ---------------------------------------------------------------------------
# Gübreleme Optimizasyon (Fertilizer Optimization)
# ---------------------------------------------------------------------------

class FertilizerOptimizationRequestSerializer(serializers.Serializer):
    """Gübreleme tahmini istek şeması."""
    nitrogen = serializers.FloatField(min_value=0)
    phosphorus = serializers.FloatField(min_value=0)
    potassium = serializers.FloatField(min_value=0)
    crop_type = serializers.CharField(max_length=100)
    growth_stage = serializers.CharField(max_length=100)


class FertilizerOptimizationResponseSerializer(serializers.Serializer):
    """Gübreleme tahmini yanıt şeması."""
    fertilizer_type = serializers.CharField(max_length=100)
    amount_kg_per_decare = serializers.FloatField()
    application_timing = serializers.CharField(max_length=100)
