"""
Model eğitimi — RandomForestClassifier ile ürün tahmin modeli.

Kaggle CSV'sinden veri yükler, Türkiye mahsullerini filtreler,
model eğitir ve joblib ile kaydeder.
"""

import logging
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from .constants import FEATURE_COLUMNS, MODEL_FILENAME
from .data_loader import get_prepared_data

logger = logging.getLogger(__name__)


def train_crop_model(
    csv_path: Path | None = None,
    output_dir: Path | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Ürün tahmin modelini eğitir ve kaydeder.

    Args:
        csv_path: CSV dosya yolu.
        output_dir: Model kayıt dizini.
        test_size: Test seti oranı.
        random_state: Rastgelelik seed'i.

    Returns:
        Eğitim sonuçları dict: accuracy, report, model_path.
    """
    # Veriyi hazırla
    df = get_prepared_data(csv_path)

    # Feature / label ayır
    x = df[FEATURE_COLUMNS].values
    y = df['label'].values

    logger.info("Feature shape: %s, Unique labels: %d", x.shape, len(set(y)))

    # Train/test split
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=random_state, stratify=y,
    )

    # Model oluştur ve eğit
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    # Değerlendirme
    y_pred = model.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    logger.info("Model accuracy: %.4f", accuracy)
    logger.info("Classification Report:\n%s", report)

    # Modeli kaydet
    if output_dir is None:
        from django.conf import settings
        output_dir = settings.ML_MODELS_DIR

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / MODEL_FILENAME
    joblib.dump(model, model_path)
    logger.info("Model kaydedildi: %s", model_path)

    return {
        'accuracy': accuracy,
        'report': report,
        'model_path': str(model_path),
        'n_samples': len(df),
        'n_features': len(FEATURE_COLUMNS),
        'n_classes': len(set(y)),
    }
