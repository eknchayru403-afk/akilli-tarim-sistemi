# Tahminleme Algoritması Tasarımı Dokümantasyonu

## Genel Bakış

Akıllı Tarım Yönetim Sistemi (ATYS), iki katmanlı bir tahminleme mimarisi kullanır:

1. **scikit-learn RandomForest** — Ürün önerisi (mevcut)
2. **TensorFlow/Keras Neural Network** — Sulama, gübreleme ve hastalık riski tahmini (yeni)

## Mimari Genel Görünüm

```
                   ┌──────────────────────┐
                   │    Sensör Verileri    │
                   │  (N, P, K, pH, nem,  │
                   │   sıcaklık, yağış)   │
                   └──────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼────────┐
     │  RandomForest  │ │ TensorFlow │ │  TensorFlow   │
     │  Ürün Önerisi  │ │  Modelleri │ │  Modelleri    │
     │  (scikit-learn) │ │ (Sulama +  │ │  (Hastalık    │
     │                │ │  Gübreleme)│ │   Riski)      │
     └────────┬──────┘ └─────┬──────┘ └──────┬────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                   ┌──────────▼───────────┐
                   │   Bakım Tavsiyeleri   │
                   │  (CareRecommendation) │
                   └──────────────────────┘
```

---

## 1. Ürün Tahmin Modeli (Mevcut — scikit-learn)

### Model: RandomForestClassifier
- **Kütüphane:** scikit-learn
- **Algoritma:** Random Forest (n_estimators=100, max_depth=15)
- **Dosya:** `ml/trainer.py`, `ml/predictor.py`
- **Kayıtlı Model:** `ml/saved_models/crop_model.pkl`

### Girdi Parametreleri

| Parametre | Tip | Aralık | Birim |
|-----------|-----|--------|-------|
| Nitrogen (N) | float | 0–200 | mg/kg |
| Phosphorus (P) | float | 0–200 | mg/kg |
| Potassium (K) | float | 0–300 | mg/kg |
| Temperature | float | -10–50 | °C |
| Humidity | float | 0–100 | % |
| pH | float | 0–14 | - |
| Rainfall | float | 0–2000 | mm |

### Çıktı
- **crop_name**: Önerilen ürün (İngilizce)
- **crop_name_tr**: Türkçe ürün adı
- **confidence**: Güven skoru (%)
- **estimated_yield_kg**: Tahmini verim (kg)
- **estimated_revenue_tl**: Tahmini kazanç (TL)

### Doğruluk Metrikleri
- Accuracy: ~%99 (Kaggle Crop Recommendation veri seti)
- Stratified train/test split: %80/%20

---

## 2. Sulama İhtiyacı Tahmin Modeli (Yeni — TensorFlow)

### Model Mimarisi
```
Input(6) → Dense(64, ReLU) → BN → Dropout(0.3)
         → Dense(32, ReLU) → BN → Dropout(0.2)
         → Dense(16, ReLU) → Dense(1, Sigmoid)
```

### Dosya: `ml/tf_models/irrigation_model.py`

### Girdi Parametreleri

| Parametre | Tip | Aralık | Açıklama |
|-----------|-----|--------|----------|
| soil_moisture | float | 10–90 | Toprak nemi (%) |
| temperature | float | 5–45 | Sıcaklık (°C) |
| humidity | float | 20–95 | Hava nemi (%) |
| rainfall | float | 0–300 | Yağış (mm) |
| season_encoded | int | 0–3 | Mevsim (ilkbahar=0, yaz=1, sonbahar=2, kış=3) |
| soil_type_encoded | int | 0–5 | Toprak tipi |

### Çıktı Formatı
```json
{
    "irrigation_needed": true,
    "probability": 78.5,
    "water_amount_lm2": 8.3,
    "urgency": "Normal"
}
```

