"""
TensorFlow Model Eğitim Pipeline'ı.

Sulama, gübreleme ve hastalık riski modellerini
sentetik veri ile eğitir ve kaydeder.

Kullanım:
    python manage.py shell -c "from ml.tf_models.trainer import train_all_models; train_all_models()"
"""

import logging
import time
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def train_irrigation_model(output_dir: Path, epochs: int = 50) -> dict:
    """
    Sulama modelini eğitir ve kaydeder.

    Args:
        output_dir: Model kayıt dizini.
        epochs: Eğitim epoch sayısı.

    Returns:
        Eğitim sonuçları dict.
    """
    from .constants import IRRIGATION_MODEL_FILE
    from .irrigation_model import build_irrigation_model, generate_irrigation_training_data

    logger.info("═" * 50)
    logger.info("Sulama modeli eğitimi başlıyor...")

    # Veri üret
    X, y = generate_irrigation_training_data(n_samples=2000)

    # Model oluştur
    model = build_irrigation_model(input_dim=X.shape[1])
    if model is None:
        return {'error': 'TensorFlow yüklenemedi'}

    # Eğit
    start_time = time.time()
    history = model.fit(
        X, y,
        epochs=epochs,
        batch_size=32,
        validation_split=0.2,
        verbose=0,
    )
    training_time = time.time() - start_time

    # Kaydet
    model_path = output_dir / IRRIGATION_MODEL_FILE
    model.save(model_path)

    # Sonuçlar
    final_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]
    final_loss = history.history['loss'][-1]

    result = {
        'model': 'Sulama Tahmini',
        'accuracy': round(final_acc * 100, 2),
        'val_accuracy': round(final_val_acc * 100, 2),
        'loss': round(final_loss, 4),
        'epochs': epochs,
        'training_time': round(training_time, 2),
        'model_path': str(model_path),
        'n_samples': len(X),
        'n_params': model.count_params(),
    }

    logger.info("Sulama modeli eğitildi: accuracy=%.2f%%, val_accuracy=%.2f%%",
                result['accuracy'], result['val_accuracy'])
    return result


def train_fertilization_model(output_dir: Path, epochs: int = 50) -> dict:
    """
    Gübreleme modelini eğitir ve kaydeder.

    Args:
        output_dir: Model kayıt dizini.
        epochs: Eğitim epoch sayısı.

    Returns:
        Eğitim sonuçları dict.
    """
    from .constants import FERTILIZATION_MODEL_FILE
    from .fertilization_model import (
        build_fertilization_model,
        generate_fertilization_training_data,
    )

    logger.info("═" * 50)
    logger.info("Gübreleme modeli eğitimi başlıyor...")

    X, y = generate_fertilization_training_data(n_samples=2000)
    model = build_fertilization_model(input_dim=X.shape[1], num_classes=4)
    if model is None:
        return {'error': 'TensorFlow yüklenemedi'}

    start_time = time.time()
    history = model.fit(
        X, y,
        epochs=epochs,
        batch_size=32,
        validation_split=0.2,
        verbose=0,
    )
    training_time = time.time() - start_time

    model_path = output_dir / FERTILIZATION_MODEL_FILE
    model.save(model_path)

    final_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]

    result = {
        'model': 'Gübreleme Tahmini',
        'accuracy': round(final_acc * 100, 2),
        'val_accuracy': round(final_val_acc * 100, 2),
        'loss': round(history.history['loss'][-1], 4),
        'epochs': epochs,
        'training_time': round(training_time, 2),
        'model_path': str(model_path),
        'n_samples': len(X),
        'n_params': model.count_params(),
    }

    logger.info("Gübreleme modeli eğitildi: accuracy=%.2f%%, val_accuracy=%.2f%%",
                result['accuracy'], result['val_accuracy'])
    return result


def train_disease_risk_model(output_dir: Path, epochs: int = 50) -> dict:
    """
    Hastalık riski modelini eğitir ve kaydeder.

    Args:
        output_dir: Model kayıt dizini.
        epochs: Eğitim epoch sayısı.

    Returns:
        Eğitim sonuçları dict.
    """
    from .constants import DISEASE_RISK_MODEL_FILE
    from .disease_risk_model import (
        build_disease_risk_model,
        generate_disease_training_data,
    )

    logger.info("═" * 50)
    logger.info("Hastalık riski modeli eğitimi başlıyor...")

    X, y = generate_disease_training_data(n_samples=2000)
    model = build_disease_risk_model(input_dim=X.shape[1], num_classes=4)
    if model is None:
        return {'error': 'TensorFlow yüklenemedi'}

    start_time = time.time()
    history = model.fit(
        X, y,
        epochs=epochs,
        batch_size=32,
        validation_split=0.2,
        verbose=0,
    )
    training_time = time.time() - start_time

    model_path = output_dir / DISEASE_RISK_MODEL_FILE
    model.save(model_path)

    final_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]

    result = {
        'model': 'Hastalık Riski Tahmini',
        'accuracy': round(final_acc * 100, 2),
        'val_accuracy': round(final_val_acc * 100, 2),
        'loss': round(history.history['loss'][-1], 4),
        'epochs': epochs,
        'training_time': round(training_time, 2),
        'model_path': str(model_path),
        'n_samples': len(X),
        'n_params': model.count_params(),
    }

    logger.info("Hastalık riski modeli eğitildi: accuracy=%.2f%%, val_accuracy=%.2f%%",
                result['accuracy'], result['val_accuracy'])
    return result


def train_all_models(epochs: int = 50) -> list[dict]:
    """
    Tüm TensorFlow modellerini eğitir.

    Args:
        epochs: Eğitim epoch sayısı.

    Returns:
        Tüm model eğitim sonuçlarının listesi.
    """
    from django.conf import settings

    output_dir = settings.ML_MODELS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("TensorFlow Model Eğitim Pipeline'ı Başlatıldı")
    logger.info("=" * 60)

    results = []

    # 1) Sulama modeli
    results.append(train_irrigation_model(output_dir, epochs))

    # 2) Gübreleme modeli
    results.append(train_fertilization_model(output_dir, epochs))

    # 3) Hastalık riski modeli
    results.append(train_disease_risk_model(output_dir, epochs))

    logger.info("=" * 60)
    logger.info("Tüm modeller eğitildi!")
    for r in results:
        if 'error' not in r:
            logger.info(
                "  %s: accuracy=%.2f%%, val_accuracy=%.2f%%, süre=%.1fs",
                r['model'], r['accuracy'], r['val_accuracy'], r['training_time'],
            )
    logger.info("=" * 60)

    return results
