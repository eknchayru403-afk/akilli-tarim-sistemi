import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We allow everyone to connect to the sensor stream for now
        # You can add self.scope["user"].is_authenticated checks here
        
        # Subscribe to the 'sensor_data' group
        self.group_name = 'sensor_data'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    # Receive message from WebSocket (frontend -> backend)
    async def receive(self, text_data):
        pass # We might not need to receive data, just send

    # Receive message from group (backend -> frontend)
    async def sensor_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
