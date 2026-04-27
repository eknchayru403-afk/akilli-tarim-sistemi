"""
Analysis servisleri — iş mantığı katmanı.

SimulationService: CSV'den sensör verisi simüle eder.
AnalysisService: ML modeli ile ürün tahmini yapar.
CareAdvisor: Kural tabanlı bakım tavsiyesi üretir.
"""

import logging
import random

import pandas as pd
from django.conf import settings

from apps.fields.models import Field
from ml.constants import THRESHOLDS, TURKEY_CROP_LABELS
from ml.predictor import CropPredictor

from .models import CareRecommendation, CropRecommendation, SoilAnalysis

logger = logging.getLogger(__name__)


class SimulationService:
    """CSV'den rastgele sensör verisi simüle eder."""

    @staticmethod
    def simulate_sensor_data(field: Field) -> SoilAnalysis:
        """
        CSV'den rastgele bir satır seçip SoilAnalysis kaydı oluşturur.

        Args:
            field: Simülasyon yapılacak tarla.

        Returns:
            Oluşturulan SoilAnalysis kaydı.
        """
        csv_path = settings.DATA_DIR / 'Crop_recommendation.csv'
        df = pd.read_csv(csv_path)

        # Türkiye mahsullerini filtrele
        df = df[df['label'].isin(TURKEY_CROP_LABELS)]

        # Rastgele bir satır seç
        row = df.sample(n=1).iloc[0]

        analysis = SoilAnalysis.objects.create(
            field=field,
            nitrogen=round(float(row['N']), 2),
            phosphorus=round(float(row['P']), 2),
            potassium=round(float(row['K']), 2),
            temperature=round(float(row['temperature']), 2),
            humidity=round(float(row['humidity']), 2),
            ph=round(float(row['ph']), 2),
            rainfall=round(float(row['rainfall']), 2),
            source='simulation',
        )

        logger.info("Simülasyon verisi oluşturuldu: %s", analysis)
        return analysis


class AnalysisService:
    """ML modeli ile ürün analizi ve öneri üretimi."""

    @staticmethod
    def run_analysis(soil_analysis: SoilAnalysis) -> list[CropRecommendation]:
        """
        Toprak analizi üzerinden ML tahminini çalıştırır.

        Args:
            soil_analysis: Toprak analizi kaydı.

        Returns:
            Oluşturulan CropRecommendation listesi.
        """
        predictor = CropPredictor()

        if not predictor.is_ready:
            logger.error("ML modeli hazır değil, analiz yapılamaz")
            return []

        area_hectare = soil_analysis.field.area_hectare

        predictions = predictor.predict(
            nitrogen=float(soil_analysis.nitrogen),
            phosphorus=float(soil_analysis.phosphorus),
            potassium=float(soil_analysis.potassium),
            temperature=float(soil_analysis.temperature),
            humidity=float(soil_analysis.humidity),
            ph=float(soil_analysis.ph),
            rainfall=float(soil_analysis.rainfall),
            area_hectare=area_hectare,
        )

        recommendations = []
        for pred in predictions:
            rec = CropRecommendation.objects.create(
                analysis=soil_analysis,
                crop_name=pred['crop_name'],
                crop_name_tr=pred['crop_name_tr'],
                confidence=pred['confidence'],
                estimated_yield_kg=pred['estimated_yield_kg'],
                estimated_revenue_tl=pred['estimated_revenue_tl'],
                rank=pred['rank'],
            )
            recommendations.append(rec)

        logger.info(
            "Analiz tamamlandı: %d öneri oluşturuldu",
            len(recommendations),
        )
        return recommendations


