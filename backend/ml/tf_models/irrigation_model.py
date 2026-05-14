"""
Sulama İhtiyacı Tahmin Modeli (TensorFlow/Keras).

Toprak nemi, sıcaklık, yağış, mevsim ve toprak tipine göre
sulama gerekip gerekmediğini tahmin eder.

Girdiler:
    - soil_moisture (float): Toprak nemi (%)
    - temperature (float): Sıcaklık (°C)
    - humidity (float): Hava nemi (%)
    - rainfall (float): Yağış (mm)
    - season_encoded (int): Mevsim (0-3)
    - soil_type_encoded (int): Toprak tipi (0-5)

Çıktılar:
    - irrigation_needed (bool): Sulama gerekli mi
    - water_amount (float): Önerilen su miktarı (L/m²)
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


def build_irrigation_model(input_dim: int = 6):
    """
    Sulama tahmin modelini oluşturur.

    Keras Sequential model — 3 Dense katman + Dropout.

    Args:
        input_dim: Girdi boyutu (feature sayısı).

    Returns:
        Derlenmiş Keras modeli.
    """
    try:
        from tensorflow import keras
        from tensorflow.keras import layers
    except ImportError:
        logger.error("TensorFlow yüklü değil. 'pip install tensorflow' çalıştırın.")
        return None

    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(64, activation='relu', name='dense_1'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu', name='dense_2'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        layers.Dense(16, activation='relu', name='dense_3'),
        layers.Dense(1, activation='sigmoid', name='output'),
    ], name='irrigation_model')

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()],
    )

    logger.info("Sulama modeli oluşturuldu: %d parametre", model.count_params())
    return model


def generate_irrigation_training_data(n_samples: int = 2000) -> tuple:
    """
    Sulama modeli için sentetik eğitim verisi üretir.

    Kural tabanlı etiketleme:
    - Toprak nemi düşük + yağış az → sulama gerekli
    - Sıcaklık yüksek + nem düşük → sulama gerekli

    Args:
        n_samples: Üretilecek örnek sayısı.

    Returns:
        (X, y) — features ve labels numpy dizileri.
    """
    np.random.seed(42)

    soil_moisture = np.random.uniform(10, 90, n_samples)
    temperature = np.random.uniform(5, 45, n_samples)
    humidity = np.random.uniform(20, 95, n_samples)
    rainfall = np.random.uniform(0, 300, n_samples)
    season = np.random.randint(0, 4, n_samples)
    soil_type = np.random.randint(0, 6, n_samples)

    X = np.column_stack([
        soil_moisture, temperature, humidity, rainfall, season, soil_type,
    ])

    # Kural tabanlı etiketleme
    y = np.zeros(n_samples)
    for i in range(n_samples):
        score = 0
        if soil_moisture[i] < 30:
            score += 3
        elif soil_moisture[i] < 45:
            score += 1

        if temperature[i] > 30:
            score += 2
        elif temperature[i] > 25:
            score += 1

        if rainfall[i] < 30:
            score += 2
        elif rainfall[i] < 80:
            score += 1

        if humidity[i] < 40:
            score += 1

        # Yaz mevsimi ek puan
        if season[i] == 1:  # yaz
            score += 1

        # Kumlu toprak su tutar az
        if soil_type[i] == 1:  # kumlu
            score += 1

        y[i] = 1 if score >= 4 else 0

    logger.info(
        "Sulama eğitim verisi üretildi: %d örnek (sulama: %d, yok: %d)",
        n_samples, int(y.sum()), int(n_samples - y.sum()),
    )
    return X, y


def predict_irrigation(model, soil_moisture, temperature, humidity,
                       rainfall, season_encoded, soil_type_encoded) -> dict:
    """
    Sulama tahmini yapar.

    Args:
        model: Eğitilmiş Keras modeli.
        soil_moisture: Toprak nemi (%).
        temperature: Sıcaklık (°C).
        humidity: Hava nemi (%).
        rainfall: Yağış (mm).
        season_encoded: Mevsim kodu (0-3).
        soil_type_encoded: Toprak tipi kodu (0-5).

    Returns:
        Tahmin sonucu dict.
    """
    features = np.array([[
        soil_moisture, temperature, humidity,
        rainfall, season_encoded, soil_type_encoded,
    ]])

    probability = float(model.predict(features, verbose=0)[0][0])
    irrigation_needed = probability >= 0.5

    # Önerilen su miktarı hesapla
    if irrigation_needed:
        if probability >= 0.8:
            water_amount = round(np.random.uniform(10.0, 20.0), 1)
            urgency = 'Acil'
        elif probability >= 0.6:
            water_amount = round(np.random.uniform(5.0, 10.0), 1)
            urgency = 'Normal'
        else:
            water_amount = round(np.random.uniform(2.0, 5.0), 1)
            urgency = 'Düşük'
    else:
        water_amount = 0.0
        urgency = 'Gerekli Değil'

    return {
        'irrigation_needed': irrigation_needed,
        'probability': round(probability * 100, 2),
        'water_amount_lm2': water_amount,
        'urgency': urgency,
    }
