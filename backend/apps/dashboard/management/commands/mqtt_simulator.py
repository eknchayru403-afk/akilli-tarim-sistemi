import json
import time
import random
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt

from apps.fields.models import Field

class Command(BaseCommand):
    help = 'Simulates sensor data and publishes to MQTT broker'

    def handle(self, *args, **options):
        broker = 'broker.hivemq.com'
        port = 1883
        topic = 'atys/sensors'

        client = mqtt.Client()
        try:
            client.connect(broker, port, 60)
            self.stdout.write(self.style.SUCCESS(f"Successfully connected to MQTT broker at {broker}:{port}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to connect to MQTT broker: {e}"))
            return

        client.loop_start()

        self.stdout.write("Starting simulator... Press Ctrl+C to stop.")
        try:
            while True:
                # Get all fields
                fields = list(Field.objects.all().values_list('id', flat=True))
                
                if not fields:
                    self.stdout.write(self.style.WARNING("No fields found in database. Simulating for field_id=1 as fallback."))
                    fields = [1]
                
                for field_id in fields:
                    # Generate fake data
                    payload = {
                        "field_id": field_id,
                        "timestamp": time.time(),
                        "soil_moisture": round(random.uniform(20.0, 80.0), 2),
                        "air_temperature": round(random.uniform(15.0, 35.0), 2),
                        "irrigation_status": random.choice([0, 1]),
                    }
                    
                    client.publish(topic, json.dumps(payload))
                    self.stdout.write(f"Published to {topic}: {payload}")
                
                # Wait 5 seconds
                time.sleep(5)
        except KeyboardInterrupt:
            self.stdout.write("\nStopping simulator...")
        finally:
            client.loop_stop()
            client.disconnect()
            self.stdout.write(self.style.SUCCESS("Disconnected."))
