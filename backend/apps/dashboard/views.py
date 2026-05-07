"""
Dashboard views — Ana sayfa ve özet bilgiler.
"""

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from apps.fields.models import Field

from .services import DashboardService

logger = logging.getLogger(__name__)


@login_required
def index(request):
    """Dashboard ana sayfa."""
    context = DashboardService.get_dashboard_data(request.user)
    return render(request, 'dashboard/index.html', context)

@login_required
def realtime_dashboard(request):
    """Gerçek zamanlı sensör izleme panosu."""
    fields = Field.objects.filter(user=request.user)
    context = {
        'fields': fields,
    }
    return render(request, 'dashboard/realtime.html', context)

@login_required
def api_realtime_data(request):
    """Tarla verilerinin ilk yüklemesi (Geçmiş veya anlık simüle değerler)"""
    fields = Field.objects.filter(user=request.user)
    data = []
    import random
    for field in fields:
        data.append({
            'field_id': field.id,
            'name': field.name,
            'soil_moisture': round(random.uniform(30.0, 70.0), 1), # Simulated
            'air_temperature': round(random.uniform(20.0, 30.0), 1),
            'ph_level': round(random.uniform(6.0, 7.5), 1),
            'irrigation_status': random.choice([0, 1])
        })
    return JsonResponse({'status': 'success', 'data': data})
