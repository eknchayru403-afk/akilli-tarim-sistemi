"""PostgreSQL: sensor_readings BRIN/B-tree indeksleri ve güncel partition fonksiyonları."""

from pathlib import Path

from django.db import connection, migrations


def _sql(name: str) -> str:
    return (Path(__file__).resolve().parent.parent / 'sql' / 'postgresql' / name).read_text(
        encoding='utf-8',
    )


def apply_pg_indexes(apps, schema_editor) -> None:
    if connection.vendor != 'postgresql':
        return
    schema_editor.execute(_sql('indexes_sensor_readings.sql'))


def apply_partition_functions(apps, schema_editor) -> None:
    if connection.vendor != 'postgresql':
        return
    schema_editor.execute(_sql('partition_monthly.sql'))


def reverse_pg_indexes(apps, schema_editor) -> None:
    if connection.vendor != 'postgresql':
        return
    schema_editor.execute(
        """
        DROP INDEX IF EXISTS idx_sr_timestamp_brin;
        DROP INDEX IF EXISTS idx_sr_field_timestamp_btree;
        DROP INDEX IF EXISTS idx_sr_field_id_btree;
        """
    )


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0004_sensor_readings_table'),
    ]

    operations = [
        migrations.RunPython(apply_partition_functions, migrations.RunPython.noop),
        migrations.RunPython(apply_pg_indexes, reverse_pg_indexes),
    ]
