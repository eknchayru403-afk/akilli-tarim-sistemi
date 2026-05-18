"""MQTT topic ve sensör sabitleri."""

from django.conf import settings

SENSOR_TYPE_CHOICES = [
    ('nem', 'Nem'),
    ('sicaklik', 'Sıcaklık'),
    ('ph', 'pH'),
    ('yagis', 'Yağış'),
    ('isik', 'Işık'),
    ('toprak_nemi', 'Toprak Nemi'),
    ('co2', 'CO₂'),
    ('ruzgar', 'Rüzgar'),
]

SENSOR_STATUS_CHOICES = [
    ('aktif', 'Aktif'),
    ('pasif', 'Pasif'),
    ('baglanti_yok', 'Bağlantı Yok'),
    ('hata', 'Hata'),
    ('bakimda', 'Bakımda'),
]

SENSOR_TYPE_UNITS = {
    'nem': '%',
    'toprak_nemi': '%',
    'sicaklik': '°C',
    'ph': 'pH',
    'yagis': 'mm',
    'isik': 'lux',
    'co2': 'ppm',
    'ruzgar': 'm/s',
}

MESSAGE_TYPES = ('telemetry', 'status', 'birth', 'config')

TOPIC_PATTERN = (
    r'^ats/(?P<env>[^/]+)/(?P<version>[^/]+)/(?P<user_id>\d+)/'
    r'tarla/(?P<field_id>\d+)/sensor/(?P<sensor_id>[0-9a-f-]{36})/'
    r'(?P<message_type>telemetry|status|birth|config)$'
)


def mqtt_env() -> str:
    """Aktif MQTT ortam adını döndürür (dev, staging, prod)."""
    return getattr(settings, 'MQTT_ENV', 'dev')


def mqtt_version() -> str:
    """Topic API sürümünü döndürür."""
    return getattr(settings, 'MQTT_TOPIC_VERSION', 'v1')


def topic_prefix(user_id: int, field_id: int, sensor_id: str) -> str:
    """Sensör topic kök yolunu oluşturur."""
    return (
        f'ats/{mqtt_env()}/{mqtt_version()}/{user_id}/'
        f'tarla/{field_id}/sensor/{sensor_id}'
    )


def telemetry_topic(user_id: int, field_id: int, sensor_id: str) -> str:
    """Telemetri publish topic'i."""
    return f'{topic_prefix(user_id, field_id, sensor_id)}/telemetry'


def status_topic(user_id: int, field_id: int, sensor_id: str) -> str:
    """Durum publish topic'i."""
    return f'{topic_prefix(user_id, field_id, sensor_id)}/status'


def config_topic(user_id: int, field_id: int, sensor_id: str) -> str:
    """Yapılandırma subscribe topic'i (broker → cihaz)."""
    return f'{topic_prefix(user_id, field_id, sensor_id)}/config'


def ingest_subscription_pattern() -> str:
    """Ingest servisi için shared subscription kalıbı."""
    env = mqtt_env()
    version = mqtt_version()
    return f'$share/ingest-group/ats/{env}/{version}/+/tarla/+/sensor/+/+'
