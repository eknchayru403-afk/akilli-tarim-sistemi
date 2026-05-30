#!/usr/bin/env python
"""
MQTT Publisher Test Scripti.

Nem, sıcaklık ve toprak verisi simüle ederek ilgili topic'lere yayınlar.
Kullanım:
    python mqtt/publisher_test.py

Bu script bağımsız çalışır (Django gerektirmez).
"""

import json
import random
import time

import paho.mqtt.client as mqtt

from config import (
    DEFAULT_SENSOR_QOS,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_SENSORS,
)


def on_connect(client, userdata, flags, rc, properties=None):
    """Bağlantı callback'i."""
    if rc == 0:
        print(f"✅ MQTT Broker'a bağlanıldı: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    else:
        print(f"❌ Bağlantı başarısız, return code: {rc}")


def on_publish(client, userdata, mid, rc=None, properties=None):
    """Yayınlama callback'i."""
    print(f"   📤 Mesaj yayınlandı (mid: {mid})")


def generate_sensor_data(field_id: int = 1) -> dict:
    """
    Simüle edilmiş sensör verisi üretir.

    Args:
        field_id: Tarla kimliği.

    Returns:
        Sensör verisi dict.
    """
    return {
        'field_id': field_id,
        'timestamp': time.time(),
        'humidity': round(random.uniform(20.0, 90.0), 2),
        'temperature': round(random.uniform(5.0, 40.0), 2),
        'soil_moisture': round(random.uniform(15.0, 85.0), 2),
        'ph': round(random.uniform(4.5, 9.0), 2),
    }


def main():
    """Ana yayıncı döngüsü."""
    print("=" * 60)
    print("  ATYS — MQTT Publisher Test Scripti")
    print("=" * 60)
    print(f"  Broker : {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    print(f"  Topic'ler:")
    for name, topic in TOPIC_SENSORS.items():
        print(f"    • {topic}")
    print("=" * 60)

    # MQTT istemci oluştur
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
        client.loop_start()
        print("\n🚀 Yayın başlatılıyor... Durdurmak için Ctrl+C\n")

        cycle = 0
        while True:
            cycle += 1
            data = generate_sensor_data(field_id=1)
            print(f"\n--- Döngü {cycle} ---")

            # Her sensör tipini ayrı topic'e yayınla
            for sensor_type, topic in TOPIC_SENSORS.items():
                payload = {
                    'field_id': data['field_id'],
                    'timestamp': data['timestamp'],
                    'value': data[sensor_type],
                    'unit': _get_unit(sensor_type),
                }
                client.publish(topic, json.dumps(payload), qos=DEFAULT_SENSOR_QOS)
                print(f"   📡 {topic}: {payload['value']} {payload['unit']}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n⏹️  Yayın durduruldu.")
    finally:
        client.loop_stop()
        client.disconnect()
        print("🔌 Bağlantı kapatıldı.")


def _get_unit(sensor_type: str) -> str:
    """Sensör tipi için birim döndürür."""
    units = {
        'humidity': '%',
        'temperature': '°C',
        'soil_moisture': '%',
        'ph': 'pH',
    }
    return units.get(sensor_type, '')


if __name__ == '__main__':
    main()
