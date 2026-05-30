"""Sensör analitik sorgularını çalıştırır; EXPLAIN ANALYZE sonuçlarını belgeler."""

from __future__ import annotations

import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone as dj_tz

from apps.accounts.models import CustomUser
from apps.fields.models import Field
from apps.iot.constants import SENSOR_TYPE_CHOICES
from apps.iot.models import Sensor, SensorReading
from apps.iot.services.analytics import SensorAnalyticsService


class Command(BaseCommand):
    """Benchmark + EXPLAIN ANALYZE raporu üretir."""

    help = 'Sensör analitik ORM sorgularını ölçer ve docs/SENSOR_READING_ANALYTICS.md yazar.'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--seed',
            type=int,
            default=0,
            help='Test için oluşturulacak okuma sayısı (0 = seed yok)',
        )
        parser.add_argument(
            '--output',
            default='docs/SENSOR_READING_ANALYTICS.md',
            help='Rapor dosya yolu (proje köküne göre)',
        )

    def handle(self, *args, **options) -> None:
        seed_count = options['seed']
        if seed_count > 0:
            created = self._seed_readings(seed_count)
            self.stdout.write(f'Seed: {created} okuma oluşturuldu.')

        now = dj_tz.now()
        start = now - timedelta(days=30)
        end = now

        report_lines = [
            '# Sensör Okuma Analitiği — Performans Raporu',
            '',
            f'**Oluşturulma:** {dj_tz.now().isoformat()}  ',
            f'**Veritabanı:** {connection.vendor} ({connection.settings_dict["NAME"]})  ',
            f'**Tarih aralığı:** {start.isoformat()} → {end.isoformat()}  ',
            '',
            '## 1. İndeks ve partitioning',
            '',
            '| Öğe | Açıklama |',
            '|-----|----------|',
            '| `idx_sr_field_timestamp_btree` | B-tree `(field_id, timestamp)` — tarla + zaman |',
            '| `idx_sr_timestamp_brin` | BRIN `(timestamp)` — geniş tarih taraması |',
            '| `idx_sr_sensor_timestamp` | B-tree `(sensor_id, timestamp)` — sensör serisi |',
            "| Aylık partition | `sensor_readings_YYYY_MM` — `setup_sensor_partitions` |",
            '',
            '## 2. Analitik sorgular (Django ORM)',
            '',
        ]

        # Sorgu 1: sensör tipine göre
        t0 = time.perf_counter()
        by_type = SensorAnalyticsService.aggregate_by_sensor_type(
            start=start, end=end,
        )
        elapsed_type = (time.perf_counter() - t0) * 1000

        qs_type = (
            SensorAnalyticsService.base_queryset(start=start, end=end)
            .values('sensor__sensor_type')
            .annotate(
                avg_value=Avg('value'),
                min_value=Min('value'),
                max_value=Max('value'),
                reading_count=Count('id'),
            )
        )
        explain_type = SensorAnalyticsService.explain_queryset(qs_type)

        report_lines.extend([
            '### 2.1 Sensör tipine göre avg / min / max',
            '',
            '```python',
            'SensorAnalyticsService.aggregate_by_sensor_type(start=..., end=...)',
            '```',
            '',
            f'**Süre:** {elapsed_type:.2f} ms  ',
            f'**Satır:** {len(by_type)} sensör tipi  ',
            '',
            '| sensor_type | avg | min | max | count |',
            '|-------------|-----|-----|-----|-------|',
        ])
        for row in by_type:
            report_lines.append(
                f'| {row.sensor_type} | {row.avg_value} | {row.min_value} | '
                f'{row.max_value} | {row.reading_count} |',
            )

        report_lines.extend([
            '',
            '**EXPLAIN:**',
            '',
            '```text',
            explain_type[:4000],
            '```',
            '',
        ])

        # Sorgu 2: tek tip filtresi
        sample_type = SENSOR_TYPE_CHOICES[0][0]
        t1 = time.perf_counter()
        filtered = SensorAnalyticsService.aggregate_by_sensor_type(
            start=start,
            end=end,
            sensor_types=[sample_type],
        )
        elapsed_filtered = (time.perf_counter() - t1) * 1000

        qs_filtered = SensorAnalyticsService.base_queryset(
            start=start, end=end, sensor_types=[sample_type],
        )
        explain_filtered = SensorAnalyticsService.explain_queryset(qs_filtered)

        report_lines.extend([
            f'### 2.2 Filtre: sensor_type = `{sample_type}`',
            '',
            f'**Süre:** {elapsed_filtered:.2f} ms  ',
            '',
            '```text',
            explain_filtered[:3000],
            '```',
            '',
        ])

        # Sorgu 3: global
        t2 = time.perf_counter()
        global_stats = SensorAnalyticsService.global_aggregate(start=start, end=end)
        elapsed_global = (time.perf_counter() - t2) * 1000

        report_lines.extend([
            '### 2.3 Genel özet (tüm tipler)',
            '',
            f'**Süre:** {elapsed_global:.2f} ms  ',
            f'- avg: {global_stats.get("avg_value")}  ',
            f'- min: {global_stats.get("min_value")}  ',
            f'- max: {global_stats.get("max_value")}  ',
            f'- count: {global_stats.get("reading_count")}  ',
            '',
            '## 3. Referans SQL',
            '',
            '```sql',
            SensorAnalyticsService.raw_aggregate_by_sensor_type_sql(start, end),
            '```',
            '',
            '## 4. Komutlar',
            '',
            '```bash',
            'python manage.py setup_sensor_partitions --months-ahead 6',
            'python manage.py setup_sensor_partitions --convert  # tek seferlik PG dönüşüm',
            'python manage.py benchmark_sensor_analytics --seed 50000',
            '```',
            '',
        ])

        # backend/apps/iot/management/commands -> proje kökü
        project_root = Path(__file__).resolve().parents[5]
        out_path = project_root / options['output']
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text('\n'.join(report_lines), encoding='utf-8')

        self.stdout.write(self.style.SUCCESS(f'Rapor yazıldı: {out_path}'))

    def _seed_readings(self, count: int) -> int:
        user, _ = CustomUser.objects.get_or_create(
            username='bench_sensor',
            defaults={'email': 'bench@ats.local'},
        )
        if not user.has_usable_password():
            user.set_password('bench-pass')
            user.save()

        field, _ = Field.objects.get_or_create(
            user=user,
            name='Benchmark Tarla',
            defaults={'area_decar': Decimal('10')},
        )

        sensors = []
        for tip, _ in SENSOR_TYPE_CHOICES[:4]:
            sensor, _ = Sensor.objects.get_or_create(
                field=field,
                name=f'Bench {tip}',
                defaults={'sensor_type': tip, 'status': 'aktif'},
            )
            sensors.append(sensor)

        now = datetime.now(timezone.utc)
        batch = []
        for i in range(count):
            sensor = random.choice(sensors)
            measured = now - timedelta(
                days=random.randint(0, 60),
                seconds=random.randint(0, 86400),
            )
            batch.append(
                SensorReading(
                    sensor=sensor,
                    field=field,
                    message_id=uuid.uuid4(),
                    value=Decimal(str(round(random.uniform(10, 90), 4))),
                    unit='%',
                    raw_payload={'seed': True, 'i': i},
                    measured_at=measured,
                ),
            )
            if len(batch) >= 2000:
                SensorReading.objects.bulk_create(batch, ignore_conflicts=True)
                batch = []

        if batch:
            SensorReading.objects.bulk_create(batch, ignore_conflicts=True)

        return count
