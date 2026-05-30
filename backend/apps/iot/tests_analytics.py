"""Sensör analitik servisi testleri."""

import uuid
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.fields.models import Field
from apps.iot.models import Sensor, SensorReading
from apps.iot.services.analytics import SensorAnalyticsService


class SensorAnalyticsServiceTests(TestCase):
    """ORM analitik aggregasyon testleri."""

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username='analytics_user',
            password='test-pass-123',
        )
        self.field = Field.objects.create(
            user=self.user,
            name='Analitik Tarla',
            area_decar=Decimal('10'),
        )
        self.sensor_nem = Sensor.objects.create(
            field=self.field,
            name='Nem',
            sensor_type='toprak_nemi',
        )
        self.sensor_ph = Sensor.objects.create(
            field=self.field,
            name='pH',
            sensor_type='ph',
        )
        now = timezone.now()
        for i, (sensor, value) in enumerate([
            (self.sensor_nem, Decimal('40')),
            (self.sensor_nem, Decimal('60')),
            (self.sensor_ph, Decimal('6.5')),
        ]):
            SensorReading.objects.create(
                sensor=sensor,
                field=self.field,
                message_id=uuid.uuid4(),
                value=value,
                unit='%',
                raw_payload={'i': i},
                measured_at=now - timedelta(hours=i),
            )

    def test_aggregate_by_sensor_type(self) -> None:
        start = timezone.now() - timedelta(days=1)
        end = timezone.now() + timedelta(hours=1)
        rows = SensorAnalyticsService.aggregate_by_sensor_type(start=start, end=end)
        types = {r.sensor_type: r for r in rows}
        self.assertIn('toprak_nemi', types)
        self.assertEqual(types['toprak_nemi'].reading_count, 2)
        self.assertEqual(types['toprak_nemi'].min_value, Decimal('40'))
        self.assertEqual(types['toprak_nemi'].max_value, Decimal('60'))

    def test_aggregate_filtered_by_type(self) -> None:
        start = timezone.now() - timedelta(days=1)
        end = timezone.now() + timedelta(hours=1)
        rows = SensorAnalyticsService.aggregate_by_sensor_type(
            start=start,
            end=end,
            sensor_types=['ph'],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].sensor_type, 'ph')

    def test_explain_queryset_returns_text(self) -> None:
        start = timezone.now() - timedelta(days=1)
        end = timezone.now() + timedelta(hours=1)
        qs = SensorAnalyticsService.base_queryset(start=start, end=end)
        plan = SensorAnalyticsService.explain_queryset(qs)
        self.assertTrue(len(plan) > 0)
