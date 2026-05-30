"""
ML Model Benchmark — Dogruluk, calisma suresi ve performans olcumu.

Mevcut RandomForest ve TF modellerinin performansini degerlendirir.

Kullanim:
    python manage.py shell -c "from ml.benchmark import run_benchmark; run_benchmark()"
"""
import logging
import time
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


def benchmark_crop_model() -> dict:
    """RandomForest urun tahmin modelinin performansini olcer."""
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from .data_loader import get_prepared_data
    from .constants import FEATURE_COLUMNS
    from .predictor import CropPredictor
    from sklearn.model_selection import train_test_split

    logger.info("=" * 60)
    logger.info("RandomForest Urun Tahmin Modeli Benchmark")
    logger.info("=" * 60)

    # Veri hazirla
    df = get_prepared_data()
    X = df[FEATURE_COLUMNS].values
    y = df['label'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )

    # Predictor yukle
    predictor = CropPredictor()
    if not predictor.is_ready:
        logger.error("Model yuklu degil!")
        return {'error': 'Model yuklu degil'}

    # Dogruluk olcumu
    start = time.time()
    y_pred = predictor._model.predict(X_test)
    predict_time = time.time() - start

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    # Latency olcumu (tek tahmin)
    latencies = []
    for _ in range(100):
        sample = X_test[np.random.randint(0, len(X_test))].reshape(1, -1)
        t0 = time.time()
        predictor._model.predict_proba(sample)
        latencies.append((time.time() - t0) * 1000)  # ms

    result = {
        'model': 'RandomForest (Urun Tahmini)',
        'accuracy': round(accuracy * 100, 2),
        'weighted_f1': round(report['weighted avg']['f1-score'] * 100, 2),
        'macro_f1': round(report['macro avg']['f1-score'] * 100, 2),
        'test_samples': len(X_test),
        'train_samples': len(X_train),
        'batch_predict_time_ms': round(predict_time * 1000, 2),
        'avg_single_predict_ms': round(np.mean(latencies), 3),
        'p95_single_predict_ms': round(np.percentile(latencies, 95), 3),
        'confusion_matrix': cm.tolist(),
        'per_class_report': {
            k: v for k, v in report.items()
            if k not in ('accuracy', 'macro avg', 'weighted avg')
        },
    }

    logger.info("Accuracy: %.2f%%", result['accuracy'])
    logger.info("Weighted F1: %.2f%%", result['weighted_f1'])
    logger.info("Ortalama tahmin suresi: %.3f ms", result['avg_single_predict_ms'])
    logger.info("P95 tahmin suresi: %.3f ms", result['p95_single_predict_ms'])

    return result


def benchmark_cross_validation() -> dict:
    """K-Fold Cross Validation ile model guvenilirligi olcer."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    from .data_loader import get_prepared_data
    from .constants import FEATURE_COLUMNS

    logger.info("=" * 60)
    logger.info("Cross Validation (5-Fold)")
    logger.info("=" * 60)

    df = get_prepared_data()
    X = df[FEATURE_COLUMNS].values
    y = df['label'].values

    model = RandomForestClassifier(
        n_estimators=100, max_depth=15,
        random_state=42, n_jobs=-1,
    )

    start = time.time()
    scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    cv_time = time.time() - start

    result = {
        'cv_folds': 5,
        'cv_scores': [round(s * 100, 2) for s in scores],
        'cv_mean': round(scores.mean() * 100, 2),
        'cv_std': round(scores.std() * 100, 2),
        'cv_time_seconds': round(cv_time, 2),
    }

    logger.info("CV Skorlari: %s", result['cv_scores'])
    logger.info("Ortalama: %.2f%% (+/- %.2f%%)", result['cv_mean'], result['cv_std'])

    return result


def run_benchmark() -> dict:
    """Tum benchmark'lari calistirir."""
    logger.info("=" * 60)
    logger.info("ATYS ML Model Benchmark Suite")
    logger.info("=" * 60)

    results = {
        'crop_model': benchmark_crop_model(),
        'cross_validation': benchmark_cross_validation(),
    }

    logger.info("\n" + "=" * 60)
    logger.info("Benchmark tamamlandi!")
    logger.info("=" * 60)

    return results
