"""
Sensör okuma analitiği — Django ORM ile tarih aralığı ve sensör tipi aggregasyonları.

PostgreSQL'de composite index (sensor_id, measured_at) ve aylık partitioning ile
optimize edilmiş sorgular kullanır.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Sequence

from django.db import connection
from django.db.models import Avg, Count, Max, Min, QuerySet
from django.db.models.functions import Coalesce

from apps.iot.models import SensorReading


@dataclass(frozen=True)
class SensorTypeAggregate:
    """Sensör tipi bazında özet istatistikler."""

    sensor_type: str
    avg_value: Decimal | None
    min_value: Decimal | None
    max_value: Decimal | None
    reading_count: int


@dataclass(frozen=True)
class SensorAggregate:
    """Tek sensör için özet istatistikler."""

    sensor_id: str
    sensor_type: str
    avg_value: Decimal | None
    min_value: Decimal | None
    max_value: Decimal | None
    reading_count: int


class SensorAnalyticsService:
    """Yüksek frekanslı sensör verisi analitik sorguları."""

    @staticmethod
    def base_queryset(
        *,
        start: datetime,
        end: datetime,
        sensor_types: Sequence[str] | None = None,
        field_id: int | None = None,
        sensor_ids: Sequence[str] | None = None,
    ) -> QuerySet[SensorReading]:
        """Tarih aralığı ve filtrelerle temel queryset."""
        qs = SensorReading.objects.filter(
            measured_at__gte=start,
            measured_at__lt=end,
        ).select_related('sensor')

        if sensor_types:
            qs = qs.filter(sensor__sensor_type__in=sensor_types)
        if field_id is not None:
            qs = qs.filter(field_id=field_id)
        if sensor_ids:
            qs = qs.filter(sensor_id__in=sensor_ids)

        return qs

    @classmethod
    def aggregate_by_sensor_type(
        cls,
        *,
        start: datetime,
        end: datetime,
        sensor_types: Sequence[str] | None = None,
        field_id: int | None = None,
    ) -> list[SensorTypeAggregate]:
        """
        Sensör tipine göre avg / min / max.

        Örnek SQL (ORM üretimi):
        SELECT s.sensor_type, AVG(r.value), MIN(r.value), MAX(r.value), COUNT(*)
        FROM iot_sensorreading r
        JOIN iot_sensor s ON r.sensor_id = s.id
        WHERE r.measured_at >= %s AND r.measured_at < %s
        GROUP BY s.sensor_type;
        """
        qs = cls.base_queryset(
            start=start,
            end=end,
            sensor_types=sensor_types,
            field_id=field_id,
        )
        rows = (
            qs.values('sensor__sensor_type')
            .annotate(
                avg_value=Avg('value'),
                min_value=Min('value'),
                max_value=Max('value'),
                reading_count=Count('id'),
            )
            .order_by('sensor__sensor_type')
        )
        return [
            SensorTypeAggregate(
                sensor_type=row['sensor__sensor_type'],
                avg_value=row['avg_value'],
                min_value=row['min_value'],
                max_value=row['max_value'],
                reading_count=row['reading_count'],
            )
            for row in rows
        ]

    @classmethod
    def aggregate_by_sensor(
        cls,
        *,
        start: datetime,
        end: datetime,
        sensor_types: Sequence[str] | None = None,
        field_id: int | None = None,
    ) -> list[SensorAggregate]:
        """Sensör bazında avg / min / max."""
        qs = cls.base_queryset(
            start=start,
            end=end,
            sensor_types=sensor_types,
            field_id=field_id,
        )
        rows = (
            qs.values('sensor_id', 'sensor__sensor_type')
            .annotate(
                avg_value=Avg('value'),
                min_value=Min('value'),
                max_value=Max('value'),
                reading_count=Count('id'),
            )
            .order_by('sensor__sensor_type', 'sensor_id')
        )
        return [
            SensorAggregate(
                sensor_id=str(row['sensor_id']),
                sensor_type=row['sensor__sensor_type'],
                avg_value=row['avg_value'],
                min_value=row['min_value'],
                max_value=row['max_value'],
                reading_count=row['reading_count'],
            )
            for row in rows
        ]

    @classmethod
    def global_aggregate(
        cls,
        *,
        start: datetime,
        end: datetime,
        sensor_types: Sequence[str] | None = None,
        field_id: int | None = None,
    ) -> dict[str, Any]:
        """Filtrelenmiş tüm okumalar için tek satır özet."""
        qs = cls.base_queryset(
            start=start,
            end=end,
            sensor_types=sensor_types,
            field_id=field_id,
        )
        return qs.aggregate(
            avg_value=Coalesce(Avg('value'), Decimal('0')),
            min_value=Min('value'),
            max_value=Max('value'),
            reading_count=Count('id'),
        )

    @staticmethod
    def explain_queryset(
        queryset: QuerySet,
        *,
        analyze: bool = True,
        buffers: bool = True,
    ) -> str:
        """
        QuerySet için EXPLAIN (ANALYZE) çıktısını döndürür.

        PostgreSQL: EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
        SQLite: EXPLAIN QUERY PLAN
        """
        sql, params = queryset.query.sql_with_params()
        prefix = 'EXPLAIN '
        if connection.vendor == 'postgresql':
            options = ['FORMAT TEXT']
            if analyze:
                options.insert(0, 'ANALYZE')
            if buffers and analyze:
                options.insert(0, 'BUFFERS')
            prefix += f"({', '.join(options)}) "
        elif connection.vendor == 'sqlite':
            prefix = 'EXPLAIN QUERY PLAN '

        with connection.cursor() as cursor:
            cursor.execute(f'{prefix}{sql}', params)
            rows = cursor.fetchall()

        return '\n'.join(
            row[0] if len(row) == 1 else ' | '.join(str(c) for c in row)
            for row in rows
        )

    @staticmethod
    def raw_aggregate_by_sensor_type_sql(
        start: datetime,
        end: datetime,
        sensor_types: Sequence[str] | None = None,
    ) -> str:
        """Referans analitik SQL (dokümantasyon / benchmark)."""
        type_filter = ''
        if sensor_types:
            types = ', '.join(f"'{t}'" for t in sensor_types)
            type_filter = f'AND s.sensor_type IN ({types})'

        return f"""
SELECT
    s.sensor_type,
    AVG(r.value)   AS avg_value,
    MIN(r.value)   AS min_value,
    MAX(r.value)   AS max_value,
    COUNT(*)       AS reading_count
FROM sensor_readings r
INNER JOIN iot_sensor s ON s.id = r.sensor_id
WHERE r.timestamp >= %(start)s
  AND r.timestamp < %(end)s
  {type_filter}
GROUP BY s.sensor_type
ORDER BY s.sensor_type;
""".strip()
