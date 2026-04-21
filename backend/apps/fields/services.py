"""
Fields servisleri — Tarla bazlı gelir tahmini.
"""

import json
import logging
from pathlib import Path

from django.conf import settings

from apps.analysis.models import CropPrice, CropRecommendation, SoilAnalysis
from ml.constants import TURKEY_CROPS, TURKEY_CROPS_TR_TO_EN

logger = logging.getLogger(__name__)


class RevenueService:
    """Tarla bazlı tahmini gelir hesaplama servisi."""

    @staticmethod
    def get_field_revenue(field) -> dict:
        """
        Tarla için tahmini gelir bilgisi hesaplar.

        - Ekili tarla → mevcut ürün için gelir tahmini
        - Boş tarla → son analizin top önerileri için gelir karşılaştırması
        - Analiz yok → tüm ürünlerin genel gelir karşılaştırması

        Hesaplama:
            verim_kg = (alan_dekar / 10) × hektar_verim
            gelir_tl = verim_kg × fiyat_tl_kg

        Args:
            field: Field nesnesi.

        Returns:
            {
              'has_data': bool,
              'current_crop': dict | None,   # ekili ürün geliri
              'recommendations': list[dict],  # öneri bazlı gelirler
              'all_crops': list[dict],         # tüm ürün karşılaştırması
            }
        """
        area_decar = float(field.area_decar)
        area_hectare = area_decar / 10

        result = {
            'has_data': False,
            'current_crop': None,
            'recommendations': [],
            'all_crops': [],
            'area_decar': area_decar,
        }

        # Fiyat verisi yoksa boş döner
        prices = CropPrice.objects.all()
        if not prices.exists():
            return result

        result['has_data'] = True

        # ── 1) Ekili tarla → mevcut ürün geliri ──
        if field.status == 'planted' and field.current_crop:
            crop_tr = field.current_crop
            crop_en = TURKEY_CROPS_TR_TO_EN.get(crop_tr, '')

            try:
                price_obj = CropPrice.objects.get(crop_name=crop_en) if crop_en else None
            except CropPrice.DoesNotExist:
                price_obj = None

            if price_obj:
                yield_kg = round(float(price_obj.avg_yield_per_hectare) * area_hectare, 1)
                revenue = round(yield_kg * float(price_obj.price_per_kg), 2)
                yield_per_decar = round(float(price_obj.avg_yield_per_hectare) / 10, 1)

                result['current_crop'] = {
                    'crop_name_tr': crop_tr,
                    'crop_name': crop_en,
                    'price_per_kg': float(price_obj.price_per_kg),
                    'yield_per_decar': yield_per_decar,
                    'total_yield_kg': yield_kg,
                    'total_revenue': revenue,
                }

        # ── 2) Son analiz önerileri → detaylı gelir ──
        last_analysis = SoilAnalysis.objects.filter(
            field=field,
        ).order_by('-created_at').first()

        if last_analysis:
            recs = CropRecommendation.objects.filter(
                analysis=last_analysis,
            ).order_by('rank')

            for rec in recs:
                try:
                    price_obj = CropPrice.objects.get(crop_name=rec.crop_name)
                except CropPrice.DoesNotExist:
                    continue

                yield_kg = round(float(price_obj.avg_yield_per_hectare) * area_hectare, 1)
                revenue = round(yield_kg * float(price_obj.price_per_kg), 2)
                yield_per_decar = round(float(price_obj.avg_yield_per_hectare) / 10, 1)

                result['recommendations'].append({
                    'rank': rec.rank,
                    'crop_name_tr': rec.crop_name_tr,
                    'crop_name': rec.crop_name,
                    'confidence': float(rec.confidence),
                    'price_per_kg': float(price_obj.price_per_kg),
                    'yield_per_decar': yield_per_decar,
                    'total_yield_kg': yield_kg,
                    'total_revenue': revenue,
                })

        # ── 3) Tüm ürünler genel karşılaştırma ──
        for p in prices:
            yield_kg = round(float(p.avg_yield_per_hectare) * area_hectare, 1)
            revenue = round(yield_kg * float(p.price_per_kg), 2)
            yield_per_decar = round(float(p.avg_yield_per_hectare) / 10, 1)

            result['all_crops'].append({
                'crop_name_tr': p.crop_name_tr,
                'crop_name': p.crop_name,
                'price_per_kg': float(p.price_per_kg),
                'yield_per_decar': yield_per_decar,
                'total_yield_kg': yield_kg,
                'total_revenue': revenue,
            })

        # Gelire göre sırala
        result['all_crops'].sort(key=lambda x: x['total_revenue'], reverse=True)

        return result
