#!/usr/bin/env python
"""
MQTT Subscriber Test Scripti.

Tüm sensör topic'lerine abone olup gelen mesajları terminalde gösterir.
Kullanım:
    python mqtt/subscriber_test.py

Bu script bağımsız çalışır (Django gerektirmez).
"""

import json
from datetime import datetime

import paho.mqtt.client as mqtt

from config import (
    DEFAULT_SENSOR_QOS,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_SENSORS,
    TOPIC_SENSORS_WILDCARD,
)


def on_connect(client, userdata, flags, rc, properties=None):
    """Bağlantı callback'i — başarılı bağlantıda topic'lere abone ol."""
    if rc == 0:
        print(f"✅ MQTT Broker'a bağlanıldı: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")

        # Wildcard ile tüm sensör topic'lerine abone ol
        client.subscribe(TOPIC_SENSORS_WILDCARD, qos=DEFAULT_SENSOR_QOS)
        print(f"📥 Abone olundu: {TOPIC_SENSORS_WILDCARD}")
        print("-" * 60)
    else:
        print(f"❌ Bağlantı başarısız, return code: {rc}")


def on_message(client, userdata, msg):
    """Mesaj alındığında çağrılır."""
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        timestamp = datetime.fromtimestamp(payload.get('timestamp', 0))

        # Topic'ten sensör tipini çıkar
        topic_parts = msg.topic.split('/')
        sensor_type = topic_parts[-1] if len(topic_parts) > 2 else 'bilinmeyen'

        # Renkli çıktı
        icon = _get_icon(sensor_type)
        print(
            f"  {icon} [{timestamp:%H:%M:%S}] "
            f"Topic: {msg.topic} | "
            f"Tarla: {payload.get('field_id', '?')} | "
            f"Değer: {payload.get('value', '?')} {payload.get('unit', '')}"
        )
    except json.JSONDecodeError:
        print(f"  ⚠️  JSON parse hatası: {msg.payload.decode('utf-8')}")
    except Exception as e:
        print(f"  ❌ Hata: {e}")


def on_disconnect(client, userdata, rc, properties=None, reason_code=None):
    """Bağlantı koptuğunda çağrılır."""
    if rc != 0:
        print(f"\n⚠️  Bağlantı beklenmedik şekilde koptu (rc: {rc})")


def _get_icon(sensor_type: str) -> str:
    """Sensör tipine göre ikon döndürür."""
    icons = {
        'humidity': '💧',
        'temperature': '🌡️',
        'soil_moisture': '🌱',
        'ph': '🧪',
    }
    return icons.get(sensor_type, '📡')


def main():
    """Ana abone döngüsü."""
    print("=" * 60)
    print("  ATYS — MQTT Subscriber Test Scripti")
    print("=" * 60)
    print(f"  Broker : {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    print(f"  Dinlenen topic: {TOPIC_SENSORS_WILDCARD}")
    print(f"  Alt topic'ler:")
    for name, topic in TOPIC_SENSORS.items():
        print(f"    • {topic}")
    print("=" * 60)

    # MQTT istemci oluştur
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
        print("\n🔊 Dinleme başlatılıyor... Durdurmak için Ctrl+C\n")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n⏹️  Dinleme durduruldu.")
    finally:
        client.disconnect()
        print("🔌 Bağlantı kapatıldı.")


if __name__ == '__main__':
    main()
