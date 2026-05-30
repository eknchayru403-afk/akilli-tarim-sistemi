"""
TensorFlow model sabitleri — Girdi parametreleri, eşik değerleri ve etiketler.

Bu dosya TF tahminleme modelleri tarafından kullanılan sabit değerleri tanımlar.
"""

# ── Sulama Modeli Sabitleri ──
IRRIGATION_FEATURES = [
    'soil_moisture',    # Toprak nemi (%)
    'temperature',      # Sıcaklık (°C)
    'humidity',         # Hava nemi (%)
    'rainfall',         # Yağış (mm)
    'season_encoded',   # Mevsim (0-3)
    'soil_type_encoded',  # Toprak tipi (0-5)
]

IRRIGATION_LABELS = {
    0: 'Sulama Gerekli Değil',
    1: 'Sulama Gerekli',
}

# Önerilen su miktarı aralıkları (L/m²)
IRRIGATION_WATER_RANGES = {
    'low': (2.0, 5.0),       # Düşük ihtiyaç
    'medium': (5.0, 10.0),   # Orta ihtiyaç
    'high': (10.0, 20.0),    # Yüksek ihtiyaç
}

# ── Gübreleme Modeli Sabitleri ──
FERTILIZATION_FEATURES = [
    'nitrogen',         # Azot (N)
    'phosphorus',       # Fosfor (P)
    'potassium',        # Potasyum (K)
    'ph',               # pH
    'soil_type_encoded',  # Toprak tipi
    'crop_encoded',     # Ürün türü
]

FERTILIZATION_LABELS = {
    0: 'Gübreleme Gerekli Değil',
    1: 'Azotlu Gübre Gerekli',
    2: 'Fosforlu Gübre Gerekli',
    3: 'Potasyumlu Gübre Gerekli',
}

# Gübre miktar önerileri (kg/dekar)
FERTILIZATION_AMOUNTS = {
    1: {'min': 5.0, 'max': 15.0, 'unit': 'kg/dekar'},   # Azot
    2: {'min': 3.0, 'max': 10.0, 'unit': 'kg/dekar'},   # Fosfor
    3: {'min': 4.0, 'max': 12.0, 'unit': 'kg/dekar'},   # Potasyum
}

# ── Hastalık Riski Modeli Sabitleri ──
DISEASE_RISK_FEATURES = [
    'humidity',         # Nem (%)
    'temperature',      # Sıcaklık (°C)
    'rainfall',         # Yağış (mm)
    'crop_encoded',     # Ürün türü
    'season_encoded',   # Mevsim
]

DISEASE_RISK_LABELS = {
    0: 'Düşük Risk',
    1: 'Orta Risk',
    2: 'Yüksek Risk',
    3: 'Kritik Risk',
}

DISEASE_RISK_COLORS = {
    0: 'success',
    1: 'warning',
    2: 'danger',
    3: 'dark',
}

# ── Ortak Encoding'ler ──
SOIL_TYPE_ENCODING = {
    'killi': 0,
    'kumlu': 1,
    'tinli': 2,
    'killi_tinli': 3,
    'kumlu_tinli': 4,
    'limolu': 5,
}

SEASON_ENCODING = {
    'ilkbahar': 0,
    'yaz': 1,
    'sonbahar': 2,
    'kis': 3,
}

CROP_ENCODING = {
    'rice': 0, 'maize': 1, 'chickpea': 2, 'lentil': 3,
    'cotton': 4, 'apple': 5, 'grapes': 6, 'watermelon': 7,
    'pomegranate': 8, 'orange': 9, 'wheat': 10, 'sunflower': 11,
    'mango': 12,
}

# ── Model Dosya Adları ──
IRRIGATION_MODEL_FILE = 'irrigation_model.keras'
FERTILIZATION_MODEL_FILE = 'fertilization_model.keras'
DISEASE_RISK_MODEL_FILE = 'disease_risk_model.keras'

# ── Eğitim Sabitleri ──
DEFAULT_EPOCHS = 50
DEFAULT_BATCH_SIZE = 32
DEFAULT_VALIDATION_SPLIT = 0.2
DEFAULT_LEARNING_RATE = 0.001
