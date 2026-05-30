"""IoT app configuration."""

from django.apps import AppConfig


class IotConfig(AppConfig):
    """MQTT sensör envanteri ve telemetri ingest uygulaması."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.iot'
    verbose_name = 'IoT Sensörler'
