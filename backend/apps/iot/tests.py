"""IoT modülü testleri."""

import json
import uuid
from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import CustomUser
from apps.fields.models import Field
from apps.iot.constants import telemetry_topic
from apps.iot.models import Sensor, SensorReading
from apps.iot.services.ingest import IngestService
from apps.iot.services.mqtt_topics import parse_topic


class MqttTopicTests(TestCase):
    """Topic parse testleri."""

    def test_parse_telemetry_topic(self) -> None:
        topic = 'ats/dev/v1/1/tarla/2/sensor/550e8400-e29b-41d4-a716-446655440000/telemetry'
        parsed = parse_topic(topic)
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.env, 'dev')
        self.assertEqual(parsed.user_id, 1)
        self.assertEqual(parsed.field_id, 2)
        self.assertEqual(parsed.message_type, 'telemetry')

    def test_invalid_topic_returns_none(self) -> None:
        self.assertIsNone(parse_topic('invalid/topic'))


class IngestServiceTests(TestCase):
    """Ingest servisi testleri."""

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username='farmer',
            password='test-pass-123',
        )
        self.field = Field.objects.create(
            user=self.user,
            name='Test Tarla',
            area_decar=Decimal('10'),
        )
        self.sensor = Sensor.objects.create(
            field=self.field,
            name='Nem Sensörü',
            sensor_type='toprak_nemi',
        )

    def _telemetry_payload(self, message_id: str | None = None) -> dict:
        return {
            'schema_version': '1.0',
            'message_id': message_id or str(uuid.uuid4()),
            'sensor_id': str(self.sensor.id),
            'tarla_id': str(self.field.id),
            'tip': 'toprak_nemi',
            'deger': 42.5,
            'birim': '%',
            'olcum_zamani': '2026-05-18T14:32:01.123Z',
        }

    def test_telemetry_creates_reading(self) -> None:
        topic = telemetry_topic(self.user.id, self.field.id, str(self.sensor.id))
        payload = json.dumps(self._telemetry_payload()).encode()
        self.assertTrue(IngestService.handle_message(topic, payload))
        self.assertEqual(SensorReading.objects.count(), 1)
        self.sensor.refresh_from_db()
        self.assertEqual(self.sensor.status, 'aktif')

    def test_duplicate_message_id_is_idempotent(self) -> None:
        message_id = str(uuid.uuid4())
        topic = telemetry_topic(self.user.id, self.field.id, str(self.sensor.id))
        payload = json.dumps(self._telemetry_payload(message_id)).encode()
        IngestService.handle_message(topic, payload)
        IngestService.handle_message(topic, payload)
        self.assertEqual(SensorReading.objects.count(), 1)

    def test_provisioning_birth(self) -> None:
        token = self.sensor.issue_provisioning_token()
        topic = telemetry_topic(self.user.id, self.field.id, str(self.sensor.id)).replace(
            '/telemetry',
            '/birth',
        )
        payload = json.dumps({
            'schema_version': '1.0',
            'mac_adresi': 'AA:BB:CC:DD:EE:FF',
            'tip': 'toprak_nemi',
            'firmware': '1.0.0',
            'provisioning_token': token,
        }).encode()
        IngestService.handle_message(topic, payload)
        self.sensor.refresh_from_db()
        self.assertEqual(self.sensor.mac_address, 'AA:BB:CC:DD:EE:FF')
        self.assertIsNone(self.sensor.provisioning_token)
