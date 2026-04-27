"""
Fields views — Tarla CRUD işlemleri.
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
    fields = Field.objects.filter(user=request.user)
    return render(request, 'fields/list.html', {'fields': fields})


@login_required
def field_detail(request, pk: int):
    """Tarla detay sayfası."""
    field = get_object_or_404(Field, pk=pk, user=request.user)
    analyses = SoilAnalysis.objects.filter(field=field)[:5]
    care_recs = CareRecommendation.objects.filter(field=field, is_done=False)

    # Tarla bazlı gelir tahmini
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
        return redirect('fields:list')

    return render(request, 'fields/confirm_delete.html', {'field': field})
