"""
MQTT Listener — Broker'dan sensör mesajlarını dinler ve Django Channels'a iletir.

Wildcard subscription ile tüm sensör topic'lerini dinler.
Gelen mesajlar WebSocket üzerinden gerçek zamanlı dashboard'a aktarılır.

Kullanım:
    python manage.py mqtt_listener
"""

import json
import logging

import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand

from mqtt.config import (
    DEFAULT_SENSOR_QOS,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_SENSORS_ALL,
    TOPIC_SENSORS_WILDCARD,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'MQTT broker\'dan sensör mesajlarını dinler ve Channels\'a iletir (wildcard)'

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS(
                    f"✅ MQTT Broker'a bağlanıldı: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}"
                ))

                # Wildcard ile tüm sensör topic'lerine abone ol
                client.subscribe(TOPIC_SENSORS_WILDCARD, qos=DEFAULT_SENSOR_QOS)
                self.stdout.write(self.style.SUCCESS(
                    f"📥 Abone olundu: {TOPIC_SENSORS_WILDCARD}"
                ))

                # Toplu sensör topic'ine de abone ol
                client.subscribe(TOPIC_SENSORS_ALL, qos=DEFAULT_SENSOR_QOS)
                self.stdout.write(self.style.SUCCESS(
                    f"📥 Abone olundu: {TOPIC_SENSORS_ALL}"
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"❌ Bağlantı başarısız, return code: {rc}"
                ))

        def on_message(client, userdata, msg):
            payload = msg.payload.decode('utf-8')
            try:
                data = json.loads(payload)

                # Topic bilgisini mesaja ekle
                data['_topic'] = msg.topic

                # Topic'ten sensör tipini çıkar
                topic_parts = msg.topic.split('/')
                if len(topic_parts) > 2:
                    data['_sensor_type'] = topic_parts[-1]

                # Django Channels grubuna ilet
                async_to_sync(channel_layer.group_send)(
                    'sensor_data',
                    {
                        'type': 'sensor_message',
                        'message': data,
                    }
                )

                logger.info(
                    "MQTT mesajı iletildi: topic=%s, field_id=%s",
                    msg.topic, data.get('field_id', '?'),
                )

            except json.JSONDecodeError:
                logger.warning("Geçersiz JSON: %s", payload[:200])
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Mesaj işleme hatası: {e}"))
                logger.exception("MQTT mesaj işleme hatası")

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
            self.stdout.write("🔊 Listener başlatılıyor... Ctrl+C ile durdurun.")
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write("\n⏹️  Listener durduruldu.")
            client.disconnect()
            self.stdout.write(self.style.SUCCESS("🔌 Bağlantı kapatıldı."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Bağlantı hatası: {e}"))
            logger.exception("MQTT bağlantı hatası")
