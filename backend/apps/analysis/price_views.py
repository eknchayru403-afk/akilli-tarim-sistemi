"""Price views — Ürün fiyatları listesi."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import CropPrice


@login_required
def price_list(request):
    """Ürün fiyat tablosunu gösterir."""
    prices = CropPrice.objects.all()
    return render(request, 'prices/list.html', {'prices': prices})
