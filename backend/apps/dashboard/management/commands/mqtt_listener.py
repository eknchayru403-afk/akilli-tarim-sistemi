import json
import asyncio
from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from channels.layers import get_channel_layer

class Command(BaseCommand):
    help = 'Listens to MQTT broker and forwards messages to Django Channels'

    def handle(self, *args, **options):
        broker = 'broker.hivemq.com'
        port = 1883
        topic = 'atys/sensors'
        
        channel_layer = get_channel_layer()

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS(f"Connected to MQTT broker at {broker}:{port}"))
                client.subscribe(topic)
                self.stdout.write(self.style.SUCCESS(f"Subscribed to topic: {topic}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to connect, return code {rc}"))

        def on_message(client, userdata, msg):
            payload = msg.payload.decode('utf-8')
            # self.stdout.write(f"Received from {msg.topic}: {payload}")
            
            try:
                data = json.loads(payload)
                
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
