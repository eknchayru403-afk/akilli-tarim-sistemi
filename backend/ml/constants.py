"""
ML sabitleri — Türkiye mahsul mapping ve eşik değerleri.

Bu dosya ML modeli ve servisler tarafından kullanılan
sabit değerleri merkezi olarak tanımlar.
"""

# Türkiye iklimine uygun mahsuller (EN → TR mapping)
TURKEY_CROPS: dict[str, str] = {
    'rice': 'Pirinç',
    'maize': 'Mısır',
    'chickpea': 'Nohut',
    'lentil': 'Mercimek',
    'cotton': 'Pamuk',
    'apple': 'Elma',
    'grapes': 'Üzüm',
    'watermelon': 'Karpuz',
    'pomegranate': 'Nar',
    'orange': 'Portakal',
    'wheat': 'Buğday',
    'sunflower': 'Ayçiçeği',
    'mango': 'Mango',
}

# TR → EN ters mapping
TURKEY_CROPS_TR_TO_EN: dict[str, str] = {v: k for k, v in TURKEY_CROPS.items()}

# CSV'de kullanılacak mahsul listesi
TURKEY_CROP_LABELS: list[str] = list(TURKEY_CROPS.keys())

# Feature sütunları (ML modeli input sırası)
FEATURE_COLUMNS: list[str] = [
    'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
]

# Toprak analizi eşik değerleri (bakım tavsiyesi için)
THRESHOLDS = {
    'humidity_low': 30.0,
    'humidity_high': 80.0,
    'ph_low': 5.5,
    'ph_high': 8.5,
    'nitrogen_low': 20.0,
    'phosphorus_low': 15.0,
    'potassium_low': 15.0,
    'temperature_high': 38.0,
    'temperature_low': 5.0,
    'rainfall_low': 50.0,
}

# Top-N ürün önerisi sayısı
TOP_N_RECOMMENDATIONS: int = 3

# Model dosya adı
MODEL_FILENAME: str = 'crop_model.pkl'
