"""
MQTT Simulator — Sensör verisi simüle ederek MQTT broker'a yayınlar.

Her tarla için ayrı ayrı sensör verisi üretir ve ilgili topic'lere gönderir.
Topic hiyerarşisi mqtt.config modülünden yönetilir.

Kullanım:
    python manage.py mqtt_simulator
"""

import json
import random
import time

import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand

from apps.fields.models import Field
from mqtt.config import (
    DEFAULT_SENSOR_QOS,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_SENSORS,
    TOPIC_SENSORS_ALL,
    TOPIC_FARM_PATTERN,
)


class Command(BaseCommand):
    help = 'Sensör verisi simüle ederek MQTT broker\'a yayınlar (topic bazlı)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Yayın aralığı (saniye), varsayılan: 5',
        )

    def handle(self, *args, **options):
        interval = options['interval']

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        try:
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
            self.stdout.write(self.style.SUCCESS(
                f"✅ MQTT Broker'a bağlanıldı: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Bağlantı hatası: {e}"))
            return

        client.loop_start()
        self.stdout.write(f"🚀 Simülatör başlatıldı (aralık: {interval}s). Ctrl+C ile durdurun.\n")

        try:
            cycle = 0
            while True:
                cycle += 1
                fields = list(Field.objects.all().values_list('id', 'name', flat=False))

                if not fields:
                    self.stdout.write(self.style.WARNING(
                        "⚠️  DB'de tarla yok, field_id=1 ile simüle ediliyor."
                    ))
                    fields = [(1, 'Varsayılan Tarla')]

                self.stdout.write(f"\n--- Döngü {cycle} ({len(fields)} tarla) ---")

                for field_id, field_name in fields:
                    sensor_data = {
                        'field_id': field_id,
                        'timestamp': time.time(),
                        'soil_moisture': round(random.uniform(20.0, 80.0), 2),
                        'air_temperature': round(random.uniform(15.0, 35.0), 2),
                        'humidity': round(random.uniform(30.0, 90.0), 2),
                        'ph_level': round(random.uniform(5.0, 8.5), 2),
                        'irrigation_status': random.choice([0, 1]),
                    }

                    # 1) Toplu mesaj — tüm sensör verisi tek topic'te
                    client.publish(
                        TOPIC_SENSORS_ALL,
                        json.dumps(sensor_data),
                        qos=DEFAULT_SENSOR_QOS,
                    )

                    # 2) Ayrı topic'lere yayınla
                    topic_value_map = {
                        'humidity': sensor_data['humidity'],
                        'temperature': sensor_data['air_temperature'],
                        'soil_moisture': sensor_data['soil_moisture'],
                        'ph': sensor_data['ph_level'],
                    }

                    for sensor_type, value in topic_value_map.items():
                        # Yeni format (Görev 1)
                        topic = TOPIC_FARM_PATTERN.format(field_id=field_id, sensor_type=sensor_type)
                        payload = {
                            'field_id': field_id,
                            'timestamp': sensor_data['timestamp'],
                            'value': value,
                        }
                        client.publish(topic, json.dumps(payload), qos=DEFAULT_SENSOR_QOS)
                        
                        # Eski format (Geriye uyumluluk için)
                        old_topic = TOPIC_SENSORS.get(sensor_type)
                        if old_topic:
                            client.publish(old_topic, json.dumps(payload), qos=DEFAULT_SENSOR_QOS)

                    self.stdout.write(
                        f"  📡 {field_name} (#{field_id}): "
                        f"nem={sensor_data['humidity']}% "
                        f"sıcaklık={sensor_data['air_temperature']}°C "
                        f"toprak={sensor_data['soil_moisture']}% "
                        f"pH={sensor_data['ph_level']}"
                    )

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write("\n⏹️  Simülatör durduruldu.")
        finally:
            client.loop_stop()
            client.disconnect()
            self.stdout.write(self.style.SUCCESS("🔌 Bağlantı kapatıldı."))
