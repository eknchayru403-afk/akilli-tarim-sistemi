"""
Price views — Ürün fiyatları listesi.

Performans iyileştirmeleri:
- Fiyat listesi Django cache ile önbelleklenir (seyrek değişen referans veri).
"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render

from .models import CropPrice

_CACHE_KEY_PRICE_LIST = 'price_list_queryset'


@login_required
def price_list(request):
    """Ürün fiyat tablosunu gösterir."""
    prices = cache.get(_CACHE_KEY_PRICE_LIST)
    if prices is None:
        prices = list(CropPrice.objects.all())
        cache.set(
            _CACHE_KEY_PRICE_LIST,
            prices,
            getattr(settings, 'CACHE_TTL_PRICES', 1800),
        )
    return render(request, 'prices/list.html', {'prices': prices})
