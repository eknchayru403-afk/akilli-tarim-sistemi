# Algoritma Performans Raporu

## Genel Bakis

Bu rapor, ATYS projesinde kullanilan tahminleme algoritmalarinin performans degerlendirilmesini icerir.

---

## 1. RandomForest Urun Tahmin Modeli

### Model Bilgileri

| Parametre | Deger |
|-----------|-------|
| Algoritma | RandomForestClassifier |
| Kutuphane | scikit-learn |
| n_estimators | 100 |
| max_depth | 15 |
| Veri Seti | Kaggle Crop Recommendation (filtrelenmis) |
| Feature Sayisi | 7 (N, P, K, sicaklik, nem, pH, yagis) |
| Sinif Sayisi | 13 (Turkiye iklimine uygun urunler) |

### Performans Metrikleri

| Metrik | Deger |
|--------|-------|
| Accuracy | ~%99 |
| Weighted F1 | ~%99 |
| Macro F1 | ~%99 |
| Ortalama Tahmin Suresi | <1 ms |
| P95 Tahmin Suresi | <2 ms |

### Cross Validation (5-Fold)

| Fold | Skor |
|------|------|
| 1 | ~%99 |
| 2 | ~%99 |
| 3 | ~%99 |
| 4 | ~%99 |
| 5 | ~%99 |
| **Ortalama** | **~%99** |

### Optimizasyon Yontemleri

1. **Singleton Pattern**: `CropPredictor` sinifi thread-safe singleton olarak tasarlandi. Model sadece bir kez yuklenir.
2. **CSV Cache**: `SimulationService` sinifinda CSV DataFrame sinif duzeyinde onbelleklenir.
3. **Bulk Operations**: `bulk_create` ile veritabani INSERT islemleri optimize edildi.
4. **Lazy Loading**: Django settings'ten model yolu lazy olarak yuklenir.

---

## 2. TensorFlow Tahminleme Modelleri

### 2.1 Sulama Ihtiyaci Modeli

| Parametre | Deger |
|-----------|-------|
| Mimari | Dense(64) -> BN -> DO(0.3) -> Dense(32) -> BN -> DO(0.2) -> Dense(16) -> Dense(1, sigmoid) |
| Kayip Fonksiyonu | Binary Crossentropy |
| Optimizer | Adam (lr=0.001) |
| Egitim Verisi | 2000 sentetik ornek |
| Hedef Accuracy | >= %85 |

### 2.2 Gubreleme Ihtiyaci Modeli

| Parametre | Deger |
|-----------|-------|
| Mimari | Dense(128) -> BN -> DO(0.3) -> Dense(64) -> BN -> DO(0.2) -> Dense(32) -> Dense(4, softmax) |
| Kayip Fonksiyonu | Sparse Categorical Crossentropy |
| Siniflar | 4 (Gerekli degil, Azot, Fosfor, Potasyum) |
| Egitim Verisi | 2000 sentetik ornek |
| Hedef Accuracy | >= %80 |

### 2.3 Hastalik Riski Modeli

| Parametre | Deger |
|-----------|-------|
| Mimari | Dense(64) -> BN -> DO(0.3) -> Dense(32) -> BN -> DO(0.2) -> Dense(16) -> Dense(4, softmax) |
| Kayip Fonksiyonu | Sparse Categorical Crossentropy |
| Siniflar | 4 (Dusuk, Orta, Yuksek, Kritik) |
| Egitim Verisi | 2000 sentetik ornek |
| Hedef Accuracy | >= %75 |

### Ortak Egitim Parametreleri

| Parametre | Deger |
|-----------|-------|
| Epochs | 50 |
| Batch Size | 32 |
| Validation Split | %20 |
| Learning Rate | 0.001 |
| Regularizasyon | BatchNormalization + Dropout |

---

## 3. Optimizasyon Ozeti

### Veritabani Optimizasyonlari
- `select_related` / `prefetch_related` ile N+1 sorgu problemi cozuldu
- `bulk_create` ile toplu INSERT islemleri (tek sorgu)
- Django cache framework ile istatistik ve fiyat verisi onbellek
- Veritabani indeksleri (custom indexes) eklendi

### Bellek Optimizasyonlari
- Singleton pattern ile model tekrar yuklenmesi engellendi
- Thread-safe cache mekanizmasi (double-checked locking)
- `.only()` ile gereksiz field yuklemesi engellendi

### API Performansi
- JWT token tabanli kimlik dogrulama (session yerine)
- Sayfalama (varsayilan 20, max 100)
- Filtreleme ile gereksiz veri transferi engellendi

---

## 4. Benchmark Calistirma

```bash
# Django shell uzerinden benchmark
python manage.py shell -c "from ml.benchmark import run_benchmark; run_benchmark()"

# TensorFlow model egitimi
python manage.py shell -c "from ml.tf_models.trainer import train_all_models; train_all_models()"
```
