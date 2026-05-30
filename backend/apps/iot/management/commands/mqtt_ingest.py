"""Management command: mqtt_ingest — MQTT broker'dan telemetri dinler."""

import logging
import signal
import ssl
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

import paho.mqtt.client as mqtt

from apps.iot.constants import ingest_subscription_pattern
from apps.iot.services.ingest import IngestService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """EMQX/Mosquitto broker'a bağlanır ve shared subscription ile mesaj işler."""

    help = 'MQTT broker üzerinden sensör telemetrisini dinler ve veritabanına yazar.'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._client: mqtt.Client | None = None
        self._running = True

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--topic',
            default=None,
            help='Özel subscribe topic (varsayılan: shared ingest pattern)',
        )

    def handle(self, *args, **options) -> None:
        topic = options['topic'] or ingest_subscription_pattern()
        self.stdout.write(f'MQTT ingest başlıyor — subscribe: {topic}')

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=getattr(settings, 'MQTT_CLIENT_ID', 'ats-ingest-1'),
            protocol=mqtt.MQTTv311,
        )
        self._client = client

        username = getattr(settings, 'MQTT_USERNAME', '')
        password = getattr(settings, 'MQTT_PASSWORD', '')
        if username:
            client.username_pw_set(username, password)

        if getattr(settings, 'MQTT_TLS', False):
            tls_context = ssl.create_default_context()
            ca_certs = getattr(settings, 'MQTT_CA_CERT', None)
            if ca_certs:
                tls_context.load_verify_locations(ca_certs)
            client.tls_set_context(tls_context)

        client.on_connect = self._on_connect(topic)
        client.on_message = self._on_message
        client.on_disconnect = self._on_disconnect

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        host = getattr(settings, 'MQTT_HOST', 'localhost')
        port = getattr(settings, 'MQTT_PORT', 1883)
        keepalive = getattr(settings, 'MQTT_KEEPALIVE', 60)

        try:
            client.connect(host, port, keepalive=keepalive)
        except OSError as exc:
            self.stderr.write(self.style.ERROR(f'Broker bağlantı hatası: {exc}'))
            sys.exit(1)

        client.loop_start()
        self.stdout.write(self.style.SUCCESS(f'Bağlandı: {host}:{port}'))

        import time
        while self._running:
            time.sleep(0.5)

        client.loop_stop()
        client.disconnect()
        self.stdout.write('MQTT ingest durduruldu.')

    def _on_connect(self, topic: str):
        def callback(client, userdata, connect_flags, reason_code, properties) -> None:
            if reason_code != 0:
                logger.error('MQTT bağlantı reddedildi: %s', reason_code)
                return
            client.subscribe(topic, qos=1)
            logger.info('Subscribed: %s', topic)

        return callback

    def _on_message(self, client, userdata, message) -> None:
        IngestService.handle_message(message.topic, message.payload)

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties) -> None:
        if reason_code != 0:
            logger.warning('MQTT bağlantı koptu: %s', reason_code)

    def _signal_handler(self, signum, frame) -> None:
        self._running = False
