"""
Gübreleme İhtiyacı Tahmin Modeli (TensorFlow/Keras).

N, P, K değerleri, pH, toprak tipi ve ürün türüne göre
hangi tür gübreleme gerektiğini tahmin eder.

Girdiler:
    - nitrogen (float): Azot (N) değeri
    - phosphorus (float): Fosfor (P) değeri
    - potassium (float): Potasyum (K) değeri
    - ph (float): pH değeri
    - soil_type_encoded (int): Toprak tipi (0-5)
    - crop_encoded (int): Ürün türü (0-12)

Çıktılar:
    - fertilization_type (int): 0=Gerekli değil, 1=Azot, 2=Fosfor, 3=Potasyum
    - amount (float): Önerilen gübre miktarı (kg/dekar)
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


def build_fertilization_model(input_dim: int = 6, num_classes: int = 4):
    """
    Gübreleme tahmin modelini oluşturur.

    Multi-class classification — 4 sınıf (gerekmez + 3 gübre tipi).

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
        layers.Dense(128, activation='relu', name='dense_1'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu', name='dense_2'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu', name='dense_3'),
        layers.Dense(num_classes, activation='softmax', name='output'),
    ], name='fertilization_model')

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'],
    )

    logger.info("Gübreleme modeli oluşturuldu: %d parametre", model.count_params())
    return model


def generate_fertilization_training_data(n_samples: int = 2000) -> tuple:
    """
    Gübreleme modeli için sentetik eğitim verisi üretir.

    Etiketleme kuralları:
    - N düşük → Azotlu gübre (1)
    - P düşük → Fosforlu gübre (2)
    - K düşük → Potasyumlu gübre (3)
    - Hepsi yeterli → Gerekmez (0)

    Args:
        n_samples: Örnek sayısı.

    Returns:
        (X, y) tuple.
    """
    np.random.seed(43)

    nitrogen = np.random.uniform(5, 150, n_samples)
    phosphorus = np.random.uniform(5, 150, n_samples)
    potassium = np.random.uniform(5, 250, n_samples)
    ph = np.random.uniform(4.0, 9.5, n_samples)
    soil_type = np.random.randint(0, 6, n_samples)
    crop = np.random.randint(0, 13, n_samples)

    X = np.column_stack([nitrogen, phosphorus, potassium, ph, soil_type, crop])

    # Kural tabanlı etiketleme
    y = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        deficiencies = []
        if nitrogen[i] < 20:
            deficiencies.append(1)  # Azot eksik
        if phosphorus[i] < 15:
            deficiencies.append(2)  # Fosfor eksik
        if potassium[i] < 15:
            deficiencies.append(3)  # Potasyum eksik

        if not deficiencies:
            y[i] = 0  # Gerekmez
        else:
            # En kritik eksikliği seç
            y[i] = deficiencies[0]

    logger.info(
        "Gübreleme eğitim verisi üretildi: %d örnek | "
        "Gerekmez: %d, Azot: %d, Fosfor: %d, Potasyum: %d",
        n_samples,
        int((y == 0).sum()),
        int((y == 1).sum()),
        int((y == 2).sum()),
        int((y == 3).sum()),
    )
    return X, y


def predict_fertilization(model, nitrogen, phosphorus, potassium,
                          ph, soil_type_encoded, crop_encoded) -> dict:
    """
    Gübreleme tahmini yapar.

    Args:
        model: Eğitilmiş Keras modeli.
        nitrogen: Azot değeri.
        phosphorus: Fosfor değeri.
        potassium: Potasyum değeri.
        ph: pH değeri.
        soil_type_encoded: Toprak tipi kodu.
        crop_encoded: Ürün kodu.

    Returns:
        Tahmin sonucu dict.
    """
    from .constants import FERTILIZATION_AMOUNTS, FERTILIZATION_LABELS

    features = np.array([[
        nitrogen, phosphorus, potassium,
        ph, soil_type_encoded, crop_encoded,
    ]])

    probabilities = model.predict(features, verbose=0)[0]
    predicted_class = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_class]) * 100

    result = {
        'fertilization_type': predicted_class,
        'fertilization_label': FERTILIZATION_LABELS[predicted_class],
        'confidence': round(confidence, 2),
        'probabilities': {
            FERTILIZATION_LABELS[i]: round(float(p) * 100, 2)
            for i, p in enumerate(probabilities)
        },
    }

    # Miktar önerisi ekle
    if predicted_class in FERTILIZATION_AMOUNTS:
        amount_info = FERTILIZATION_AMOUNTS[predicted_class]
        result['recommended_amount'] = {
            'min': amount_info['min'],
            'max': amount_info['max'],
            'unit': amount_info['unit'],
        }
    else:
        result['recommended_amount'] = None

    return result
