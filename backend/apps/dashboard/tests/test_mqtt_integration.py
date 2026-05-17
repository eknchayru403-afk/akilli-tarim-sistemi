import json
from django.test import TestCase
from apps.fields.models import Field, SensorReading
from django.contrib.auth import get_user_model
from apps.dashboard.management.commands.mqtt_listener import Command

User = get_user_model()

class MQTTIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.field = Field.objects.create(
            user=self.user,
            name='Test Tarla',
            area_decar=10.5,
            soil_type='tinli'
        )
        self.cmd = Command()
        self.cmd.Z_THRESHOLD = 3.0

    def test_payload_validation_valid(self):
        valid_payload1 = {'field_id': self.field.id, 'value': 25.4}
        self.assertTrue(self.cmd._validate_payload(valid_payload1))

        valid_payload2 = {'field_id': self.field.id, 'temperature': 25.4}
        self.assertTrue(self.cmd._validate_payload(valid_payload2))

    def test_payload_validation_invalid(self):
        invalid_payload1 = {'value': 25.4} # missing field_id
        self.assertFalse(self.cmd._validate_payload(invalid_payload1))

        invalid_payload2 = {'field_id': self.field.id, 'random_key': 'hello'} # no value or known sensor key
        self.assertFalse(self.cmd._validate_payload(invalid_payload2))

    def test_save_to_db(self):
        topic = f"farm/{self.field.id}/sensor/temperature"
        raw_data = {'field_id': self.field.id, 'value': 28.5}
        
        self.cmd._save_to_db(self.field.id, 'temperature', 28.5, topic, raw_data)
        
        reading = SensorReading.objects.filter(field=self.field, sensor_type='temperature').first()
        self.assertIsNotNone(reading)
        self.assertEqual(float(reading.value), 28.5)
        self.assertEqual(reading.topic, topic)
        self.assertTrue(reading.is_valid)
