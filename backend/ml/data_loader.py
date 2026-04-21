"""
Veri yükleme modülü — Kaggle CSV okuma ve Türkiye mahsul filtreleme.

CSV dosyasını yükler, sadece Türkiye iklimine uygun
mahsulleri filtreler ve ML eğitimi için hazır hale getirir.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from django.conf import settings

from .constants import TURKEY_CROP_LABELS

logger = logging.getLogger(__name__)


def load_crop_data(csv_path: Path | None = None) -> pd.DataFrame:
    """
    Kaggle Crop Recommendation CSV'sini yükler.

    Args:
        csv_path: CSV dosya yolu. None ise varsayılan kullanılır.

    Returns:
        Tüm veriyi içeren DataFrame.
    """
    if csv_path is None:
        csv_path = settings.DATA_DIR / 'Crop_recommendation.csv'

    logger.info("CSV yükleniyor: %s", csv_path)
    df = pd.read_csv(csv_path)
    logger.info("Toplam satır: %d, Sütunlar: %s", len(df), list(df.columns))
    return df


def filter_turkey_crops(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sadece Türkiye iklimine uygun mahsulleri filtreler.

    Args:
        df: Ham CSV verisi.

    Returns:
        Filtrelenmiş DataFrame.
    """
    filtered = df[df['label'].isin(TURKEY_CROP_LABELS)].copy()
    logger.info(
        "Türkiye filtresi: %d → %d satır (%d ürün)",
        len(df), len(filtered), filtered['label'].nunique(),
    )
    return filtered


def add_synthetic_crops(df: pd.DataFrame) -> pd.DataFrame:
    """
    CSV'de eksik olan Buğday ve Ayçiçeği için sentetik veri ekler.

    Args:
        df: Filtrelenmiş DataFrame.

    Returns:
        Sentetik veriler eklenmiş DataFrame.
    """
    synthetic_data = []

    if 'wheat' not in df['label'].values:
        logger.info("Buğday için sentetik veri ekleniyor")
        for _ in range(100):
            synthetic_data.append({
                'N': np.random.uniform(60, 120),
                'P': np.random.uniform(35, 65),
                'K': np.random.uniform(15, 45),
                'temperature': np.random.uniform(12, 28),
                'humidity': np.random.uniform(40, 70),
                'ph': np.random.uniform(6.0, 7.5),
                'rainfall': np.random.uniform(300, 600),
                'label': 'wheat',
            })

    if 'sunflower' not in df['label'].values:
        logger.info("Ayçiçeği için sentetik veri ekleniyor")
        for _ in range(100):
            synthetic_data.append({
                'N': np.random.uniform(50, 100),
                'P': np.random.uniform(40, 70),
                'K': np.random.uniform(20, 50),
                'temperature': np.random.uniform(18, 32),
                'humidity': np.random.uniform(35, 65),
                'ph': np.random.uniform(6.0, 7.5),
                'rainfall': np.random.uniform(250, 500),
                'label': 'sunflower',
            })

    if synthetic_data:
        synthetic_df = pd.DataFrame(synthetic_data)
        df = pd.concat([df, synthetic_df], ignore_index=True)
        logger.info("Sentetik veri sonrası: %d satır", len(df))

    return df


def get_prepared_data(csv_path: Path | None = None) -> pd.DataFrame:
    """
    Tam pipeline: CSV yükle → filtrele → sentetik ekle.

    Args:
        csv_path: CSV dosya yolu.

    Returns:
        Eğitime hazır DataFrame.
    """
    df = load_crop_data(csv_path)
    df = filter_turkey_crops(df)
    df = add_synthetic_crops(df)
    return df
