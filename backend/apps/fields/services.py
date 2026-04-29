"""
Fields servisleri — Tarla bazlı gelir tahmini.

Performans iyileştirmeleri:
- CropPrice tablosu Django cache ile önbelleklenir (N+1 → O(1) dict lookup).
- for döngüsündeki CropPrice.objects.get() çağrıları kaldırıldı.
- Fiyat verisi dict'e dönüştürülüp bellekte tutulur.
"""

import logging

from django.conf import settings
from django.core.cache import cache

from apps.analysis.models import CropPrice, CropRecommendation, SoilAnalysis
from ml.constants import TURKEY_CROPS_TR_TO_EN

logger = logging.getLogger(__name__)

# Önbellek anahtarı
_CACHE_KEY_PRICES = 'crop_prices_dict'


class RevenueService:
    """Tarla bazlı tahmini gelir hesaplama servisi."""

    @staticmethod
    def _get_prices_dict() -> dict:
        """
        CropPrice tablosundaki tüm verileri crop_name → dict olarak döndürür.

        Önbellek kullanır: ilk çağrıda DB'den yükler, sonrakilerinde cache'ten alır.
        Bu sayede for döngüsündeki N adet SELECT sorgusu → tek bir sorgu + dict lookup'a düşer.

        Returns:
            {crop_name: {'price_per_kg': float, 'avg_yield_per_hectare': float, 'crop_name_tr': str}}
        """
        prices_dict = cache.get(_CACHE_KEY_PRICES)
        if prices_dict is not None:
            return prices_dict

        prices_dict = {}
        for p in CropPrice.objects.all():
            prices_dict[p.crop_name] = {
                'price_per_kg': float(p.price_per_kg),
                'avg_yield_per_hectare': float(p.avg_yield_per_hectare),
                'crop_name_tr': p.crop_name_tr,
            }

        cache.set(
            _CACHE_KEY_PRICES,
            prices_dict,
            getattr(settings, 'CACHE_TTL_PRICES', 1800),
        )
        logger.debug("CropPrice cache yüklendi: %d ürün", len(prices_dict))
        return prices_dict

    @staticmethod
    def invalidate_price_cache() -> None:
        """Fiyat önbelleğini temizler. Admin fiyat güncellemesinden sonra çağrılmalı."""
        cache.delete(_CACHE_KEY_PRICES)
        logger.debug("CropPrice cache temizlendi")

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

        Optimizasyon:
            Fiyat verisi önbellekten dict olarak alınır → O(1) lookup.
            for döngüsündeki CropPrice.objects.get() tamamen kaldırıldı.

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

        # Fiyat dict'ini önbellekten al (tek sorgu veya cache hit)
        prices_dict = RevenueService._get_prices_dict()
        if not prices_dict:
            return result

        result['has_data'] = True

        # ── 1) Ekili tarla → mevcut ürün geliri ──
        if field.status == 'planted' and field.current_crop:
            crop_tr = field.current_crop
            crop_en = TURKEY_CROPS_TR_TO_EN.get(crop_tr, '')

            price_data = prices_dict.get(crop_en)
            if price_data:
                yield_kg = round(price_data['avg_yield_per_hectare'] * area_hectare, 1)
                revenue = round(yield_kg * price_data['price_per_kg'], 2)
                yield_per_decar = round(price_data['avg_yield_per_hectare'] / 10, 1)

                result['current_crop'] = {
                    'crop_name_tr': crop_tr,
                    'crop_name': crop_en,
                    'price_per_kg': price_data['price_per_kg'],
                    'yield_per_decar': yield_per_decar,
                    'total_yield_kg': yield_kg,
                    'total_revenue': revenue,
                }

        # ── 2) Son analiz önerileri → detaylı gelir ──
        last_analysis = SoilAnalysis.objects.filter(
            field=field,
        ).order_by('-created_at').only('id', 'created_at').first()

        if last_analysis:
            recs = CropRecommendation.objects.filter(
                analysis=last_analysis,
            ).order_by('rank').only(
                'rank', 'crop_name', 'crop_name_tr', 'confidence',
            )

            for rec in recs:
                price_data = prices_dict.get(rec.crop_name)
                if not price_data:
                    continue

                yield_kg = round(price_data['avg_yield_per_hectare'] * area_hectare, 1)
                revenue = round(yield_kg * price_data['price_per_kg'], 2)
                yield_per_decar = round(price_data['avg_yield_per_hectare'] / 10, 1)

                result['recommendations'].append({
                    'rank': rec.rank,
                    'crop_name_tr': rec.crop_name_tr,
                    'crop_name': rec.crop_name,
                    'confidence': float(rec.confidence),
                    'price_per_kg': price_data['price_per_kg'],
                    'yield_per_decar': yield_per_decar,
                    'total_yield_kg': yield_kg,
                    'total_revenue': revenue,
                })

        # ── 3) Tüm ürünler genel karşılaştırma (dict'ten — ek sorgu yok) ──
        for crop_name, p in prices_dict.items():
            yield_kg = round(p['avg_yield_per_hectare'] * area_hectare, 1)
            revenue = round(yield_kg * p['price_per_kg'], 2)
            yield_per_decar = round(p['avg_yield_per_hectare'] / 10, 1)

            result['all_crops'].append({
                'crop_name_tr': p['crop_name_tr'],
                'crop_name': crop_name,
                'price_per_kg': p['price_per_kg'],
                'yield_per_decar': yield_per_decar,
                'total_yield_kg': yield_kg,
                'total_revenue': revenue,
            })

        # Gelire göre sırala
        result['all_crops'].sort(key=lambda x: x['total_revenue'], reverse=True)

        return result
