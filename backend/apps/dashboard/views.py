"""
Dashboard views — Ana sayfa ve özet bilgiler.
"""

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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
    fields = Field.objects.filter(owner=request.user)
    context = {
        'fields': fields,
    }
    return render(request, 'dashboard/realtime.html', context)
