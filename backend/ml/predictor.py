"""
Tahmin servisi — CropPredictor (Singleton pattern).

Eğitilmiş modeli yükleyerek toprak verilerinden ürün tahmini yapar.
"""

import json
import logging
import threading
from pathlib import Path

import joblib
import numpy as np

from .constants import MODEL_FILENAME, TOP_N_RECOMMENDATIONS, TURKEY_CROPS

logger = logging.getLogger(__name__)


class CropPredictor:
    """
    Ürün tahmin servisi. Singleton pattern ile tek instance.

    Eğitilmiş ML modelini yükler ve predict_proba() ile
    en uygun ürünleri döndürür.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> 'CropPredictor':
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

        model_path = settings.ML_MODELS_DIR / MODEL_FILENAME
        self._model = None
        self._prices = {}
        self._yields = {}

        if model_path.exists():
            self._model = joblib.load(model_path)
            logger.info("ML modeli yüklendi: %s", model_path)
        else:
            logger.warning("Model dosyası bulunamadı: %s", model_path)

        self._load_price_data(settings.DATA_DIR)
        self._load_yield_data(settings.DATA_DIR)
        self._initialized = True

    def _load_price_data(self, data_dir: Path) -> None:
        """Fiyat verilerini JSON'dan yükler."""
        price_path = data_dir / 'prices.json'
        if price_path.exists():
            with open(price_path, 'r', encoding='utf-8') as f:
                self._prices = json.load(f)
            logger.info("Fiyat verisi yüklendi: %d ürün", len(self._prices))

    def _load_yield_data(self, data_dir: Path) -> None:
        """Verim verilerini JSON'dan yükler."""
        yield_path = data_dir / 'yield_data.json'
        if yield_path.exists():
            with open(yield_path, 'r', encoding='utf-8') as f:
                self._yields = json.load(f)
            logger.info("Verim verisi yüklendi: %d ürün", len(self._yields))

    @property
    def is_ready(self) -> bool:
        """Model yüklü ve tahmine hazır mı?"""
        return self._model is not None

    def predict(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float,
        area_hectare: float = 1.0,
    ) -> list[dict]:
        """
        Toprak verilerinden ürün tahmini yapar.

        Args:
            nitrogen: Azot (N) değeri.
            phosphorus: Fosfor (P) değeri.
            potassium: Potasyum (K) değeri.
            temperature: Sıcaklık (°C).
            humidity: Nem (%).
            ph: pH değeri.
            rainfall: Yağış (mm).
            area_hectare: Tarla alanı (hektar).

        Returns:
            Top N ürün önerisi listesi.
        """
        if not self.is_ready:
            logger.error("Model yüklenmedi, tahmin yapılamaz")
            return []

        features = np.array([[
            nitrogen, phosphorus, potassium,
            temperature, humidity, ph, rainfall,
        ]])

        # Olasılık dağılımı
        probabilities = self._model.predict_proba(features)[0]
        classes = self._model.classes_

        # Sıralama
        sorted_indices = np.argsort(probabilities)[::-1]

        results = []
        for rank, idx in enumerate(sorted_indices[:TOP_N_RECOMMENDATIONS], 1):
            crop_name = classes[idx]
            confidence = round(probabilities[idx] * 100, 2)

            crop_info = self._get_crop_info(crop_name, area_hectare)
            results.append({
                'crop_name': crop_name,
                'crop_name_tr': TURKEY_CROPS.get(crop_name, crop_name),
                'confidence': confidence,
                'estimated_yield_kg': crop_info['yield_kg'],
                'estimated_revenue_tl': crop_info['revenue_tl'],
                'rank': rank,
            })

        return results

    def _get_crop_info(
        self, crop_name: str, area_hectare: float,
    ) -> dict:
        """Ürün için verim ve kazanç hesaplar."""
        yield_per_ha = self._yields.get(crop_name, 0)
        yield_kg = round(yield_per_ha * area_hectare, 2)

        price_data = self._prices.get(crop_name, {})
        price_per_kg = price_data.get('fiyat_tl_kg', 0)
        revenue_tl = round(yield_kg * price_per_kg, 2)

        return {
            'yield_kg': yield_kg,
            'revenue_tl': revenue_tl,
        }
