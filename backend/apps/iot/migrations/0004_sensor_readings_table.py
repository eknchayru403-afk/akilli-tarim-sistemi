# sensor_readings tablosu, field_id denormalizasyonu, timestamp kolon adı

import django.db.models.deletion
from django.db import migrations, models


def backfill_field_id(apps, schema_editor) -> None:
    SensorReading = apps.get_model('iot', 'SensorReading')
    for reading in SensorReading.objects.select_related('sensor').iterator(chunk_size=500):
        if reading.field_id is None:
            reading.field_id = reading.sensor.field_id
            reading.save(update_fields=['field_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('fields', '0002_field_idx_field_user_status_and_more'),
        ('iot', '0003_postgresql_brin_and_partition_helpers'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensorreading',
            name='field',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sensor_readings',
                to='fields.field',
                verbose_name='Tarla',
                db_column='field_id',
            ),
        ),
        migrations.RunPython(backfill_field_id, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='sensorreading',
            name='field',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sensor_readings',
                to='fields.field',
                verbose_name='Tarla',
                db_column='field_id',
            ),
        ),
        migrations.AlterModelTable(
            name='sensorreading',
            table='sensor_readings',
        ),
        migrations.AlterField(
            model_name='sensorreading',
            name='measured_at',
            field=models.DateTimeField(
                db_column='timestamp',
                db_index=False,
                verbose_name='Ölçüm Zamanı',
            ),
        ),
        migrations.RemoveIndex(
            model_name='sensorreading',
            name='idx_reading_sensor_measured_at',
        ),
        migrations.RemoveIndex(
            model_name='sensorreading',
            name='idx_reading_measured_sensor',
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(
                fields=['field', 'measured_at'],
                name='idx_sr_field_timestamp',
            ),
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(
                fields=['sensor', 'measured_at'],
                name='idx_sr_sensor_timestamp',
            ),
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(
                fields=['measured_at', 'field'],
                name='idx_sr_timestamp_field',
            ),
        ),
    ]