class CareAdvisor:
    """Kural tabanlı bakım tavsiye motoru."""

    @staticmethod
    def generate_recommendations(
        field: Field,
        analysis: SoilAnalysis,
    ) -> list[CareRecommendation]:
        """
        Toprak verilerine göre bakım tavsiyeleri üretir.

        Args:
            field: Tarla.
            analysis: Son toprak analizi.

        Returns:
            Oluşturulan CareRecommendation listesi.
        """
        # Eski tavsiyeleri temizle
        field.care_recommendations.filter(is_done=False).delete()

        recommendations = []
        checks = [
            CareAdvisor._check_humidity,
            CareAdvisor._check_ph,
            CareAdvisor._check_nitrogen,
            CareAdvisor._check_phosphorus,
            CareAdvisor._check_potassium,
            CareAdvisor._check_temperature,
            CareAdvisor._check_rainfall,
        ]

        for check_fn in checks:
            result = check_fn(analysis)
            if result:
                rec = CareRecommendation.objects.create(
                    field=field, **result,
                )
                recommendations.append(rec)

        logger.info(
            "%s için %d bakım tavsiyesi üretildi",
            field.name, len(recommendations),
        )
        return recommendations

    @staticmethod
    def _check_humidity(analysis: SoilAnalysis) -> dict | None:
        """Nem kontrolü."""
        humidity = float(analysis.humidity)
        if humidity < THRESHOLDS['humidity_low']:
            return {
                'recommendation_type': 'irrigation',
                'message': f'Toprak nemi kritik seviyede ({humidity:.1f}%). Acil sulama gerekli.',
                'priority': 'critical',
            }
        if humidity > THRESHOLDS['humidity_high']:
            return {
                'recommendation_type': 'irrigation',
                'message': f'Toprak nemi çok yüksek ({humidity:.1f}%). Drenaj kontrol edilmeli.',
                'priority': 'high',
            }
        return None

    @staticmethod
    def _check_ph(analysis: SoilAnalysis) -> dict | None:
        """pH kontrolü."""
        ph = float(analysis.ph)
        if ph < THRESHOLDS['ph_low']:
            return {
                'recommendation_type': 'soil_amendment',
                'message': f'Toprak asitliği yüksek (pH: {ph:.2f}). Kireçleme önerilir.',
                'priority': 'high',
            }
        if ph > THRESHOLDS['ph_high']:
            return {
                'recommendation_type': 'soil_amendment',
                'message': f'Toprak bazikliği yüksek (pH: {ph:.2f}). Kükürt uygulaması önerilir.',
                'priority': 'high',
            }
        return None

    @staticmethod
    def _check_nitrogen(analysis: SoilAnalysis) -> dict | None:
        """Azot kontrolü."""
        nitrogen = float(analysis.nitrogen)
        if nitrogen < THRESHOLDS['nitrogen_low']:
            return {
                'recommendation_type': 'fertilization',
                'message': f'Azot seviyesi düşük ({nitrogen:.1f}). Azotlu gübre uygulanmalı.',
                'priority': 'medium',
            }
        return None

    @staticmethod
    def _check_phosphorus(analysis: SoilAnalysis) -> dict | None:
        """Fosfor kontrolü."""
        phosphorus = float(analysis.phosphorus)
        if phosphorus < THRESHOLDS['phosphorus_low']:
            return {
                'recommendation_type': 'fertilization',
                'message': f'Fosfor seviyesi düşük ({phosphorus:.1f}). Fosforlu gübre önerilir.',
                'priority': 'medium',
            }
        return None

    @staticmethod
    def _check_potassium(analysis: SoilAnalysis) -> dict | None:
        """Potasyum kontrolü."""
        potassium = float(analysis.potassium)
        if potassium < THRESHOLDS['potassium_low']:
            return {
                'recommendation_type': 'fertilization',
                'message': f'Potasyum seviyesi düşük ({potassium:.1f}). Potasyumlu gübre önerilir.',
                'priority': 'medium',
            }
        return None

    @staticmethod
    def _check_temperature(analysis: SoilAnalysis) -> dict | None:
        """Sıcaklık kontrolü."""
        temp = float(analysis.temperature)
        if temp > THRESHOLDS['temperature_high']:
            return {
                'recommendation_type': 'temperature',
                'message': f'Sıcaklık çok yüksek ({temp:.1f}°C). Gölgeleme ve sulama artırılmalı.',
                'priority': 'high',
            }
        if temp < THRESHOLDS['temperature_low']:
            return {
                'recommendation_type': 'temperature',
                'message': f'Sıcaklık çok düşük ({temp:.1f}°C). Don riski var, koruyucu örtü kullanın.',
                'priority': 'critical',
            }
        return None

    @staticmethod
    def _check_rainfall(analysis: SoilAnalysis) -> dict | None:
        """Yağış kontrolü."""
        rainfall = float(analysis.rainfall)
        if rainfall < THRESHOLDS['rainfall_low']:
            return {
                'recommendation_type': 'irrigation',
                'message': f'Yağış miktarı düşük ({rainfall:.1f} mm). Ek sulama planlanmalı.',
                'priority': 'medium',
            }
        return None
