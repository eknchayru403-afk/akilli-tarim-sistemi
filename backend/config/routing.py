from django.urls import re_path

from apps.dashboard.consumers import SensorConsumer

websocket_urlpatterns = [
    re_path(r'ws/sensor/$', SensorConsumer.as_asgi()),
]
