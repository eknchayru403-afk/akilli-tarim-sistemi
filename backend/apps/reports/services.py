"""
Rapor servisleri — Veritabanı sorgulama ve rapor verisi hazırlama.
"""
import logging
from datetime import datetime
from apps.analysis.models import CareRecommendation, CropRecommendation, SoilAnalysis
from apps.fields.models import Field

logger = logging.getLogger(__name__)


class ReportService:
    """Rapor verisi toplama servisi."""

    @staticmethod
    def get_report_data(user, field_id=None, date_from=None, date_to=None) -> dict:
        """
        Rapor icin gerekli verileri toplar.

        Args:
            user: Kullanici.
            field_id: Tarla ID (None ise tum tarlalar).
            date_from: Baslangic tarihi.
            date_to: Bitis tarihi.

        Returns:
            Rapor verisi dict.
        """
        # Tarla filtresi
        field_filter = {'field__user': user}
        if field_id:
            field_filter['field__id'] = field_id

        # Tarih filtresi
        if date_from:
            field_filter['created_at__date__gte'] = date_from
        if date_to:
            field_filter['created_at__date__lte'] = date_to

        # Tarla adi
        field_name = 'Tum Tarlalar'
        if field_id:
            try:
                field_name = Field.objects.get(id=field_id, user=user).name
            except Field.DoesNotExist:
                pass

        # Bakim kayitlari
        care_qs = CareRecommendation.objects.filter(
            **field_filter
        ).select_related('field').order_by('-created_at')

        care_records = []
        for c in care_qs:
            care_records.append({
                'type': c.recommendation_type,
                'field_name': c.field.name,
                'message': c.message,
                'priority': c.get_priority_display(),
                'is_done': c.is_done,
                'date': c.created_at.strftime('%d.%m.%Y %H:%M'),
            })

        # Toprak analizleri
        soil_qs = SoilAnalysis.objects.filter(
            **field_filter
        ).select_related('field').order_by('-created_at')

        soil_analyses = []
        for s in soil_qs:
            soil_analyses.append({
                'field_name': s.field.name,
                'nitrogen': float(s.nitrogen),
                'phosphorus': float(s.phosphorus),
                'potassium': float(s.potassium),
                'ph': float(s.ph),
                'humidity': float(s.humidity),
                'temperature': float(s.temperature),
                'rainfall': float(s.rainfall),
                'date': s.created_at.strftime('%d.%m.%Y %H:%M'),
            })

        # Urun onerileri
        rec_filter = {'analysis__field__user': user}
        if field_id:
            rec_filter['analysis__field__id'] = field_id
        if date_from:
            rec_filter['created_at__date__gte'] = date_from
        if date_to:
            rec_filter['created_at__date__lte'] = date_to

        rec_qs = CropRecommendation.objects.filter(
            **rec_filter
        ).select_related('analysis', 'analysis__field').order_by('-created_at')

        recommendations = []
        for r in rec_qs:
            recommendations.append({
                'crop_name_tr': r.crop_name_tr,
                'confidence': float(r.confidence),
                'yield_kg': float(r.estimated_yield_kg),
                'revenue_tl': float(r.estimated_revenue_tl),
                'rank': r.rank,
                'date': r.created_at.strftime('%d.%m.%Y %H:%M'),
            })

        return {
            'user_name': user.get_full_name() or user.username,
            'field_name': field_name,
            'date_from': date_from.strftime('%d.%m.%Y') if date_from else 'Baslangic',
            'date_to': date_to.strftime('%d.%m.%Y') if date_to else 'Guncel',
            'care_records': care_records,
            'soil_analyses': soil_analyses,
            'recommendations': recommendations,
        }
