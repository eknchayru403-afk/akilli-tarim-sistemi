# Composite indexes for high-frequency sensor readings (sensor_id + measured_at)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='sensorreading',
            name='idx_reading_sensor_time',
        ),
        migrations.AlterField(
            model_name='sensorreading',
            name='measured_at',
            field=models.DateTimeField(db_index=False, verbose_name='Ölçüm Zamanı'),
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(
                fields=['sensor', 'measured_at'],
                name='idx_reading_sensor_measured_at',
            ),
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(
                fields=['measured_at', 'sensor'],
                name='idx_reading_measured_sensor',
            ),
        ),
    ]
