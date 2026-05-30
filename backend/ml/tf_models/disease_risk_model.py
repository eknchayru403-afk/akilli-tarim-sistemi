"""
Hastalık Riski Tahmin Modeli (TensorFlow/Keras).

Nem, sıcaklık, yağış, ürün türü ve mevsime göre
bitki hastalık riskini tahmin eder.

Girdiler:
    - humidity (float): Nem (%)
    - temperature (float): Sıcaklık (°C)
    - rainfall (float): Yağış (mm)
    - crop_encoded (int): Ürün türü (0-12)
    - season_encoded (int): Mevsim (0-3)

Çıktılar:
    - risk_level (int): 0=Düşük, 1=Orta, 2=Yüksek, 3=Kritik
    - risk_label (str): Risk etiketi
    - confidence (float): Güven skoru (%)
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


def build_disease_risk_model(input_dim: int = 5, num_classes: int = 4):
    """
    Hastalık riski tahmin modelini oluşturur.

    Multi-class classification — 4 risk seviyesi.

    Args:
        input_dim: Girdi boyutu.
        num_classes: Sınıf sayısı.

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
        layers.Dense(num_classes, activation='softmax', name='output'),
    ], name='disease_risk_model')

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'],
    )

    logger.info("Hastalık riski modeli oluşturuldu: %d parametre", model.count_params())
    return model


def generate_disease_training_data(n_samples: int = 2000) -> tuple:
    """
    Hastalık riski modeli için sentetik eğitim verisi üretir.

    Risk etiketleme kuralları:
    - Yüksek nem + yüksek sıcaklık → Yüksek/Kritik risk
    - Düşük nem + normal sıcaklık → Düşük risk
    - Çok yüksek yağış → Risk artar

    Args:
        n_samples: Örnek sayısı.

    Returns:
        (X, y) tuple.
    """
    np.random.seed(44)

    humidity = np.random.uniform(20, 95, n_samples)
    temperature = np.random.uniform(5, 45, n_samples)
    rainfall = np.random.uniform(0, 500, n_samples)
    crop = np.random.randint(0, 13, n_samples)
    season = np.random.randint(0, 4, n_samples)

    X = np.column_stack([humidity, temperature, rainfall, crop, season])

    # Kural tabanlı etiketleme
    y = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        risk_score = 0

        # Nem faktörü
        if humidity[i] > 80:
            risk_score += 3
        elif humidity[i] > 65:
            risk_score += 2
        elif humidity[i] > 50:
            risk_score += 1

        # Sıcaklık faktörü
        if 25 <= temperature[i] <= 35:
            risk_score += 2  # Patojenlere uygun
        elif temperature[i] > 35:
            risk_score += 1  # Stres riski

        # Yağış faktörü
        if rainfall[i] > 200:
            risk_score += 2
        elif rainfall[i] > 100:
            risk_score += 1

        # Mevsim faktörü
        if season[i] == 1:  # Yaz — böcek riski
            risk_score += 1
        elif season[i] == 0:  # İlkbahar — mantar riski
            risk_score += 1

        # Risk seviyesi belirleme
        if risk_score >= 6:
            y[i] = 3  # Kritik
        elif risk_score >= 4:
            y[i] = 2  # Yüksek
        elif risk_score >= 2:
            y[i] = 1  # Orta
        else:
            y[i] = 0  # Düşük

    logger.info(
        "Hastalık riski eğitim verisi üretildi: %d örnek | "
        "Düşük: %d, Orta: %d, Yüksek: %d, Kritik: %d",
        n_samples,
        int((y == 0).sum()),
        int((y == 1).sum()),
        int((y == 2).sum()),
        int((y == 3).sum()),
    )
    return X, y


def predict_disease_risk(model, humidity, temperature, rainfall,
                         crop_encoded, season_encoded) -> dict:
    """
    Hastalık riski tahmini yapar.

    Args:
        model: Eğitilmiş Keras modeli.
        humidity: Nem (%).
        temperature: Sıcaklık (°C).
        rainfall: Yağış (mm).
        crop_encoded: Ürün kodu.
        season_encoded: Mevsim kodu.

    Returns:
        Tahmin sonucu dict.
    """
    from .constants import DISEASE_RISK_COLORS, DISEASE_RISK_LABELS

    features = np.array([[
        humidity, temperature, rainfall, crop_encoded, season_encoded,
    ]])

    probabilities = model.predict(features, verbose=0)[0]
    predicted_class = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_class]) * 100

    return {
        'risk_level': predicted_class,
        'risk_label': DISEASE_RISK_LABELS[predicted_class],
        'risk_color': DISEASE_RISK_COLORS[predicted_class],
        'confidence': round(confidence, 2),
        'probabilities': {
            DISEASE_RISK_LABELS[i]: round(float(p) * 100, 2)
            for i, p in enumerate(probabilities)
        },
    }
