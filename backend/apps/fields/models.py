"""
Field (Tarla) modeli.

Kullanıcıların tarla bilgilerini yönetmek için kullanılır.
"""

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model — created_at ve updated_at alanları sağlar."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme')

    class Meta:
        abstract = True


class Field(TimeStampedModel):
    """Kullanıcıya ait tarla. Boş veya ekili durumda olabilir."""

    SOIL_TYPE_CHOICES = [
        ('killi', 'Killi'),
        ('kumlu', 'Kumlu'),
        ('tinli', 'Tınlı'),
        ('killi_tinli', 'Killi-Tınlı'),
        ('kumlu_tinli', 'Kumlu-Tınlı'),
        ('limolu', 'Limolu'),
    ]

    STATUS_CHOICES = [
        ('empty', 'Boş'),
        ('planted', 'Ekili'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fields',
        verbose_name='Kullanıcı',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Tarla Adı',
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Konum',
    )
    area_decar = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Alan (Dekar)',
    )
    soil_type = models.CharField(
        max_length=50,
        choices=SOIL_TYPE_CHOICES,
        default='tinli',
        verbose_name='Toprak Tipi',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='empty',
        verbose_name='Durum',
    )
    current_crop = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Mevcut Ürün',
    )

    class Meta:
        verbose_name = 'Tarla'
        verbose_name_plural = 'Tarlalar'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_field_user_status'),
            models.Index(fields=['user', '-created_at'], name='idx_field_user_created'),
        ]

    def __str__(self) -> str:
        """Tarla adı ve durumunu döndürür."""
        return f"{self.name} ({self.get_status_display()})"

    @property
    def area_hectare(self) -> float:
        """Dekar cinsinden alanı hektara çevirir."""
        return float(self.area_decar) / 10


class SensorData(TimeStampedModel):
    """Tarladaki sensörlerden gelen anlık ölçüm verileri."""

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='sensor_data',
        verbose_name='Tarla',
    )
    humidity = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Nem (%)',
    )
    temperature = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Sıcaklık (°C)',
    )
    soil_moisture = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0,
        verbose_name='Toprak Nemi (%)',
    )
    plant_water_consumption = models.DecimalField(
        max_digits=6, decimal_places=2,
        default=0,
        verbose_name='Bitki Su Tüketimi (mm/gün)',
    )
    soil_ph = models.DecimalField(
        max_digits=4, decimal_places=2,
        verbose_name='Toprak pH',
    )
    light_intensity = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name='Işık Yoğunluğu (Lux)',
    )

    class Meta:
        verbose_name = 'Sensör Verisi'
        verbose_name_plural = 'Sensör Verileri'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', '-created_at'], name='idx_sensor_field_created'),
        ]

    def __str__(self) -> str:
        return f"{self.field.name} - {self.created_at:%d.%m.%Y %H:%M}"


class SensorReading(TimeStampedModel):
    """MQTT üzerinden gelen ham sensör okuma verileri."""

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='field_sensor_readings',
        verbose_name='Tarla',
    )
    sensor_type = models.CharField(
        max_length=30,
        verbose_name='Sensör Tipi',
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=4,
        verbose_name='Değer',
    )
    topic = models.CharField(
        max_length=200,
        verbose_name='Topic',
    )
    raw_payload = models.JSONField(
        default=dict,
        verbose_name='Ham Veri',
    )
    is_valid = models.BooleanField(
        default=True,
        verbose_name='Geçerli mi?',
    )

    class Meta:
        verbose_name = 'Sensör Okuması'
        verbose_name_plural = 'Sensör Okumaları'
        db_table = 'sensör_okumalari'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', 'sensor_type', '-created_at'], name='idx_sensorreading_field_type'),
        ]

    def __str__(self) -> str:
        return f"{self.field.name} - {self.sensor_type}: {self.value}"


class IrrigationLog(TimeStampedModel):
    """Tarlaya uygulanan sulama ve gübreleme işlemlerinin geçmişi."""

    LOG_TYPE_CHOICES = [
        ('irrigation', 'Sulama'),
        ('fertilization', 'Gübreleme'),
    ]

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='irrigation_logs',
        verbose_name='Tarla',
    )
    log_type = models.CharField(
        max_length=20,
        choices=LOG_TYPE_CHOICES,
        default='irrigation',
        verbose_name='İşlem Tipi',
    )
    amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name='Miktar (Litre veya kg)',
    )
    details = models.TextField(
        blank=True,
        verbose_name='Detaylar/Notlar',
    )

    class Meta:
        verbose_name = 'Sulama/Gübreleme Kaydı'
        verbose_name_plural = 'Sulama/Gübreleme Kayıtları'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', 'log_type', '-created_at'], name='idx_irrigation_field_type'),
        ]

    def __str__(self) -> str:
        return f"{self.field.name} - {self.get_log_type_display()} ({self.amount})"

