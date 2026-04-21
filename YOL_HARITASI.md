# YOL HARİTASI — Akıllı Tarım Yönetim Sistemi

> Her görev tamamlandığında `projeakisi.md` dosyasına log düşülecek.
> Görevler sırayla yapılacak; bir önceki tamamlanmadan sonrakine geçilmeyecek.

---

## FAZ 0: PROJE ALTYAPISI (Temel Kurulum)

### Görev 0.1 — Django Projesi Oluşturma
- `backend/` klasöründe Django projesi oluştur (`config` adıyla)
- `apps/` dizini oluştur
- `requirements.txt` dosyasını yaz ve bağımlılıkları kur
- `.env.example` ve `.env` dosyalarını oluştur
- `config/settings.py`'de `django-environ` entegrasyonu
- **Çıktı:** `python manage.py runserver` hatasız çalışır

### Görev 0.2 — PostgreSQL Bağlantısı
- PostgreSQL'de `akilli_tarim` veritabanını oluştur (talimat ver)
- `settings.py`'de DB konfigürasyonu (`.env`'den okunsun)
- `python manage.py migrate` başarılı
- **Çıktı:** Django admin `/admin` açılır

### Görev 0.3 — Proje İskeleti
- Django app'lerini oluştur: `accounts`, `fields`, `analysis`, `weather`, `dashboard`
- `INSTALLED_APPS`'e ekle
- Her app'te boş `urls.py`, `services.py` dosyaları oluştur
- `config/urls.py`'de root URL include'ları
- **Çıktı:** Tüm app'ler registered, boş URL'ler çalışır

---

## FAZ 1: VERİTABANI MODELLERİ

### Görev 1.1 — CustomUser Modeli
- `accounts/models.py`: `AbstractUser` extend eden `CustomUser`
- `AUTH_USER_MODEL = 'accounts.CustomUser'` settings'e ekle
- Alanlar: username, email, first_name, last_name, city, phone (opsiyonel)
- `__str__`, admin registration
- Migration oluştur + uygula
- **Çıktı:** Superuser oluşturulabilir

### Görev 1.2 — Field (Tarla) Modeli
- `fields/models.py`: `Field` modeli
- Alanlar: user (FK), name, location, area_decar, soil_type (choices), status (empty/planted), current_crop
- `TimeStampedModel` abstract base (created_at, updated_at) → tüm modeller kullanacak
- `__str__`, admin registration
- Migration

### Görev 1.3 — Analysis Modelleri
- `analysis/models.py`:
  - `SoilAnalysis`: field (FK), N, P, K, temperature, humidity, ph, rainfall, source (manual/simulation)
  - `CropRecommendation`: analysis (FK), crop_name, crop_name_tr, confidence, estimated_yield_kg, estimated_revenue_tl, rank
  - `CareRecommendation`: field (FK), recommendation_type, message, priority, is_done
- Admin registration + `__str__`
- Migration

### Görev 1.4 — CropPrice Modeli
- `analysis/models.py`'e ekle veya ayrı: `CropPrice`
- Alanlar: crop_name, crop_name_tr, price_per_kg, avg_yield_per_hectare, updated_at
- Django management command: `load_prices` → `prices.json`'dan DB'ye yükle
- Migration
- **Çıktı:** `python manage.py load_prices` çalışır, 12 ürün DB'de

---

## FAZ 2: VERİ KATMANI

### Görev 2.1 — Kaggle CSV Hazırlığı
- `backend/data/crop_recommendation.csv` yerleştir
- `ml/data_loader.py`: CSV yükleme + Türkiye mahsullerini filtreleme fonksiyonu
- `ml/constants.py`: `TURKEY_CROPS` dict (en→tr mapping), eşik değerleri
- Unit test: filtreleme doğru çalışıyor mu?

