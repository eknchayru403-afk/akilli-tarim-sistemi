"""
EXPLAIN ANALYZE karşılaştırması — sensor_readings partitioning ve indeksler.

PostgreSQL gerekir. Rapor: docs/SENSOR_READINGS_PARTITIONING.md
"""

from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone

from apps.iot.models import SensorReading
from apps.iot.services.analytics import SensorAnalyticsService


class Command(BaseCommand):
    """BRIN vs B-tree ve partition pruning için EXPLAIN ANALYZE raporu üretir."""

    help = 'sensor_readings sorgu planlarını EXPLAIN ANALYZE ile karşılaştırır ve belgeler.'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--output',
            default='docs/SENSOR_READINGS_PARTITIONING.md',
        )
        parser.add_argument(
            '--field-id',
            type=int,
            default=None,
            help='Filtre için örnek field_id',
        )

    def handle(self, *args, **options) -> None:
        if connection.vendor != 'postgresql':
            self.stderr.write(
                self.style.WARNING(
                    'PostgreSQL gerekli. SQLite için: '
                    'DB_ENGINE=django.db.backends.postgresql ve docker compose up postgres',
                ),
            )
            self._write_sqlite_fallback_report(options['output'])
            return

        now = timezone.now()
        start = now - timedelta(days=30)
        end = now

        field_id = options['field_id']
        if field_id is None:
            field_id = (
                SensorReading.objects.order_by('-measured_at')
                .values_list('field_id', flat=True)
                .first()
            )

        partitioned = self._is_partitioned()
        lines = [
            '# sensor_readings — Partitioning ve İndeks Performans Raporu',
            '',
            f'**Tarih:** {now.isoformat()}  ',
            f'**Tablo:** `sensor_readings`  ',
            f'**Partitioned:** {"Evet (RANGE aylık)" if partitioned else "Hayır — setup_sensor_partitions --convert çalıştırın"}  ',
            '',
            '## 1. İndeks stratejisi',
            '',
            '| İndeks | Tür | Sütun(lar) | Kullanım |',
            '|--------|-----|------------|----------|',
            '| `idx_sr_timestamp_brin` | BRIN | `timestamp` | Geniş tarih taraması |',
            '| `idx_sr_field_timestamp_btree` | B-tree | `(field_id, timestamp)` | Tarla + tarih aralığı |',
            '| `idx_sr_field_id_btree` | B-tree | `field_id` | Tarla bazlı filtre |',
            '| `idx_sr_sensor_timestamp` | B-tree | `(sensor_id, timestamp)` | Tek sensör serisi |',
            '',
            '## 2. EXPLAIN ANALYZE karşılaştırması',
            '',
        ]

        scenarios = [
            (
                '2.1 Yalnızca timestamp aralığı (BRIN adayı)',
                SensorReading.objects.filter(
                    measured_at__gte=start,
                    measured_at__lt=end,
                ),
            ),
            (
                f'2.2 field_id={field_id} + timestamp (B-tree composite)',
                SensorReading.objects.filter(
                    field_id=field_id,
                    measured_at__gte=start,
                    measured_at__lt=end,
                ),
            ),
            (
                '2.3 Aggregate: sensör tipi + tarih (JOIN + GROUP BY)',
                SensorReading.objects.filter(
                    measured_at__gte=start,
                    measured_at__lt=end,
                )
                .values('sensor__sensor_type')
                .annotate(
                    avg_value=Avg('value'),
                    min_value=Min('value'),
                    max_value=Max('value'),
                    reading_count=Count('id'),
                ),
            ),
        ]

        for title, qs in scenarios:
            t0 = time.perf_counter()
            if hasattr(qs, 'count') and 'annotate' not in str(qs.query):
                _ = qs.count()
            else:
                _ = list(qs[:100])
            elapsed_ms = (time.perf_counter() - t0) * 1000

            plan = SensorAnalyticsService.explain_queryset(qs, analyze=True, buffers=True)
            lines.extend([
                f'### {title}',
                '',
                f'**Çalışma süresi (yaklaşık):** {elapsed_ms:.2f} ms  ',
                '',
                '```text',
                plan,
                '```',
                '',
            ])

        # ORM servis karşılaştırması
        t0 = time.perf_counter()
        rows = SensorAnalyticsService.aggregate_by_sensor_type(
            start=start, end=end, field_id=field_id,
        )
        svc_ms = (time.perf_counter() - t0) * 1000

        lines.extend([
            '## 3. Django ORM — SensorAnalyticsService',
            '',
            f'**aggregate_by_sensor_type (field_id={field_id}):** {svc_ms:.2f} ms, {len(rows)} grup  ',
            '',
            '## 4. Beklenen plan farkları',
            '',
            '| Senaryo | Partition yok | Partition + BRIN/B-tree |',
            '|---------|---------------|-------------------------|',
            '| Geniş tarih | Seq Scan tüm tablo | Append + partition pruning, BRIN |',
            '| field_id + tarih | Index Scan veya Seq | Bitmap/Index Scan `idx_sr_field_timestamp_btree` |',
            '| Aggregate JOIN | Hash Join büyük | Prune edilmiş partition\'larda Join |',
            '',
            '## 5. Kurulum komutları',
            '',
            '```bash',
            'docker compose up -d postgres',
            'cd backend',
            'set DB_ENGINE=django.db.backends.postgresql',
            'python manage.py migrate',
            'python manage.py setup_sensor_partitions --convert',
            'python manage.py setup_sensor_partitions --months-ahead 12',
            'python manage.py benchmark_sensor_analytics --seed 100000',
            'python manage.py compare_sensor_reading_plans',
            '```',
            '',
        ])

        out = Path(__file__).resolve().parents[5] / options['output']
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text('\n'.join(lines), encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f'Rapor: {out}'))

    def _is_partitioned(self) -> bool:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT relkind = 'p'
                FROM pg_class
                WHERE relname = 'sensor_readings'
                """
            )
            row = cursor.fetchone()
            return bool(row and row[0])

    def _write_sqlite_fallback_report(self, output: str) -> None:
        """PostgreSQL yoksa şablon rapor."""
        out = Path(__file__).resolve().parents[5] / output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            '\n'.join([
                '# sensor_readings — Partitioning Raporu (Şablon)',
                '',
                'Bu rapor PostgreSQL bağlantısı olmadan oluşturuldu.',
                '',
                'Tam EXPLAIN ANALYZE karşılaştırması için:',
                '',
                '```bash',
                'docker compose up -d postgres',
                'DB_ENGINE=django.db.backends.postgresql python manage.py migrate',
                'python manage.py setup_sensor_partitions --convert',
                'python manage.py compare_sensor_reading_plans',
                '```',
                '',
                'Beklenen indeksler: `idx_sr_timestamp_brin`, `idx_sr_field_timestamp_btree`.',
            ]),
            encoding='utf-8',
        )
        self.stdout.write(self.style.SUCCESS(f'Şablon rapor: {out}'))
