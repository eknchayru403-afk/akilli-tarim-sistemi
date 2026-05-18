"""PostgreSQL: BRIN index ve aylık partition yardımcı fonksiyonları."""

from pathlib import Path

from django.db import connection, migrations


def _sql_path(name: str) -> str:
    base = Path(__file__).resolve().parent.parent / 'sql' / 'postgresql'
    return (base / name).read_text(encoding='utf-8')


def apply_brin(apps, schema_editor) -> None:
    if connection.vendor != 'postgresql':
        return
    schema_editor.execute(_sql_path('brin_measured_at.sql'))


def apply_partition_helpers(apps, schema_editor) -> None:
    if connection.vendor != 'postgresql':
        return
    schema_editor.execute(_sql_path('partition_monthly.sql'))


def reverse_brin(apps, schema_editor) -> None:
    if connection.vendor != 'postgresql':
        return
    schema_editor.execute('DROP INDEX IF EXISTS idx_reading_measured_at_brin;')


def reverse_partition_helpers(apps, schema_editor) -> None:
    if connection.vendor != 'postgresql':
        return
    schema_editor.execute('DROP FUNCTION IF EXISTS iot_ensure_sensor_reading_partitions(INT);')
    schema_editor.execute('DROP FUNCTION IF EXISTS iot_create_sensor_reading_partition(DATE);')


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0002_sensorreading_composite_indexes'),
    ]

    operations = [
        migrations.RunPython(apply_brin, reverse_brin),
        migrations.RunPython(apply_partition_helpers, reverse_partition_helpers),
    ]
