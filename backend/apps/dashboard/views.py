"""
Dashboard views — Ana sayfa ve özet bilgiler.
"""

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import DashboardService

logger = logging.getLogger(__name__)


@login_required
def index(request):
    """Dashboard ana sayfa."""
    context = DashboardService.get_dashboard_data(request.user)
    return render(request, 'dashboard/index.html', context)
