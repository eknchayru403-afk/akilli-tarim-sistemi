"""
MQTT Broker merkezi konfigürasyonu.

Tüm MQTT bağlantı bilgileri ve topic hiyerarşisi burada tanımlanır.
Publisher/subscriber scriptleri ve management komutları bu ayarları kullanır.
"""

# ── Broker Ayarları ──
MQTT_BROKER_HOST = 'broker.hivemq.com'
MQTT_BROKER_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_CLIENT_ID_PREFIX = 'atys'

# ── Topic Hiyerarşisi ──
# Ana topic kökü
TOPIC_ROOT = 'atys'

# Sensör topic'leri — her sensör tipi için ayrı topic
TOPIC_SENSORS = {
    'humidity': f'{TOPIC_ROOT}/sensors/humidity',
    'temperature': f'{TOPIC_ROOT}/sensors/temperature',
    'soil_moisture': f'{TOPIC_ROOT}/sensors/soil_moisture',
    'ph': f'{TOPIC_ROOT}/sensors/ph',
}

# Toplu sensör verisi (tüm veriler tek mesajda)
TOPIC_SENSORS_ALL = f'{TOPIC_ROOT}/sensors'

# Wildcard — tüm sensör topic'lerine abone olmak için
TOPIC_SENSORS_WILDCARD = f'{TOPIC_ROOT}/sensors/#'

# Komut topic'leri — cihaz kontrolü için
TOPIC_COMMANDS = {
    'irrigation': f'{TOPIC_ROOT}/commands/irrigation',
}

# Durum topic'leri — cihaz durumu için
TOPIC_STATUS = {
    'device': f'{TOPIC_ROOT}/status/device',
}

# ── QoS Seviyeleri ──
QOS_AT_MOST_ONCE = 0    # En fazla 1 kez (fire-and-forget)
QOS_AT_LEAST_ONCE = 1   # En az 1 kez (onaylı teslimat)
QOS_EXACTLY_ONCE = 2    # Tam olarak 1 kez (garantili)

# Sensör verileri için varsayılan QoS
DEFAULT_SENSOR_QOS = QOS_AT_MOST_ONCE

# Komut verileri için varsayılan QoS (daha güvenilir olmalı)
DEFAULT_COMMAND_QOS = QOS_AT_LEAST_ONCE
