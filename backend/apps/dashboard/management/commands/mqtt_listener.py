"""
MQTT Listener — Broker'dan sensör mesajlarını dinler ve Django Channels'a iletir.
Ayrıca gelen verileri SensorReading tablosuna kaydeder.
"""

import json
import logging
import time

from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import numpy as np
from collections import defaultdict, deque

from apps.fields.models import Field, SensorReading
from apps.analysis.models import CareRecommendation
from mqtt.config import (
    DEFAULT_SENSOR_QOS,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_SENSORS_WILDCARD,
    TOPIC_FARM_WILDCARD,
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Listens to MQTT broker, saves data, forwards to Channels, and detects anomalies.'

    def handle(self, *args, **options):
        self.channel_layer = get_channel_layer()
        self.sensor_buffers = defaultdict(lambda: defaultdict(lambda: deque(maxlen=50)))
        self.Z_THRESHOLD = 3.0

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        # Otomatik yeniden bağlanma mekanizması (Exponential backoff)
        client.reconnect_delay_set(min_delay=1, max_delay=60)
        
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message

        try:
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
            self.stdout.write(self.style.SUCCESS(f"🔊 Listener başlatılıyor... Broker: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}"))
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n⏹️ Listener durduruldu."))
        finally:
            client.disconnect()
            self.stdout.write(self.style.SUCCESS("🔌 Bağlantı kapatıldı."))

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.stdout.write(self.style.SUCCESS("✅ MQTT Broker'a bağlanıldı."))
            client.subscribe(TOPIC_SENSORS_WILDCARD, qos=DEFAULT_SENSOR_QOS)
            client.subscribe(TOPIC_FARM_WILDCARD, qos=DEFAULT_SENSOR_QOS)
            self.stdout.write(self.style.SUCCESS(f"📥 Abone olundu: {TOPIC_FARM_WILDCARD} ve {TOPIC_SENSORS_WILDCARD}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Bağlantı başarısız, return code: {rc}"))

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        if rc != 0:
            self.stdout.write(self.style.WARNING(f"⚠️ Beklenmeyen bağlantı kopması (rc={rc}). Yeniden bağlanılmaya çalışılıyor..."))

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        try:
            data = json.loads(payload)
            data['_topic'] = msg.topic
            
            # Extract field_id and sensor_type from topic
            # Old format: atys/sensors/{type}  --> needs field_id in payload
            # New format: farm/{field_id}/sensor/{type}
            topic_parts = msg.topic.split('/')
            field_id = data.get('field_id')
            sensor_type = 'unknown'

            if len(topic_parts) == 4 and topic_parts[0] == 'farm' and topic_parts[2] == 'sensor':
                try:
                    field_id = int(topic_parts[1])
                except ValueError:
                    pass
                sensor_type = topic_parts[3]
            elif len(topic_parts) > 2 and topic_parts[0] == 'atys':
                sensor_type = topic_parts[-1]
            
            data['_sensor_type'] = sensor_type
            if field_id:
                data['field_id'] = field_id

            is_valid = self._validate_payload(data)
            
            # Forward to channels group
            async_to_sync(self.channel_layer.group_send)(
                'sensor_data',
                {
                    'type': 'sensor_message',
                    'message': data,
                }
            )

            if field_id and is_valid:
                value = data.get('value')
                if value is not None:
                    value = float(value)
                    self._save_to_db(field_id, sensor_type, value, msg.topic, data)
                    self._check_anomaly(field_id, sensor_type, value)
                else:
                    # In case of payload like {"temperature": 25.0} without explicit 'value' key
                    for key in ['temperature', 'humidity', 'soil_moisture', 'ph']:
                        if key in data:
                            val = float(data[key])
                            self._save_to_db(field_id, key, val, msg.topic, data)
                            self._check_anomaly(field_id, key, val)

        except json.JSONDecodeError:
            logger.warning(f"Geçersiz JSON: {payload[:200]}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Mesaj işleme hatası: {e}"))
            logger.exception("MQTT mesaj işleme hatası")

    def _validate_payload(self, data: dict) -> bool:
        """Gelen sensör verisini doğrular."""
        if 'field_id' not in data:
            return False
        
        # Check if value exists and is a number, OR if direct keys exist
        has_value = 'value' in data and isinstance(data['value'], (int, float))
        has_direct_keys = any(k in data and isinstance(data[k], (int, float)) for k in ['temperature', 'humidity', 'soil_moisture', 'ph'])
        
        return has_value or has_direct_keys

    def _save_to_db(self, field_id, sensor_type, value, topic, raw_data):
        try:
            field = Field.objects.get(id=field_id)
            SensorReading.objects.create(
                field=field,
                sensor_type=sensor_type,
                value=value,
                topic=topic,
                raw_payload=raw_data,
                is_valid=True
            )
        except Field.DoesNotExist:
            logger.warning(f"Field {field_id} not found. Cannot save sensor reading.")
        except Exception as e:
            logger.error(f"Error saving to DB: {e}")

    def _check_anomaly(self, field_id, sensor_type, value):
        buffer = self.sensor_buffers[field_id][sensor_type]
        
        if len(buffer) < 10:
            buffer.append(value)
            return
        
        mean = np.mean(buffer)
        std = np.std(buffer)
        
        if std == 0:
            buffer.append(value)
            return
            
        z_score = abs(value - mean) / std
        
        if z_score > self.Z_THRESHOLD:
            self.stdout.write(self.style.WARNING(f"ANOMALY DETECTED: Field {field_id}, {sensor_type}={value} (Z={z_score:.2f})"))
            
            try:
                field = Field.objects.get(id=field_id)
                rec_type = 'temperature' if sensor_type == 'temperature' else 'soil_amendment'
                
                CareRecommendation.objects.create(
                    field=field,
                    recommendation_type=rec_type,
                    message=f"{sensor_type.capitalize()} sensöründe anlık anomali tespit edildi. Z-Skoru: {z_score:.2f}, Değer: {value}",
                    priority='critical'
                )
            except Field.DoesNotExist:
                pass
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error saving anomaly: {e}"))
        
        buffer.append(value)
