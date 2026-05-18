# Generated manually for apps.iot

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fields', '0002_field_idx_field_user_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncellenme')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=120, verbose_name='Sensör Adı')),
                ('sensor_type', models.CharField(
                    choices=[
                        ('nem', 'Nem'),
                        ('sicaklik', 'Sıcaklık'),
                        ('ph', 'pH'),
                        ('yagis', 'Yağış'),
                        ('isik', 'Işık'),
                        ('toprak_nemi', 'Toprak Nemi'),
                        ('co2', 'CO₂'),
                        ('ruzgar', 'Rüzgar'),
                    ],
                    max_length=20,
                    verbose_name='Tip',
                )),
                ('location_name', models.CharField(blank=True, max_length=200, verbose_name='Konum')),
                ('status', models.CharField(
                    choices=[
                        ('aktif', 'Aktif'),
                        ('pasif', 'Pasif'),
                        ('baglanti_yok', 'Bağlantı Yok'),
                        ('hata', 'Hata'),
                        ('bakimda', 'Bakımda'),
                    ],
                    default='pasif',
                    max_length=20,
                    verbose_name='Durum',
                )),
                ('mac_address', models.CharField(blank=True, max_length=17, null=True, unique=True, verbose_name='MAC Adresi')),
                ('firmware_version', models.CharField(blank=True, max_length=20, verbose_name='Firmware')),
                ('connection_protocol', models.CharField(default='MQTT', max_length=20, verbose_name='Bağlantı Protokolü')),
                ('provisioning_token', models.CharField(blank=True, max_length=64, null=True, unique=True, verbose_name='Provisioning Token')),
                ('last_reading_at', models.DateTimeField(blank=True, null=True, verbose_name='Son Veri Zamanı')),
                ('field', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sensors',
                    to='fields.field',
                    verbose_name='Tarla',
                )),
            ],
            options={
                'verbose_name': 'Sensör',
                'verbose_name_plural': 'Sensörler',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SensorReading',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('message_id', models.UUIDField(unique=True, verbose_name='Mesaj ID')),
                ('value', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Değer')),
                ('unit', models.CharField(max_length=20, verbose_name='Birim')),
                ('raw_payload', models.JSONField(verbose_name='Ham Veri')),
                ('measured_at', models.DateTimeField(db_index=True, verbose_name='Ölçüm Zamanı')),
                ('received_at', models.DateTimeField(auto_now_add=True, verbose_name='Alınma Zamanı')),
                ('sensor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='readings',
                    to='iot.sensor',
                    verbose_name='Sensör',
                )),
            ],
            options={
                'verbose_name': 'Sensör Okuması',
                'verbose_name_plural': 'Sensör Okumaları',
                'ordering': ['-measured_at'],
            },
        ),
        migrations.AddIndex(
            model_name='sensor',
            index=models.Index(fields=['field', 'status'], name='idx_sensor_field_status'),
        ),
        migrations.AddIndex(
            model_name='sensor',
            index=models.Index(fields=['field', 'sensor_type'], name='idx_sensor_field_type'),
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(fields=['sensor', '-measured_at'], name='idx_reading_sensor_time'),
        ),
    ]
