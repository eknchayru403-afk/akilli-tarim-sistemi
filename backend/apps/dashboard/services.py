"""
Dashboard servisleri — Aggregation logic.
"""

import logging

from apps.analysis.models import CareRecommendation, SoilAnalysis
from apps.fields.models import Field
from apps.weather.services import WeatherService

logger = logging.getLogger(__name__)


class DashboardService:
    """Dashboard için veri toplama servisi."""

    @staticmethod
    def get_dashboard_data(user) -> dict:
        """
        Kullanıcı için dashboard verilerini toplar.

        Args:
            user: Mevcut kullanıcı.

        Returns:
            Template context dict.
        """
        fields = Field.objects.filter(user=user)
        total_fields = fields.count()
        empty_fields = fields.filter(status='empty').count()
        planted_fields = fields.filter(status='planted').count()
        total_area = sum(float(f.area_decar) for f in fields)

        # Son analizler
        recent_analyses = SoilAnalysis.objects.filter(
            field__user=user,
        ).select_related('field').prefetch_related('recommendations')[:5]

        # Aktif uyarılar
        active_alerts_qs = CareRecommendation.objects.filter(
            field__user=user,
            is_done=False,
        ).select_related('field')

        critical_alerts = active_alerts_qs.filter(priority='critical').count()
        active_alerts = active_alerts_qs[:10]

        # Hava durumu (statik)
        weather = WeatherService.get_weather(user)

        return {
            'fields': fields,
            'total_fields': total_fields,
            'empty_fields': empty_fields,
            'planted_fields': planted_fields,
            'total_area': total_area,
            'recent_analyses': recent_analyses,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'weather': weather,
        }
