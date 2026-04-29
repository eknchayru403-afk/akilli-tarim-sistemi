"""
Dashboard servisleri — Aggregation logic.

Performans iyileştirmeleri:
- Tek queryset ile count/aggregate hesaplama (N+1 → 1 sorgu)
- Django cache framework ile dashboard istatistik önbellekleme
- select_related/prefetch_related ile ilişkili veri çekimi
"""

import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, DecimalField, Q, Sum
from django.db.models.functions import Coalesce

from apps.analysis.models import CareRecommendation, SoilAnalysis
from apps.fields.models import Field
from apps.weather.services import WeatherService

logger = logging.getLogger(__name__)

# Önbellek anahtar şablonu
_CACHE_KEY_DASHBOARD = 'dashboard_stats_user_{user_id}'


class DashboardService:
    """Dashboard için veri toplama servisi."""

    @staticmethod
    def get_dashboard_data(user) -> dict:
        """
        Kullanıcı için dashboard verilerini toplar.

        Optimizasyonlar:
        - count() ve aggregate() tek sorguda çalışır (3 ayrı COUNT → 1 annotate).
        - total_area SUM ile DB seviyesinde hesaplanır (Python döngüsü yerine).
        - Dashboard istatistikleri kullanıcı bazlı önbelleklenir.
        - select_related/prefetch_related ile N+1 engellenir.

        Args:
            user: Mevcut kullanıcı.

        Returns:
            Template context dict.
        """
        cache_key = _CACHE_KEY_DASHBOARD.format(user_id=user.pk)
        cached_stats = cache.get(cache_key)

        # ── 1) İstatistikler (önbellekten veya DB'den) ──
        if cached_stats:
            stats = cached_stats
            logger.debug("Dashboard istatistikleri cache'ten alındı: user=%s", user.pk)
        else:
            stats = Field.objects.filter(user=user).aggregate(
                total_fields=Count('id'),
                empty_fields=Count('id', filter=Q(status='empty')),
                planted_fields=Count('id', filter=Q(status='planted')),
                total_area=Coalesce(
                    Sum('area_decar'),
                    0,
                    output_field=DecimalField(),
                ),
            )
            cache.set(
                cache_key,
                stats,
                getattr(settings, 'CACHE_TTL_DASHBOARD', 120),
            )
            logger.debug("Dashboard istatistikleri DB'den hesaplandı: user=%s", user.pk)

        # ── 2) Tarla listesi (template render için gerekli) ──
        fields = Field.objects.filter(user=user)

        # ── 3) Son analizler (select_related + prefetch_related) ──
        recent_analyses = SoilAnalysis.objects.filter(
            field__user=user,
        ).select_related('field').prefetch_related('recommendations')[:5]

        # ── 4) Aktif uyarılar (tek queryset, iki kez değerlendirme yerine) ──
        active_alerts_qs = CareRecommendation.objects.filter(
            field__user=user,
            is_done=False,
        ).select_related('field').order_by('-priority', '-created_at')

        critical_alerts = active_alerts_qs.filter(priority='critical').count()
        active_alerts = active_alerts_qs[:10]

        # ── 5) Hava durumu (statik — DB erişimi yok) ──
        weather = WeatherService.get_weather(user)

        return {
            'fields': fields,
            'total_fields': stats['total_fields'],
            'empty_fields': stats['empty_fields'],
            'planted_fields': stats['planted_fields'],
            'total_area': float(stats['total_area']),
            'recent_analyses': recent_analyses,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'weather': weather,
        }

    @staticmethod
    def invalidate_cache(user) -> None:
        """
        Kullanıcının dashboard önbelleğini temizler.

        Tarla ekleme/silme/güncelleme sonrası çağrılmalıdır.

        Args:
            user: Kullanıcı nesnesi veya user_id.
        """
        user_id = user.pk if hasattr(user, 'pk') else user
        cache_key = _CACHE_KEY_DASHBOARD.format(user_id=user_id)
        cache.delete(cache_key)
        logger.debug("Dashboard cache temizlendi: user=%s", user_id)
