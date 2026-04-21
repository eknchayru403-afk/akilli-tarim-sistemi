"""Management command: load_prices — Fiyat ve verim verilerini DB'ye yükler."""

import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.analysis.models import CropPrice
from ml.constants import TURKEY_CROPS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """prices.json ve yield_data.json verilerini CropPrice tablosuna yükler."""

    help = 'Ürün fiyatları ve verim verilerini JSON dosyalarından veritabanına yükler.'

    def handle(self, *args, **options) -> None:
        """Fiyat verilerini yükle."""
        prices_path = settings.DATA_DIR / 'prices.json'
        yields_path = settings.DATA_DIR / 'yield_data.json'

        with open(prices_path, 'r', encoding='utf-8') as f:
            prices = json.load(f)

        with open(yields_path, 'r', encoding='utf-8') as f:
            yields = json.load(f)

        created_count = 0
        updated_count = 0

        for crop_en, price_data in prices.items():
            crop_tr = TURKEY_CROPS.get(crop_en, price_data.get('label_tr', crop_en))
            avg_yield = yields.get(crop_en, 0)

            obj, created = CropPrice.objects.update_or_create(
                crop_name=crop_en,
                defaults={
                    'crop_name_tr': crop_tr,
                    'price_per_kg': price_data['fiyat_tl_kg'],
                    'avg_yield_per_hectare': avg_yield,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Fiyat verisi yüklendi: {created_count} yeni, {updated_count} güncellendi.'
            )
        )
