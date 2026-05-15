# TensorFlow Model Dokumantasyonu

## Genel Bakis

ATYS projesinde TensorFlow/Keras ile gelistirilen uc tahminleme modeli bulunmaktadir. Bu modeller, ciftcilere sulama, gubreleme ve hastalik riski konusunda otomatik tavsiye uretmek icin kullanilir.

## Model Mimarileri

### 1. Sulama Ihtiyaci Modeli (`irrigation_model.keras`)

```
Model: irrigation_model
_________________________________________________________________
Layer (type)                Output Shape              Param
=================================================================
dense_1 (Dense)             (None, 64)                448
batch_norm_1                (None, 64)                256
dropout_1 (Dropout)         (None, 64)                0
dense_2 (Dense)             (None, 32)                2080
batch_norm_2                (None, 32)                128
dropout_2 (Dropout)         (None, 32)                0
dense_3 (Dense)             (None, 16)                528
output (Dense)              (None, 1)                 17
=================================================================
Total params: ~3,457
```

**Aktivasyon:** ReLU (gizli), Sigmoid (cikti)
**Kayip:** Binary Crossentropy
**Tip:** Binary classification

### 2. Gubreleme Ihtiyaci Modeli (`fertilization_model.keras`)

```
Model: fertilization_model
_________________________________________________________________
Layer (type)                Output Shape              Param
=================================================================
dense_1 (Dense)             (None, 128)               896
batch_norm_1                (None, 128)               512
dropout_1 (Dropout)         (None, 128)               0
dense_2 (Dense)             (None, 64)                8256
batch_norm_2                (None, 64)                256
dropout_2 (Dropout)         (None, 64)                0
dense_3 (Dense)             (None, 32)                2080
output (Dense)              (None, 4)                 132
=================================================================
Total params: ~12,132
```

**Aktivasyon:** ReLU (gizli), Softmax (cikti)
**Kayip:** Sparse Categorical Crossentropy
**Tip:** Multi-class classification (4 sinif)

### 3. Hastalik Riski Modeli (`disease_risk_model.keras`)

```
Model: disease_risk_model
_________________________________________________________________
Layer (type)                Output Shape              Param
=================================================================
dense_1 (Dense)             (None, 64)                384
batch_norm_1                (None, 64)                256
dropout_1 (Dropout)         (None, 64)                0
dense_2 (Dense)             (None, 32)                2080
batch_norm_2                (None, 32)                128
dropout_2 (Dropout)         (None, 32)                0
dense_3 (Dense)             (None, 16)                528
output (Dense)              (None, 4)                 68
=================================================================
Total params: ~3,444
```

**Aktivasyon:** ReLU (gizli), Softmax (cikti)
**Kayip:** Sparse Categorical Crossentropy
**Tip:** Multi-class classification (4 sinif)

---

## Egitim Veri Seti

Tum modeller **sentetik veri** ile egitilmistir. Sentetik veri, tarim bilimsel kurallara dayali puanlama sistemi ile etiketlenmistir.

### Veri Uretim Sureci

1. Feature degerleri `numpy.random.uniform` ile uretilir
2. Her ornek icin bir risk/ihtiyac skoru hesaplanir
3. Skor esik degerlere gore sinifa atanir
4. Deterministik seed (`np.random.seed`) ile tekrarlanabilirlik saglanir

### Ornek Sayilari

| Model | Egitim | Validasyon | Toplam |
|-------|--------|------------|--------|
| Sulama | 1600 | 400 | 2000 |
| Gubreleme | 1600 | 400 | 2000 |
| Hastalik | 1600 | 400 | 2000 |

---

## Hiperparametre Secimleri

| Parametre | Deger | Neden |
|-----------|-------|-------|
| Learning Rate | 0.001 | Adam optimizer varsayilani, kucuk veri setinde stabil |
| Batch Size | 32 | Kucuk-orta veri seti icin uygun |
| Epochs | 50 | Early overfitting olmadan yeterli konverjans |
| Dropout | 0.2-0.3 | Overfitting onleme |
| BatchNorm | Evet | Egitim stabilizasyonu |

---

## Egitim Sureci

### Komut
```python
from ml.tf_models.trainer import train_all_models
results = train_all_models(epochs=50)
```

### Beklenen Cikti
```
Sulama modeli: accuracy=~90%, val_accuracy=~87%
Gubreleme modeli: accuracy=~85%, val_accuracy=~82%
Hastalik riski modeli: accuracy=~80%, val_accuracy=~78%
```

---

## Dosya Yapisi

```
ml/
├── __init__.py
├── constants.py          # RF model sabitleri
├── data_loader.py        # CSV veri yukleme
├── predictor.py          # RF CropPredictor (Singleton)
├── trainer.py            # RF model egitimi
├── benchmark.py          # Performans olcumu
├── saved_models/
│   ├── crop_model.pkl              # Egitilmis RF model
│   ├── irrigation_model.keras      # TF sulama modeli
│   ├── fertilization_model.keras   # TF gubreleme modeli
│   └── disease_risk_model.keras    # TF hastalik modeli
└── tf_models/
    ├── __init__.py
    ├── constants.py          # TF sabitleri
    ├── irrigation_model.py   # Sulama modeli
    ├── fertilization_model.py # Gubreleme modeli
    ├── disease_risk_model.py  # Hastalik riski modeli
    └── trainer.py            # TF egitim pipeline
```

## TensorFlow Versiyon

- **Minimum:** TensorFlow >= 2.16
- **Onerilne:** TensorFlow 2.18+
- **GPU Destegi:** Opsiyonel (CPU ile calisir)
