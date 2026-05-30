"""
Model eğitimi — Gübreleme optimizasyonu için regresyon ve sınıflandırma modelleri.

Dummy veri üreterek veya mevcut bir veri setinden, gübre tipi ve zamanlaması için sınıflandırıcı,
gübre miktarı için regresyon modeli eğitir ve joblib ile kaydeder.
"""

import logging
import random
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

FERTILIZER_MODEL_FILENAME = 'fertilizer_model.joblib'
FERTILIZER_LABEL_ENCODERS_FILENAME = 'fertilizer_label_encoders.joblib'

# Eğitim için dummy veri seti üretici
def generate_dummy_fertilizer_data(n_samples=1000):
    crops = ['Bugday', 'Misir', 'Pamuk', 'Domates', 'Seker Pancari']
    stages = ['Ekim Oncesi', 'Fide', 'Gelisim', 'Ciceklenme']
    fert_types = ['UREA', 'DAP', 'NPK 15-15-15', 'NPK 20-20-20', 'Amonyum Sulfat']
    timings = ['Toprak Hazirligi', 'İlk Sulama', 'Ara Capa', 'Tomurcuklanma']

    data = []
    for _ in range(n_samples):
        n = random.uniform(10, 100)
        p = random.uniform(5, 60)
        k = random.uniform(10, 80)
        crop = random.choice(crops)
        stage = random.choice(stages)
        
        # Basit kurallar (modelin öğrenebilmesi için mantıksal bağımlılık)
        if crop == 'Bugday':
            f_type = 'UREA' if n < 40 else 'DAP'
            amt = random.uniform(15, 25)
        elif crop == 'Domates':
            f_type = 'NPK 20-20-20'
            amt = random.uniform(25, 45)
        else:
            f_type = random.choice(fert_types)
            amt = random.uniform(10, 30)
            
        timing = random.choice(timings)
        
        data.append({
            'nitrogen': n,
            'phosphorus': p,
            'potassium': k,
            'crop_type': crop,
            'growth_stage': stage,
            'fertilizer_type': f_type,
            'amount_kg': amt,
            'application_timing': timing
        })
    return pd.DataFrame(data)

def train_fertilizer_model(
    csv_path: Path | None = None,
    output_dir: Path | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Gübreleme optimizasyon modellerini eğitir ve kaydeder.
    """
    if csv_path and csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        logger.info("CSV bulunamadı, dummy veri seti üretiliyor...")
        df = generate_dummy_fertilizer_data()

    # Encoders
    encoders = {
        'crop_type': LabelEncoder(),
        'growth_stage': LabelEncoder(),
        'fertilizer_type': LabelEncoder(),
        'application_timing': LabelEncoder()
    }
    
    # Feature Engineering
    df['crop_encoded'] = encoders['crop_type'].fit_transform(df['crop_type'])
    df['stage_encoded'] = encoders['growth_stage'].fit_transform(df['growth_stage'])
    
    df['type_encoded'] = encoders['fertilizer_type'].fit_transform(df['fertilizer_type'])
    df['timing_encoded'] = encoders['application_timing'].fit_transform(df['application_timing'])

    x = df[['nitrogen', 'phosphorus', 'potassium', 'crop_encoded', 'stage_encoded']].values
    
    y_type = df['type_encoded'].values
    y_amount = df['amount_kg'].values
    y_timing = df['timing_encoded'].values

    # Splitting
    x_train, x_test, y_type_tr, y_type_te, y_amt_tr, y_amt_te, y_time_tr, y_time_te = train_test_split(
        x, y_type, y_amount, y_timing, test_size=test_size, random_state=random_state
    )

    # Models
    clf_type = RandomForestClassifier(n_estimators=50, random_state=random_state)
    reg_amt = RandomForestRegressor(n_estimators=50, random_state=random_state)
    clf_time = RandomForestClassifier(n_estimators=50, random_state=random_state)

    clf_type.fit(x_train, y_type_tr)
    reg_amt.fit(x_train, y_amt_tr)
    clf_time.fit(x_train, y_time_tr)

    # Eval
    acc_type = accuracy_score(y_type_te, clf_type.predict(x_test))
    mae_amt = mean_absolute_error(y_amt_te, reg_amt.predict(x_test))
    acc_time = accuracy_score(y_time_te, clf_time.predict(x_test))

    logger.info("Fertilizer Type Accuracy: %.4f", acc_type)
    logger.info("Fertilizer Amount MAE: %.4f", mae_amt)
    logger.info("Application Timing Accuracy: %.4f", acc_time)

    # Save
    if output_dir is None:
        from django.conf import settings
        output_dir = settings.ML_MODELS_DIR

    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_bundle = {
        'type_classifier': clf_type,
        'amount_regressor': reg_amt,
        'timing_classifier': clf_time
    }

    joblib.dump(model_bundle, output_dir / FERTILIZER_MODEL_FILENAME)
    joblib.dump(encoders, output_dir / FERTILIZER_LABEL_ENCODERS_FILENAME)
    
    logger.info("Modeller kaydedildi: %s", output_dir)

    return {
        'accuracy_type': acc_type,
        'mae_amount': mae_amt,
        'accuracy_timing': acc_time,
        'n_samples': len(df)
    }
