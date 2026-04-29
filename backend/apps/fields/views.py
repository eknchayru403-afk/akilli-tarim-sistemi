"""
Fields views — Tarla CRUD işlemleri.

Performans iyileştirmeleri:
- field_list: select_related kaldırıldı (user zaten filtre, template'te erişilmiyor)
- field_detail: select_related('user') + prefetch_related eklendi
- field_create/update/delete: Dashboard cache invalidation eklendi
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.analysis.models import CareRecommendation, SoilAnalysis

from .forms import FieldForm
from .models import Field
from .services import RevenueService

logger = logging.getLogger(__name__)


@login_required
def field_list(request):
    """Kullanıcının tarlalarını listeler."""
    fields = Field.objects.filter(user=request.user).only(
        'id', 'name', 'location', 'area_decar', 'soil_type',
        'status', 'current_crop', 'created_at',
    )
    return render(request, 'fields/list.html', {'fields': fields})


@login_required
def field_detail(request, pk: int):
    """Tarla detay sayfası."""
    field = get_object_or_404(
        Field.objects.select_related('user'),
        pk=pk,
        user=request.user,
    )

    # Son 5 analiz — select_related ile field erişimi optimize
    analyses = SoilAnalysis.objects.filter(
        field=field,
    ).select_related('field').prefetch_related('recommendations')[:5]

    # Aktif bakım tavsiyeleri
    care_recs = CareRecommendation.objects.filter(
        field=field,
        is_done=False,
    ).order_by('-priority', '-created_at')

    # Tarla bazlı gelir tahmini (cache'li fiyat verisi kullanır)
    revenue = RevenueService.get_field_revenue(field)

    return render(request, 'fields/detail.html', {
        'field': field,
        'analyses': analyses,
        'care_recommendations': care_recs,
        'revenue': revenue,
    })


@login_required
def field_create(request):
    """Yeni tarla oluşturma."""
    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            field = form.save(commit=False)
            field.user = request.user
            field.save()
            messages.success(request, f'"{field.name}" tarlası oluşturuldu.')
            logger.info("Tarla oluşturuldu: %s (user: %s)", field.name, request.user)

            # Dashboard cache'i temizle
            _invalidate_dashboard(request.user)

            return redirect('fields:detail', pk=field.pk)
    else:
        form = FieldForm()

    return render(request, 'fields/form.html', {
        'form': form,
        'title': 'Yeni Tarla Ekle',
    })


@login_required
def field_update(request, pk: int):
    """Tarla güncelleme."""
    field = get_object_or_404(Field, pk=pk, user=request.user)

    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{field.name}" güncellendi.')

            # Dashboard cache'i temizle
            _invalidate_dashboard(request.user)

            return redirect('fields:detail', pk=field.pk)
    else:
        form = FieldForm(instance=field)

    return render(request, 'fields/form.html', {
        'form': form,
        'title': f'{field.name} — Düzenle',
        'field': field,
    })


@login_required
def field_delete(request, pk: int):
    """Tarla silme."""
    field = get_object_or_404(Field, pk=pk, user=request.user)

    if request.method == 'POST':
        name = field.name
        field.delete()
        messages.success(request, f'"{name}" tarlası silindi.')
        logger.info("Tarla silindi: %s (user: %s)", name, request.user)

        # Dashboard cache'i temizle
        _invalidate_dashboard(request.user)

        return redirect('fields:list')

    return render(request, 'fields/confirm_delete.html', {'field': field})


def _invalidate_dashboard(user) -> None:
    """Dashboard cache'ini temizler."""
    from apps.dashboard.services import DashboardService
    DashboardService.invalidate_cache(user)
