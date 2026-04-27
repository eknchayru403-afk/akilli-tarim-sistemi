"""
Analysis views — Toprak analizi, simülasyon ve sonuç görüntüleme.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.fields.models import Field

from .forms import SoilAnalysisForm
from .models import CropRecommendation, SoilAnalysis
from .services import AnalysisService, CareAdvisor, SimulationService

logger = logging.getLogger(__name__)


@login_required
def analyze_form(request, field_pk: int):
    """Manuel toprak analizi formu ve işleme."""
    field = get_object_or_404(Field, pk=field_pk, user=request.user)

    if request.method == 'POST':
        form = SoilAnalysisForm(request.POST)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.field = field
            analysis.source = 'manual'
            analysis.save()

            # ML analizi çalıştır
            recommendations = AnalysisService.run_analysis(analysis)

            # Bakım tavsiyeleri üret
            CareAdvisor.generate_recommendations(field, analysis)

            if recommendations:
                messages.success(request, 'Analiz tamamlandı! Ürün önerileri hazır.')
                return redirect('analysis:result', pk=analysis.pk)
            else:
                messages.warning(request, 'ML modeli henüz eğitilmemiş. Lütfen önce modeli eğitin.')
                return redirect('fields:detail', pk=field.pk)
    else:
        form = SoilAnalysisForm()

    return render(request, 'analysis/form.html', {
        'form': form,
        'field': field,
    })


@login_required
def simulate_data(request, field_pk: int):
    """CSV'den otomatik simülasyon verisi üretir ve analiz yapar."""
    field = get_object_or_404(Field, pk=field_pk, user=request.user)

    if request.method == 'POST':
        # Simülasyon
        analysis = SimulationService.simulate_sensor_data(field)

        # ML analizi
        recommendations = AnalysisService.run_analysis(analysis)

        # Bakım tavsiyeleri
        CareAdvisor.generate_recommendations(field, analysis)

        if recommendations:
            messages.success(request, 'Simülasyon tamamlandı! Veriler analiz edildi.')
            return redirect('analysis:result', pk=analysis.pk)
        else:
            messages.warning(request, 'ML modeli henüz eğitilmemiş.')
            return redirect('fields:detail', pk=field.pk)

    return redirect('fields:detail', pk=field.pk)


@login_required
def analysis_result(request, pk: int):
    """Analiz sonuçlarını görüntüler."""
    analysis = get_object_or_404(SoilAnalysis, pk=pk, field__user=request.user)
    recommendations = CropRecommendation.objects.filter(analysis=analysis)

    return render(request, 'analysis/result.html', {
        'analysis': analysis,
        'recommendations': recommendations,
    })


@login_required
def analysis_history(request):
    """Kullanıcının tüm geçmiş analizlerini listeler."""
    analyses = SoilAnalysis.objects.filter(
        field__user=request.user,
    ).select_related('field').prefetch_related('recommendations')

    return render(request, 'analysis/history.html', {
        'analyses': analyses,
    })


@login_required
def plant_crop(request, analysis_pk: int, rec_pk: int):
    """Seçilen ürünü tarlaya eker (status → planted)."""
    analysis = get_object_or_404(SoilAnalysis, pk=analysis_pk, field__user=request.user)
    recommendation = get_object_or_404(CropRecommendation, pk=rec_pk, analysis=analysis)

    if request.method == 'POST':
        field = analysis.field
        old_crop = field.current_crop
        
        if old_crop and old_crop != recommendation.crop_name_tr:
            msg = f'"{field.name}" tarlasındaki {old_crop} sökülüp yerine {recommendation.crop_name_tr} ekildi!'
        else:
            msg = f'"{field.name}" tarlasına {recommendation.crop_name_tr} ekildi!'
            
        field.status = 'planted'
        field.current_crop = recommendation.crop_name_tr
        field.save()

        messages.success(request, msg)
        return redirect('fields:detail', pk=field.pk)

    return redirect('analysis:result', pk=analysis_pk)
