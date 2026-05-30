"""
Rapor servisleri — Veritabanı sorgulama ve rapor verisi hazırlama.
"""
import logging
from datetime import datetime
from apps.analysis.models import CareRecommendation, CropRecommendation, SoilAnalysis
from apps.fields.models import Field, SensorData, IrrigationLog

logger = logging.getLogger(__name__)


class ReportService:
    """Rapor verisi toplama servisi."""

    @staticmethod
    def get_report_data(user, field_id=None, date_from=None, date_to=None, report_type='general') -> dict:
        """
        Rapor icin gerekli verileri toplar.

        Args:
            user: Kullanici.
            field_id: Tarla ID (None ise tum tarlalar).
            date_from: Baslangic tarihi.
            date_to: Bitis tarihi.
            report_type: Rapor tipi ('general', 'irrigation', 'fertilization', 'yield', 'sensor').

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
        field_name = 'Tüm Tarlalar'
        if field_id:
            try:
                field_name = Field.objects.get(id=field_id, user=user).name
            except Field.DoesNotExist:
                pass

        care_records = []
        soil_analyses = []
        recommendations = []
        sensor_data = []
        irrigation_logs = []

        # 1. Bakım kayıtları (Sulama, Gübreleme, İlaçlama, Sıcaklık)
        if report_type in ['general', 'irrigation', 'fertilization', 'sensor']:
            care_qs = CareRecommendation.objects.filter(**field_filter).select_related('field').order_by('-created_at')
            if report_type == 'irrigation':
                care_qs = care_qs.filter(recommendation_type='irrigation')
            elif report_type == 'fertilization':
                care_qs = care_qs.filter(recommendation_type__in=['fertilization', 'soil_amendment'])
            elif report_type == 'sensor':
                care_qs = care_qs.filter(recommendation_type='temperature')

            for c in care_qs:
                care_records.append({
                    'type': c.recommendation_type,
                    'type_display': c.get_recommendation_type_display(),
                    'field_name': c.field.name,
                    'message': c.message,
                    'priority': c.get_priority_display(),
                    'is_done': c.is_done,
                    'date': c.created_at.strftime('%d.%m.%Y %H:%M'),
                })

        # 2. Toprak Analizleri
        if report_type in ['general', 'fertilization', 'yield', 'sensor']:
            soil_qs = SoilAnalysis.objects.filter(**field_filter).select_related('field').order_by('-created_at')
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

        # 3. Ürün Önerileri (Verim Analizi)
        if report_type in ['general', 'yield']:
            rec_filter = {'analysis__field__user': user}
            if field_id:
                rec_filter['analysis__field__id'] = field_id
            if date_from:
                rec_filter['created_at__date__gte'] = date_from
            if date_to:
                rec_filter['created_at__date__lte'] = date_to

            rec_qs = CropRecommendation.objects.filter(**rec_filter).select_related('analysis', 'analysis__field').order_by('-created_at')
            for r in rec_qs:
                recommendations.append({
                    'field_name': r.analysis.field.name,
                    'crop_name_tr': r.crop_name_tr,
                    'confidence': float(r.confidence),
                    'yield_kg': float(r.estimated_yield_kg),
                    'revenue_tl': float(r.estimated_revenue_tl),
                    'rank': r.rank,
                    'date': r.created_at.strftime('%d.%m.%Y %H:%M'),
                })

        # 4. Sensör Verileri
        if report_type in ['general', 'irrigation', 'sensor']:
            sensor_qs = SensorData.objects.filter(**field_filter).select_related('field').order_by('-created_at')
            for sd in sensor_qs:
                sensor_data.append({
                    'field_name': sd.field.name,
                    'humidity': float(sd.humidity),
                    'temperature': float(sd.temperature),
                    'soil_moisture': float(sd.soil_moisture),
                    'plant_water_consumption': float(sd.plant_water_consumption),
                    'soil_ph': float(sd.soil_ph),
                    'light_intensity': float(sd.light_intensity),
                    'date': sd.created_at.strftime('%d.%m.%Y %H:%M'),
                })

        # 5. Sulama / Gübreleme İşlem Geçmişi (IrrigationLog)
        if report_type in ['general', 'irrigation', 'fertilization']:
            logs_qs = IrrigationLog.objects.filter(**field_filter).select_related('field').order_by('-created_at')
            if report_type == 'irrigation':
                logs_qs = logs_qs.filter(log_type='irrigation')
            elif report_type == 'fertilization':
                logs_qs = logs_qs.filter(log_type='fertilization')

            for l in logs_qs:
                irrigation_logs.append({
                    'field_name': l.field.name,
                    'type': l.log_type,
                    'type_display': l.get_log_type_display(),
                    'amount': float(l.amount),
                    'details': l.details,
                    'date': l.created_at.strftime('%d.%m.%Y %H:%M'),
                })

        return {
            'user_name': user.get_full_name() or user.username,
            'field_name': field_name,
            'date_from': date_from.strftime('%d.%m.%Y') if date_from else 'Başlangıç',
            'date_to': date_to.strftime('%d.%m.%Y') if date_to else 'Güncel',
            'report_type': report_type,
            'care_records': care_records,
            'soil_analyses': soil_analyses,
            'recommendations': recommendations,
            'sensor_data': sensor_data,
            'irrigation_logs': irrigation_logs,
        }
