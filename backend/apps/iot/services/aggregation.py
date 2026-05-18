"""Sensör okumalarını SoilAnalysis kaydına dönüştürür."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg
from django.utils import timezone

from apps.analysis.models import SoilAnalysis
from apps.fields.models import Field
from apps.iot.models import SensorReading


SENSOR_TO_SOIL_FIELD = {
    'nem': 'humidity',
    'toprak_nemi': 'humidity',
    'sicaklik': 'temperature',
    'ph': 'ph',
    'yagis': 'rainfall',
}


def aggregate_field_readings(
    field: Field,
    *,
    hours: int = 24,
    source: str = 'mqtt',
) -> SoilAnalysis | None:
    """
    Son N saatteki sensör ortalamalarından SoilAnalysis oluşturur.

    N, P, K sensörü yoksa CSV/simülasyon varsayılanları kullanılmaz; eksik alanlar 0.
    """
    since = timezone.now() - timedelta(hours=hours)
    aggregates: dict[str, Decimal] = {}

    for sensor_type, soil_field in SENSOR_TO_SOIL_FIELD.items():
        avg = (
            SensorReading.objects.filter(
                sensor__field=field,
                sensor__sensor_type=sensor_type,
                measured_at__gte=since,
            ).aggregate(avg=Avg('value'))['avg']
        )
        if avg is not None:
            aggregates[soil_field] = Decimal(str(round(avg, 2)))

    if not aggregates:
        return None

    return SoilAnalysis.objects.create(
        field=field,
        nitrogen=aggregates.get('nitrogen', Decimal('0')),
        phosphorus=aggregates.get('phosphorus', Decimal('0')),
        potassium=aggregates.get('potassium', Decimal('0')),
        temperature=aggregates.get('temperature', Decimal('25')),
        humidity=aggregates.get('humidity', Decimal('50')),
        ph=aggregates.get('ph', Decimal('6.5')),
        rainfall=aggregates.get('rainfall', Decimal('0')),
        source=source,
    )