### Etiketleme Kuralları
- Toprak nemi < %30 → +3 puan
- Sıcaklık > 30°C → +2 puan
- Yağış < 30mm → +2 puan
- Hava nemi < %40 → +1 puan
- Toplam ≥ 4 → Sulama Gerekli

---

## 3. Gübreleme İhtiyacı Tahmin Modeli (Yeni — TensorFlow)

### Model Mimarisi
```
Input(6) → Dense(128, ReLU) → BN → Dropout(0.3)
         → Dense(64, ReLU)  → BN → Dropout(0.2)
         → Dense(32, ReLU)  → Dense(4, Softmax)
```

### Dosya: `ml/tf_models/fertilization_model.py`

### Girdi Parametreleri

| Parametre | Tip | Aralık | Açıklama |
|-----------|-----|--------|----------|
| nitrogen | float | 5–150 | Azot (N) değeri |
| phosphorus | float | 5–150 | Fosfor (P) değeri |
| potassium | float | 5–250 | Potasyum (K) değeri |
| ph | float | 4.0–9.5 | pH değeri |
| soil_type_encoded | int | 0–5 | Toprak tipi |
| crop_encoded | int | 0–12 | Ürün türü |

### Çıktı Sınıfları

| Sınıf | Etiket | Önerilen Miktar |
|-------|--------|-----------------|
| 0 | Gübreleme Gerekli Değil | — |
| 1 | Azotlu Gübre Gerekli | 5–15 kg/dekar |
| 2 | Fosforlu Gübre Gerekli | 3–10 kg/dekar |
| 3 | Potasyumlu Gübre Gerekli | 4–12 kg/dekar |

---

## 4. Hastalık Riski Tahmin Modeli (Yeni — TensorFlow)

### Model Mimarisi
```
Input(5) → Dense(64, ReLU) → BN → Dropout(0.3)
         → Dense(32, ReLU) → BN → Dropout(0.2)
         → Dense(16, ReLU) → Dense(4, Softmax)
```

### Dosya: `ml/tf_models/disease_risk_model.py`

### Girdi Parametreleri

| Parametre | Tip | Aralık | Açıklama |
|-----------|-----|--------|----------|
| humidity | float | 20–95 | Nem (%) |
| temperature | float | 5–45 | Sıcaklık (°C) |
| rainfall | float | 0–500 | Yağış (mm) |
| crop_encoded | int | 0–12 | Ürün türü |
| season_encoded | int | 0–3 | Mevsim |

### Çıktı Sınıfları

| Seviye | Etiket | Renk |
|--------|--------|------|
| 0 | Düşük Risk | 🟢 success |
| 1 | Orta Risk | 🟡 warning |
| 2 | Yüksek Risk | 🔴 danger |
| 3 | Kritik Risk | ⚫ dark |

---

## Eğitim Pipeline'ı

### Sentetik Veri Üretimi
Her model için 2000 sentetik örnek üretilir. Etiketler, tarım bilimsel kural tabanlı puanlama sistemiyle belirlenir.

### Eğitim Komutu
```python
from ml.tf_models.trainer import train_all_models
results = train_all_models(epochs=50)
```

### Eğitim Sabitleri
| Parametre | Değer |
|-----------|-------|
| Epochs | 50 |
| Batch Size | 32 |
| Validation Split | %20 |
| Learning Rate | 0.001 |
| Optimizer | Adam |

---

## Güvenilirlik Metrikleri

| Metrik | Açıklama |
|--------|----------|
| Accuracy | Genel doğruluk oranı |
| Validation Accuracy | Doğrulama seti doğruluk oranı |
| Loss | Eğitim kaybı |
| Precision | Kesinlik (binary modeller için) |
| Recall | Duyarlılık (binary modeller için) |

### Kabul Kriterleri
- **Ürün Tahmini (RF):** Accuracy ≥ %95
- **Sulama Tahmini (TF):** Accuracy ≥ %85
- **Gübreleme Tahmini (TF):** Accuracy ≥ %80
- **Hastalık Riski (TF):** Accuracy ≥ %75
