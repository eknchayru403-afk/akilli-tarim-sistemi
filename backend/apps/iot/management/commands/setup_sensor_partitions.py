"""Aylık sensör okuma partition'larını oluşturur (PostgreSQL)."""

from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """PostgreSQL'de aylık RANGE partition kurulumu."""

    help = (
        'iot_sensorreading için aylık partition oluşturur. '
        '--convert ile mevcut tabloyu partitioned yapıya dönüştürür (tek seferlik).'
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--convert',
            action='store_true',
            help='Mevcut tabloyu PARTITION BY RANGE (measured_at) yapısına dönüştür',
        )
        parser.add_argument(
            '--months-ahead',
            type=int,
            default=6,
            help='İleriye doğru oluşturulacak ay sayısı (varsayılan: 6)',
        )

    def handle(self, *args, **options) -> None:
        if connection.vendor != 'postgresql':
            self.stderr.write(self.style.ERROR('Bu komut yalnızca PostgreSQL ile çalışır.'))
            return

        sql_dir = Path(__file__).resolve().parents[2] / 'sql' / 'postgresql'

        if options['convert']:
            self.stdout.write('sensor_readings partitioned yapıya dönüştürülüyor...')
            sql = (sql_dir / 'convert_to_partitioned.sql').read_text(encoding='utf-8')
            with connection.cursor() as cursor:
                cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS('Dönüşüm tamamlandı.'))
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT sr_ensure_monthly_partitions(%s);',
                    [options['months_ahead']],
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Partition'lar güncellendi (geçmiş 2 ay + ileri {options['months_ahead']} ay).",
                ),
            )
