"""
Gübreleme Optimizasyon Servisi — FertilizerOptimizer (Singleton pattern).

Eğitilmiş regresyon ve sınıflandırma modellerini yükleyerek 
toprak verileri ve bitki türüne göre gübre tavsiyesi yapar.
"""

import logging
import threading
from pathlib import Path

import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

# Örnek Model Dosya Adı
FERTILIZER_MODEL_FILENAME = 'fertilizer_model.joblib'
FERTILIZER_LABEL_ENCODERS_FILENAME = 'fertilizer_label_encoders.joblib'


class FertilizerOptimizer:
    """
    Gübreleme optimizasyon servisi. Singleton pattern ile tek instance.

    Eğitilmiş ML modellerini yükler ve N, P, K değerleri ile
    bitki türü/evresine göre en uygun gübreyi önerir.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> 'FertilizerOptimizer':
        """Thread-safe singleton oluşturma."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Modeli ilk kez yükler."""
        if self._initialized:
            return

        from django.conf import settings

        model_path = settings.ML_MODELS_DIR / FERTILIZER_MODEL_FILENAME
        encoder_path = settings.ML_MODELS_DIR / FERTILIZER_LABEL_ENCODERS_FILENAME
        
        self._model_bundle = None
        self._encoders = None

        if model_path.exists() and encoder_path.exists():
            try:
                self._model_bundle = joblib.load(model_path)
                self._encoders = joblib.load(encoder_path)
                logger.info("Fertilizer ML modeli yüklendi: %s", model_path)
            except Exception as e:
                logger.error("Model yüklenirken hata oluştu: %s", e)
        else:
            logger.warning("Fertilizer Model dosyaları bulunamadı: %s", model_path)

        self._initialized = True

    @property
    def is_ready(self) -> bool:
        """Model yüklü ve tahmine hazır mı?"""
        return self._model_bundle is not None and self._encoders is not None

    def predict(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        crop_type: str,
        growth_stage: str
    ) -> dict:
        """
        Toprak verilerinden ve bitki özelliklerinden gübre tavsiyesi üretir.

        Args:
            nitrogen: Azot (N) değeri.
            phosphorus: Fosfor (P) değeri.
            potassium: Potasyum (K) değeri.
            crop_type: Bitki türü (örn: Bugday, Misir).
            growth_stage: Gelişim evresi (örn: Fide, Ciceklenme).

        Returns:
            Önerilen gübre tipi, miktarı ve uygulama zamanını içeren sözlük.
        """
        if not self.is_ready:
            logger.error("Model yüklenmedi, gübre tahmini yapılamaz")
            # Fallback/Default değerler döndürülebilir veya hata fırlatılabilir.
            return {
                "fertilizer_type": "Genel Amaçlı (NPK 15-15-15)",
                "amount_kg_per_decare": 20.0,
                "application_timing": "Ekim/Dikim Öncesi"
            }

        try:
            # Sınıflandırıcılar ve regresör bundle içinden alınır
            classifier_type = self._model_bundle['type_classifier']
            regressor_amount = self._model_bundle['amount_regressor']
            classifier_timing = self._model_bundle['timing_classifier']

            # Label encoding crop_type ve growth_stage
            crop_encoder = self._encoders['crop_type']
            stage_encoder = self._encoders['growth_stage']
            
            # Eğer yeni bir crop_type geldiyse, default'a çek (veya -1)
            crop_encoded = crop_encoder.transform([crop_type])[0] if crop_type in crop_encoder.classes_ else 0
            stage_encoded = stage_encoder.transform([growth_stage])[0] if growth_stage in stage_encoder.classes_ else 0

            features = np.array([[nitrogen, phosphorus, potassium, crop_encoded, stage_encoded]])

            # Tahminler
            pred_type_encoded = classifier_type.predict(features)[0]
            pred_amount = regressor_amount.predict(features)[0]
            pred_timing_encoded = classifier_timing.predict(features)[0]

            # Çözümleme (Decoding)
            type_encoder = self._encoders['fertilizer_type']
            timing_encoder = self._encoders['application_timing']

            pred_type = type_encoder.inverse_transform([pred_type_encoded])[0]
            pred_timing = timing_encoder.inverse_transform([pred_timing_encoded])[0]

            # Miktarı makul sınırlar içinde tutmak (örn: negatif olamaz)
            pred_amount = max(5.0, round(float(pred_amount), 2))

            return {
                "fertilizer_type": pred_type,
                "amount_kg_per_decare": pred_amount,
                "application_timing": pred_timing
            }
        except Exception as e:
            logger.error("Gübre tahmini sırasında hata: %s", e)
            return {
                "fertilizer_type": "Hesaplanamadı",
                "amount_kg_per_decare": 0.0,
                "application_timing": "Belirsiz"
            }
