"""
IoT modelleri — Sensör envanteri ve telemetri zaman serisi.

PostgreSQL: `sensor_readings` tablosu aylık RANGE partition + BRIN/B-tree indeksler.
"""

import secrets
import uuid

from django.db import models

from apps.fields.models import Field, TimeStampedModel

from .constants import SENSOR_STATUS_CHOICES, SENSOR_TYPE_CHOICES, SENSOR_TYPE_UNITS


class Sensor(TimeStampedModel):
    """Tarlaya bağlı MQTT sensör kaydı."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='sensors',
        verbose_name='Tarla',
    )
    name = models.CharField(
        max_length=120,
        verbose_name='Sensör Adı',
    )
    sensor_type = models.CharField(
        max_length=20,
        choices=SENSOR_TYPE_CHOICES,
        verbose_name='Tip',
    )
    location_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Konum',
    )
    status = models.CharField(
        max_length=20,
        choices=SENSOR_STATUS_CHOICES,
        default='pasif',
        verbose_name='Durum',
    )
    mac_address = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        unique=True,
        verbose_name='MAC Adresi',
    )
    firmware_version = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Firmware',
    )
    connection_protocol = models.CharField(
        max_length=20,
        default='MQTT',
        verbose_name='Bağlantı Protokolü',
    )
    provisioning_token = models.CharField(
        max_length=64,
        blank=True,
        unique=True,
        null=True,
        verbose_name='Provisioning Token',
    )
    last_reading_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Son Veri Zamanı',
    )

    class Meta:
        verbose_name = 'Sensör'
        verbose_name_plural = 'Sensörler'
        ordering = ['name']
        indexes = [
            models.Index(fields=['field', 'status'], name='idx_sensor_field_status'),
            models.Index(fields=['field', 'sensor_type'], name='idx_sensor_field_type'),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.get_sensor_type_display()})'

    @property
    def default_unit(self) -> str:
        """Sensör tipine göre varsayılan ölçü birimi."""
        return SENSOR_TYPE_UNITS.get(self.sensor_type, '')

    @property
    def mqtt_client_id(self) -> str:
        """Broker client_id formatı."""
        return f'ats-{self.id}'

    def issue_provisioning_token(self) -> str:
        """Tek kullanımlık provisioning token üretir ve kaydeder."""
        self.provisioning_token = secrets.token_urlsafe(32)
        self.save(update_fields=['provisioning_token', 'updated_at'])
        return self.provisioning_token

    def topic_paths(self) -> dict[str, str]:
        """MQTT topic yollarını döndürür."""
        from .constants import config_topic, status_topic, telemetry_topic

        user_id = self.field.user_id
        field_id = self.field_id
        sensor_id = str(self.id)
        return {
            'telemetry': telemetry_topic(user_id, field_id, sensor_id),
            'status': status_topic(user_id, field_id, sensor_id),
            'config': config_topic(user_id, field_id, sensor_id),
        }


class SensorReading(models.Model):
    """
    Yüksek frekanslı sensör ölçümü.

    PostgreSQL kolonları: field_id, sensor_id, timestamp (partition key).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='sensor_readings',
        verbose_name='Tarla',
        db_column='field_id',
    )
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='readings',
        verbose_name='Sensör',
        db_column='sensor_id',
    )
    message_id = models.UUIDField(
        unique=True,
        verbose_name='Mesaj ID',
    )
    value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Değer',
    )
    unit = models.CharField(
        max_length=20,
        verbose_name='Birim',
    )
    raw_payload = models.JSONField(
        verbose_name='Ham Veri',
    )
    measured_at = models.DateTimeField(
        verbose_name='Ölçüm Zamanı',
        db_column='timestamp',
        db_index=False,
    )
    received_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Alınma Zamanı',
    )

    class Meta:
        db_table = 'sensor_readings'
        verbose_name = 'Sensör Okuması'
        verbose_name_plural = 'Sensör Okumaları'
        ordering = ['-measured_at']
        indexes = [
            models.Index(
                fields=['field', 'measured_at'],
                name='idx_sr_field_timestamp',
            ),
            models.Index(
                fields=['sensor', 'measured_at'],
                name='idx_sr_sensor_timestamp',
            ),
            models.Index(
                fields=['measured_at', 'field'],
                name='idx_sr_timestamp_field',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.sensor.name} — {self.value} {self.unit}'

    def save(self, *args, **kwargs) -> None:
        """field_id denormalizasyonu — ingest ile tutarlılık."""
        if self.field_id is None and self.sensor_id:
            self.field_id = Sensor.objects.filter(pk=self.sensor_id).values_list(
                'field_id', flat=True,
            ).first()
        super().save(*args, **kwargs)