### Görev 2.2 — Statik Veri Dosyaları
- `backend/data/prices.json` oluştur (Bölüm 3.2'deki içerik)
- `backend/data/yield_data.json` oluştur (Bölüm 3.3'teki içerik)
- Management command: `load_prices` → JSON'dan DB'ye

### Görev 2.3 — Simülasyon Servisi
- `analysis/services.py` → `SimulationService` sınıfı
- `simulate_sensor_data(field_id: int) -> SoilAnalysis`:
  - CSV'den rastgele bir satır seç
  - SoilAnalysis kaydı oluştur (source='simulation')
  - Kayıt döndür
- Unit test

---

## FAZ 3: MAKİNE ÖĞRENMESİ MODELİ

### Görev 3.1 — Model Eğitimi
- `ml/trainer.py`:
  - CSV yükle + filtrele (data_loader kullan)
  - RandomForestClassifier eğit
  - Train/test split, accuracy raporu (print + log)
  - joblib ile kaydet → `ml/saved_models/crop_model.pkl`
- Management command: `train_model`
- **Çıktı:** `python manage.py train_model` → model dosyası oluşur, accuracy >= %85

### Görev 3.2 — Tahmin Servisi
- `ml/predictor.py` → `CropPredictor` sınıfı (Singleton)
  - `__init__`: model yükle
  - `predict(n, p, k, temp, humidity, ph, rainfall) -> list[dict]`
  - Top 3 ürün: name, name_tr, confidence
  - Fiyat + verim hesaplama entegrasyonu
- Unit test: bilinen input → beklenen output

### Görev 3.3 — Bakım Tavsiye Motoru
- `analysis/services.py` → `CareAdvisor` sınıfı
- Kural tabanlı sistem:
  - Nem < 30 → Sulama uyarısı (critical)
  - pH < 5.5 veya > 8.5 → Toprak düzenleme (high)
  - N < 20 → Azotlu gübre (medium)
  - Sıcaklık > 38 → Don/sıcak uyarısı (high)
  - vb.
- `generate_care_recommendations(field_id: int) -> list[CareRecommendation]`
- Unit test

---

## FAZ 4: BACKEND VIEWS & İŞ MANTIĞI

### Görev 4.1 — Auth Views
- `accounts/views.py`: Login, Register, Logout views
- `accounts/forms.py`: CustomUserCreationForm, LoginForm
- `accounts/urls.py` URL patterns
- `@login_required` decorator hazırlığı
- **Çıktı:** Kullanıcı kayıt + giriş + çıkış yapabilir

### Görev 4.2 — Dashboard View
- `dashboard/views.py`: Dashboard ana sayfa
- Kullanıcının tarlaları (özet bilgi)
- Son analizler
- Aktif uyarılar
- `dashboard/services.py`: Aggregation logic
- **Çıktı:** Login sonrası dashboard görünür

### Görev 4.3 — Field CRUD Views
- `fields/views.py`: List, Detail, Create, Update, Delete
- `fields/forms.py`: FieldForm (ModelForm)
- `fields/services.py`: İş mantığı
- Kullanıcı sadece kendi tarlalarını görebilir (queryset filtreleme)
- **Çıktı:** Tarla CRUD tam çalışır

### Görev 4.4 — Analysis Views
- `analysis/views.py`:
  - `analyze_form`: Manuel veri giriş formu
  - `simulate_data`: POST → SimulationService çağrısı → otomatik analiz
  - `analysis_result`: ML sonuçlarını göster
  - `analysis_history`: Kullanıcının tüm analizleri
- `analysis/services.py` → `AnalysisService`:
  - `run_analysis(soil_analysis_id) -> list[CropRecommendation]`
  - ML predictor çağır → DB'ye kaydet → döndür
- **Çıktı:** Manuel giriş + simülasyon + sonuç gösterimi çalışır

### Görev 4.5 — Price Views
- Fiyat tablosu listeleme view'ı
- Admin fiyat güncelleme (Django admin yeterli)

### Görev 4.6 — Weather Views (Placeholder)
- `weather/services.py`: Statik hava durumu verisi döndüren servis
- Şehir bazlı dummy data (sıcaklık, nem, durum)
- Dashboard'da hava durumu widget'ı için

---

## FAZ 5: FRONTEND (TEMPLATES + UI)

### Görev 5.1 — Base Template + Layout
- `templates/base.html`: Master layout
  - Bootstrap 5 CDN
  - HTMX CDN
  - Navbar (logo, navigasyon, kullanıcı menüsü)
  - Sidebar (opsiyonel) veya top-nav
  - Content block
  - Footer
  - Messages (Django messages framework)
- `static/css/main.css`: Custom stiller (renk paleti override)
- Responsive tasarım

### Görev 5.2 — Auth Sayfaları
- `templates/accounts/login.html`: Login formu (crispy forms)
- `templates/accounts/register.html`: Register formu
- Yeşil tarım temalı, modern görünüm

### Görev 5.3 — Dashboard Sayfası
- `templates/dashboard/index.html`:
  - Tarla kartları grid (her kart: ad, alan, durum, son analiz)
  - Hava durumu banner (statik)
  - Aksiyon/uyarı kartları
  - "Tarla Ekle" butonu
- HTMX ile partial güncelleme (opsiyonel)

### Görev 5.4 — Tarla Sayfaları
- `templates/fields/list.html`: Tarla listesi
- `templates/fields/detail.html`:
  - Tarla bilgileri
  - "Toprak Analizi Yap" butonu
  - **"Veri Simüle Et"** butonu (Kaggle CSV'den random veri)
  - Son analiz sonuçları
  - Bakım tavsiyeleri (ekili tarla ise)
- `templates/fields/form.html`: Tarla ekleme/düzenleme formu

### Görev 5.5 — Analiz Sayfaları
- `templates/analysis/form.html`:
  - NPK, sıcaklık, nem, pH, yağış input'ları
  - Slider veya number input
  - "Analiz Et" butonu
- `templates/analysis/result.html`:
  - Top 3 ürün önerisi kartları
  - Her kart: Ürün adı, güven skoru (%), tahmini verim (kg), tahmini kazanç (TL)
  - Tarla durumunu "planted" yapma seçeneği
- `templates/analysis/history.html`:
  - Tablo: Tarih, Tarla, Veri Kaynağı, Önerilen Ürün, Skor
  - Filtreleme/sıralama

### Görev 5.6 — Fiyat Tablosu + Profil
- `templates/prices/list.html`: Ürün fiyat tablosu
- `templates/accounts/profile.html`: Kullanıcı profili

---

## FAZ 6: ENTEGRASYON & POLISH

### Görev 6.1 — End-to-End Test
- Tam akış testi: Kayıt → Giriş → Tarla Ekle → Simüle Et → Analiz → Sonuç → Geçmiş
- Edge case: Boş tarla, eksik veri, geçersiz input
- Fix bugs

### Görev 6.2 — Management Commands Özeti
- `python manage.py load_prices` → Fiyat verisi yükle
- `python manage.py train_model` → ML modeli eğit
- `python manage.py createsuperuser` → Admin
- Tümü çalıştırılıp doğrulanacak

### Görev 6.3 — README Güncelleme
- Proje açıklaması
- Kurulum adımları (venv, pip install, migrate, load_prices, train_model, runserver)
- Ekran görüntüleri (opsiyonel)
- API endpoint listesi

### Görev 6.4 — Kod Kalitesi
- Kullanılmayan importları temizle
- Type hints kontrolü
- Docstring kontrolü
- Django `check` ve `test` komutlarını çalıştır

---

## ÖNCELİK SIRASI

| Öncelik | Faz | Tahmini Süre |
|---------|-----|--------------|
| 🔴 Kritik | Faz 0: Altyapı | 1 oturum |
| 🔴 Kritik | Faz 1: Modeller | 1 oturum |
| 🔴 Kritik | Faz 2: Veri Katmanı | 1 oturum |
| 🟠 Yüksek | Faz 3: ML Modeli | 1 oturum |
| 🟠 Yüksek | Faz 4: Backend Views | 2 oturum |
| 🟡 Orta | Faz 5: Frontend | 2 oturum |
| 🟢 Düşük | Faz 6: Entegrasyon | 1 oturum |

**Toplam:** ~9 oturum (her oturum ≈ 1–2 saat)

---

## BAĞIMLILIK GRAFİĞİ

```
Faz 0 (Altyapı)
  └── Faz 1 (Modeller)
       ├── Faz 2 (Veri Katmanı)
       │    └── Faz 3 (ML)
       │         └── Faz 4 (Views) ← Faz 2 + Faz 3 tamamlanınca
       │              └── Faz 5 (Frontend) ← Faz 4 tamamlanınca
       │                   └── Faz 6 (Entegrasyon)
       └── Faz 4.1 (Auth Views) ← Modeller yeterli
```

