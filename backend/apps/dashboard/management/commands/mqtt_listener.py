import json
import numpy as np
from collections import defaultdict, deque
from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from channels.layers import get_channel_layer
from apps.fields.models import Field
from apps.analysis.models import CareRecommendation

class Command(BaseCommand):
    help = 'Listens to MQTT broker, forwards to Channels, and detects anomalies using Z-Score.'

    def handle(self, *args, **options):
        broker = 'broker.hivemq.com'
        port = 1883
        topic = 'atys/sensors'
        
        channel_layer = get_channel_layer()

        # field_id -> { sensor_type: deque(maxlen=50) }
        sensor_buffers = defaultdict(lambda: defaultdict(lambda: deque(maxlen=50)))
        Z_THRESHOLD = 3.0

        def check_anomaly(field_id, sensor_type, value):
            buffer = sensor_buffers[field_id][sensor_type]
            
            # Yeterli veri yoksa anomali tespiti yapma (en az 10 veri olsun)
            if len(buffer) < 10:
                buffer.append(value)
                return
            
            mean = np.mean(buffer)
            std = np.std(buffer)
            
            # Standart sapma 0 ise Z-score tanımsız olur
            if std == 0:
                buffer.append(value)
                return
                
            z_score = abs(value - mean) / std
            
            if z_score > Z_THRESHOLD:
                self.stdout.write(self.style.WARNING(f"ANOMALY DETECTED: Field {field_id}, {sensor_type}={value} (Z={z_score:.2f})"))
                
                try:
                    field = Field.objects.get(id=field_id)
                    
                    # Tavsiye tipi belirleme
                    rec_type = 'temperature' if sensor_type == 'temperature' else 'soil_amendment'
                    
                    # Veritabanına kaydet
                    CareRecommendation.objects.create(
                        field=field,
                        recommendation_type=rec_type,
                        message=f"{sensor_type.capitalize()} sensöründe anlık anomali tespit edildi. Z-Skoru: {z_score:.2f}, Değer: {value}",
                        priority='critical'
                    )
                except Field.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Field with ID {field_id} not found, anomaly not saved."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error saving anomaly: {e}"))
            
            buffer.append(value)

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS(f"Connected to MQTT broker at {broker}:{port}"))
                client.subscribe(topic)
                self.stdout.write(self.style.SUCCESS(f"Subscribed to topic: {topic}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to connect, return code {rc}"))

        def on_message(client, userdata, msg):
            payload = msg.payload.decode('utf-8')
            
            try:
                data = json.loads(payload)
                field_id = data.get('field_id')
                
                if field_id is not None:
                    # Sensör değerlerini kontrol et
                    for sensor_type in ['temperature', 'soil_moisture', 'soil_ph']:
                        if sensor_type in data:
                            value = float(data[sensor_type])
                            check_anomaly(field_id, sensor_type, value)
                
                # Forward to channels group
                async_to_sync(channel_layer.group_send)(
                    'sensor_data',
                    {
                        'type': 'sensor_message',
                        'message': data
                    }
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing message: {e}"))

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(broker, port, 60)
            self.stdout.write("Starting listener... Press Ctrl+C to stop.")
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write("\nStopping listener...")
            client.disconnect()
            self.stdout.write(self.style.SUCCESS("Disconnected."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Connection failed: {e}"))
