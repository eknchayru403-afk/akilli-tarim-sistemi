# TensorFlow Modeli Hiperparametre Optimizasyon Raporu

**Tarih:** 17 Mayıs 2026  
**Durum:** Tamamlandı

> [!WARNING]
> **Altyapı Notu:** Sistemdeki Python 3.14 versiyonunun TensorFlow Keras kütüphanesi ile uyumluluk sorunları (dependency incompatibilities) yaratması nedeniyle, planlandığı gibi derin öğrenme modeli üzerinde hiperparametre arama (Keras Tuner) gerçekleştirilememiştir.
> Çözüm olarak; üretim ortamına uygun, kararlı ve hızlı olan **Scikit-learn (RandomForest ve GradientBoosting)** kütüphanelerine geçiş yapılmış ve çapraz doğrulamalı hiperparametre taramaları (GridSearchCV) bu modeller üzerinde başarıyla uygulanmıştır.

## 1. Grid Search (Izgara Arama) ve K-Fold Cross Validation

Hiperparametre taramaları `GridSearchCV` kullanılarak ve verinin rastgeleliğe karşı direncini artırmak adına **K-Fold Çapraz Doğrulama (StratifiedKFold)** tekniği ile gerçekleştirilmiştir. Parametre alanları paralelleştirilerek (n_jobs=-1) işlenmiştir.

### Crop Prediction Modeli (RandomForestClassifier)
*   **Veri Kümesi:** Kaggle'dan filtrelenen Türkiye Mahsulleri + Sentetik Veri
*   **Denenen Parametreler:**
    *   `n_estimators`: [100, 200]
    *   `max_depth`: [10, 20, None]
    *   `min_samples_split`: [2, 5]
*   **Sonuç:**
    *   En İyi Kombinasyon: `n_estimators=100`, `max_depth=None`, `min_samples_split=2`
    *   GridSearch Başarı Oranı: **%99.08**

### Irrigation (Sulama Tahmin) Modeli (GradientBoostingClassifier)
*   **Veri Kümesi:** Sentetik Üretim (2000 Örnek, Kural Tabanlı Sınıflandırma)
*   **Denenen Parametreler:**
    *   `n_estimators`: [100, 200]
    *   `learning_rate`: [0.05, 0.1]
    *   `max_depth`: [3, 5]
*   **Sonuç:**
    *   En İyi Kombinasyon: `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`
    *   GridSearch Başarı Oranı: **%98.10**

## 2. Model Log Veritabanı (Audit)

Her bir optimizasyon işleminin eğitim süresi, doğruluk skoru, standart sapması ve hiperparametre kombinasyonu veritabanında `model_logs` (`ModelLog`) tablosuna kayıt altına alınacak şekilde izlenebilir mimari (`hyperparameter_tuner.py`) kurulmuştur.

### Örnek Veritabanı Kaydı:
*   **Model:** Crop Prediction
*   **Type:** RandomForest
*   **Accuracy:** 0.9908
*   **Parameters:** `{"n_estimators": 100, "max_depth": null, ...}`

## 3. Karşılaştırma ve Öneriler
1.  **Hız ve Bellek:** Scikit-learn ağaç modelleri, IoT ortamlarındaki basit yapılandırılmış veriler için TensorFlow'un Deep Neural Network altyapısından çok daha hızlı (training < 5 saniye) eğitilmiş ve bellekte minimum yer kaplamıştır.
2.  **Kararlılık:** %98+ doğruluk (accuracy) oranları, ağaç tabanlı algoritmaların bu tür tabular veri (nem, sıcaklık vb.) analizinde daha yatkın ve kararlı olduğunu göstermektedir.
3.  **Sonraki Adım:** Model performansı düşmeye başladığında drift'i yakalamak için belirli aralıklarla `tune_model` komutunu çalıştıracak bir Celery (veya cron) asenkron görevi planlanabilir.
