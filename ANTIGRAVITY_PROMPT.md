# Antigravity Master Prompt — Akıllı Tarım Yönetim Sistemi (ATYS)

> **Bu dosya, Antigravity AI agent'ının projeyi baştan sona inşa etmesi için hazırlanmış ana referans prompt'udur.**
> **Her görev tamamlandığında `projeakisi.md` dosyası güncellenmelidir.**

---

## 1. PROJE TANIMI

Simülasyon tabanlı, yapay zeka destekli bir tarım yönetim sistemi. Fiziksel sensör/IoT donanımı YOK. Tüm veriler Kaggle veri setinden simüle edilir.

**Amaç:** Tarlaların toprak değerlerini (N, P, K, pH, sıcaklık, nem, yağış) analiz ederek en uygun ürünü önermek ve tahmini verim/kazanç hesaplamak.

**İki ana senaryo:**
- **Senaryo A — Boş Tarla:** Toprak analizi → Scikit-learn ile ürün önerisi → Verim + kazanç tahmini
- **Senaryo B — Ekili Tarla:** Mevcut toprak + hava verileri → AI bakım tavsiyesi (sulama, gübreleme)

---

## 2. TEKNOLOJİ STACK'İ (KESİNLEŞMİŞ)

| Katman | Teknoloji | Versiyon | Not |
|--------|-----------|----------|-----|
| Backend Framework | Django | 5.x | Django REST Framework ile API desteği |
| Veritabanı | PostgreSQL | 15+ | Django ORM ile |
| ML | Scikit-learn | 1.x | RandomForest veya GradientBoosting |
| Veri İşleme | Pandas, NumPy | latest | CSV okuma, veri filtreleme |
| Model Serialization | joblib | latest | Eğitilmiş modeli kaydetme |
| Frontend | Django Templates + Bootstrap 5 + HTMX | - | SPA hissi veren server-rendered UI |
| Auth | Django built-in auth | - | Session-based |
| Environment | python-decouple veya django-environ | - | .env yönetimi |
| Test | pytest-django | - | Unit + integration testler |

### KULLANILMAYACAK TEKNOLOJİLER:
- ~~TensorFlow~~ → Scikit-learn yeterli
- ~~MQTT~~ → Fiziksel sensör yok
- ~~FastAPI~~ → Django tercih edildi (hocanın talebi)
- ~~Flutter~~ → İlk fazda kapsam dışı, Django web UI yeterli
- ~~Canlı borsa/fiyat API'si~~ → Statik prices.json
- ~~OpenWeatherMap API~~ → v1'de statik/placeholder hava verisi

---

## 3. VERİ KAYNAKLARI

### 3.1 Kaggle Crop Recommendation Dataset
- **Kaynak:** `Crop_recommendation.csv`
- **Kolonlar:** N, P, K, temperature, humidity, ph, rainfall, label
- **Filtreleme:** Sadece Türkiye iklimine uygun mahsuller:
  - `rice` → Çeltik/Pirinç
  - `maize` → Mısır
  - `chickpea` → Nohut
  - `lentil` → Mercimek
  - `cotton` → Pamuk
  - `apple` → Elma
  - `grapes` → Üzüm
  - `watermelon` → Karpuz
  - `pomegranate` → Nar
  - `orange` → Portakal
  - `mango` → (opsiyonel, Akdeniz bölgesi)
  - Ek olarak Buğday ve Ayçiçeği satırları yoksa sentetik olarak eklenecek (Türkiye'nin en yaygın ürünleri)

### 3.2 Statik Fiyat Verisi (prices.json)
```json
{
  "bugday":     {"fiyat_tl_kg": 9.50,  "label_en": "wheat",       "birim": "kg"},
  "misir":      {"fiyat_tl_kg": 7.80,  "label_en": "maize",       "birim": "kg"},
  "pamuk":      {"fiyat_tl_kg": 32.00, "label_en": "cotton",      "birim": "kg"},
  "aycicegi":   {"fiyat_tl_kg": 18.50, "label_en": "sunflower",   "birim": "kg"},
  "pirinc":     {"fiyat_tl_kg": 45.00, "label_en": "rice",        "birim": "kg"},
  "nohut":      {"fiyat_tl_kg": 55.00, "label_en": "chickpea",    "birim": "kg"},
  "mercimek":   {"fiyat_tl_kg": 48.00, "label_en": "lentil",      "birim": "kg"},
  "elma":       {"fiyat_tl_kg": 15.00, "label_en": "apple",       "birim": "kg"},
  "uzum":       {"fiyat_tl_kg": 25.00, "label_en": "grapes",      "birim": "kg"},
  "karpuz":     {"fiyat_tl_kg": 5.00,  "label_en": "watermelon",  "birim": "kg"},
  "nar":        {"fiyat_tl_kg": 20.00, "label_en": "pomegranate", "birim": "kg"},
  "portakal":   {"fiyat_tl_kg": 12.00, "label_en": "orange",      "birim": "kg"}
}
```

### 3.3 Verim Katsayıları (yield_data.json)
Her ürün için hektar başına ortalama verim (kg/ha) referans değerleri:
```json
{
  "bugday": 3500, "misir": 8000, "pamuk": 1800, "aycicegi": 2200,
  "pirinc": 7500, "nohut": 1500, "mercimek": 1200, "elma": 25000,
  "uzum": 10000, "karpuz": 40000, "nar": 15000, "portakal": 20000
}
```

### 3.4 Hava Durumu (Statik Placeholder — v1)
Şehir bazlı sabit veri döndürülecek. API entegrasyonu v2'de.

---

## 4. VERİTABANI ŞEMASI (PostgreSQL)

```sql
-- Kullanıcılar (Django auth_user tablosu extend edilecek)
-- Django'nun AbstractUser modeli kullanılacak

-- Tarlalar
CREATE TABLE fields (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    area_decar DECIMAL(10,2),          -- Dekar cinsinden alan
    soil_type VARCHAR(50),             -- Killi, Kumlu, Tınlı vb.
    status VARCHAR(20) DEFAULT 'empty', -- 'empty' veya 'planted'
    current_crop VARCHAR(50),           -- Ekili ürün (planted ise)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Toprak Analizleri (sensör simülasyonu + manuel giriş)
CREATE TABLE soil_analyses (
    id SERIAL PRIMARY KEY,
    field_id INTEGER REFERENCES fields(id) ON DELETE CASCADE,
    nitrogen DECIMAL(6,2) NOT NULL,    -- N değeri
    phosphorus DECIMAL(6,2) NOT NULL,  -- P değeri
    potassium DECIMAL(6,2) NOT NULL,   -- K değeri
    temperature DECIMAL(5,2),          -- Sıcaklık °C
    humidity DECIMAL(5,2),             -- Nem %
    ph DECIMAL(4,2),                   -- pH değeri
    rainfall DECIMAL(6,2),             -- Yağış mm
    source VARCHAR(20) DEFAULT 'manual', -- 'manual' veya 'simulation'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Ürün Önerileri (ML sonuçları)
CREATE TABLE crop_recommendations (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES soil_analyses(id) ON DELETE CASCADE,
    crop_name VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,2),            -- Model güven skoru %
    estimated_yield_kg DECIMAL(10,2),   -- Tahmini verim kg
    estimated_revenue_tl DECIMAL(12,2), -- Tahmini kazanç TL
    rank INTEGER DEFAULT 1,             -- 1=en iyi, 2, 3...
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bakım Tavsiyeleri (ekili tarlalar için)
CREATE TABLE care_recommendations (
    id SERIAL PRIMARY KEY,
    field_id INTEGER REFERENCES fields(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(30),    -- 'irrigation', 'fertilization', 'pesticide'
    message TEXT NOT NULL,
    priority VARCHAR(10) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    is_done BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Ürün Fiyatları (statik, admin güncelleyebilir)
CREATE TABLE crop_prices (
    id SERIAL PRIMARY KEY,
    crop_name VARCHAR(50) UNIQUE NOT NULL,
    crop_name_tr VARCHAR(50) NOT NULL,
    price_per_kg DECIMAL(8,2) NOT NULL,
    avg_yield_per_hectare DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. PROJE KLASÖR YAPISI

```
akıllı-tarım-sistemi/
├── backend/                          # Django projesi kök dizini
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── pytest.ini
│   │
│   ├── config/                       # Django proje ayarları
│   │   ├── __init__.py
│   │   ├── settings.py               # Ana ayarlar (tek dosya, split opsiyonel)
│   │   ├── urls.py                   # Root URL conf
│   │   └── wsgi.py
│   │
│   ├── apps/                         # Django uygulamaları
│   │   ├── __init__.py
│   │   │
│   │   ├── accounts/                 # Kullanıcı yönetimi
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── models.py             # CustomUser (AbstractUser)
│   │   │   ├── forms.py              # Login, Register formları
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests.py
│   │   │
│   │   ├── fields/                   # Tarla yönetimi
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── models.py             # Field modeli
│   │   │   ├── forms.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py           # İş mantığı (SRP)
│   │   │   └── tests.py
│   │   │
│   │   ├── analysis/                 # Toprak analizi + ML önerileri
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── models.py             # SoilAnalysis, CropRecommendation
│   │   │   ├── forms.py              # Manuel giriş formu
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py           # Simülasyon + ML çağrısı
│   │   │   └── tests.py
│   │   │
│   │   ├── weather/                  # Hava durumu (v1: statik)
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── services.py           # Statik veri servisi
│   │   │
│   │   └── dashboard/                # Ana sayfa / özet görünüm
│   │       ├── __init__.py
│   │       ├── views.py
│   │       ├── urls.py
│   │       └── services.py           # Aggregation logic
│   │
│   ├── ml/                           # Makine öğrenmesi modülü
│   │   ├── __init__.py
│   │   ├── trainer.py                # Model eğitimi script
│   │   ├── predictor.py              # Tahmin servisi (Singleton pattern)
│   │   ├── data_loader.py            # CSV yükleme + filtreleme
│   │   ├── constants.py              # Türkiye mahsul mapping, eşik değerleri
│   │   └── saved_models/
│   │       └── .gitkeep
│   │
│   ├── data/                         # Statik veri dosyaları
│   │   ├── crop_recommendation.csv   # Kaggle veri seti
│   │   ├── prices.json               # Ürün fiyatları
│   │   └── yield_data.json           # Verim katsayıları
│   │
│   ├── templates/                    # Django HTML şablonları
│   │   ├── base.html                 # Master layout
│   │   ├── components/               # Tekrar eden UI parçaları
│   │   │   ├── navbar.html
│   │   │   ├── sidebar.html
│   │   │   ├── alert.html
│   │   │   └── loading.html
│   │   ├── accounts/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── dashboard/
│   │   │   └── index.html
│   │   ├── fields/
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   └── form.html
│   │   └── analysis/
│   │       ├── form.html             # Toprak analizi giriş
│   │       ├── result.html           # Ürün önerisi sonuç
│   │       └── history.html          # Geçmiş analizler
│   │
│   └── static/                       # Statik dosyalar
│       ├── css/
│       │   └── main.css
│       ├── js/
│       │   └── main.js
│       └── images/
│           └── logo.png
│
├── docs/                             # Proje dokümanları
├── Hafta_1/
├── Hafta_3/
├── ARCHITECTURE.md
├── projeakisi.md
├── README.md
└── .gitignore
```

---

## 6. YAZILIM PRENSİPLERİ (ZORUNLU)

### 6.1 SOLID
- **S (Single Responsibility):** Her Django app tek bir iş yapar. İş mantığı `services.py` içinde, view sadece HTTP request/response yönetir.
- **O (Open/Closed):** Yeni ürün eklemek için kod değişikliği gerektirmeyen yapı. prices.json + CSV güncelle, sistem otomatik adapte olsun.
- **L (Liskov Substitution):** Base service sınıfları türetilebilir olsun.
- **I (Interface Segregation):** Büyük servisler yerine küçük, odaklı servisler (SimulationService, PredictionService, PriceService ayrı).
- **D (Dependency Inversion):** View'lar doğrudan model/DB çağırmasın → Service katmanı üzerinden.

### 6.2 DRY (Don't Repeat Yourself)
- Ortak model alanları `TimeStampedModel` abstract base class'ında.
- Template parçaları `components/` altında `{% include %}` ile.
- Ortak validasyonlar mixins ile.

### 6.3 Clean Code
- Fonksiyon/metot 20 satırı geçmesin.
- Değişken/fonksiyon isimleri açıklayıcı olsun (İngilizce kod, Türkçe UI).
- Magic number kullanma → constants.py.
- Her modül docstring ile başlasın.
- Type hints kullan.

### 6.4 Diğer
- **KISS:** Gereksiz abstraction yapma. İlk fazda basit tut.
- **YAGNI:** İhtiyaç olmayan feature ekleme.
- **Separation of Concerns:** Template → View → Service → Model → DB

---

## 7. ZORUNLU KURALLAR (Antigravity İçin)

1. **Her görev öncesi** bu prompt dosyasını ve `projeakisi.md` dosyasını oku.
2. **Her görev sonrası** `projeakisi.md` dosyasına yapılan değişikliğin özetini ekle.
3. **Kod yazarken** İngilizce değişken/fonksiyon adları, Türkçe UI metinleri.
4. **Dosya başına max 300 satır.** Geçerse böl.
5. **print() kullanma.** Django `logging` modülünü kullan.
6. **API key hardcode etme.** `.env` dosyası + `django-environ` kullan.
7. **Her model'e `__str__` metodu ekle.**
8. **Migrations dosyalarını commit et.**
9. **Test yaz.** En az her service fonksiyonu için bir unit test.
10. **Type hints kullan.** `def get_recommendation(analysis_id: int) -> list[dict]:`

---

## 8. DETAYLI AKTİVİTE AKIŞI (Kullanıcı Perspektifinden)

### Akış 1: Kayıt + Giriş
1. Kullanıcı `/register` sayfasından kayıt olur
2. `/login` sayfasından giriş yapar
3. Dashboard'a yönlendirilir

### Akış 2: Yeni Tarla Ekleme
1. Dashboard'da "Tarla Ekle" butonuna tıklar
2. Form: Ad, konum, alan (dekar), toprak tipi
3. Tarla "boş" statüsünde oluşturulur
4. Dashboard'da tarla kartı görünür

### Akış 3: Toprak Analizi (Manuel Giriş)
1. Tarla detay sayfasında "Toprak Analizi Yap" butonuna tıklar
2. Form: N, P, K, sıcaklık, nem, pH, yağış değerlerini girer
3. "Analiz Et" butonuna tıklar
4. Backend: Değerler DB'ye kaydedilir → ML modeli çalışır → Top 3 ürün önerisi döner
5. Sonuç sayfası: Önerilen ürünler, güven skoru, tahmini verim (kg), tahmini kazanç (TL)

### Akış 4: Veri Simüle Et (Kaggle CSV)
1. Tarla detay sayfasında "Veri Simüle Et" butonuna tıklar
2. Backend: CSV'den rastgele bir satır seçilir
3. Değerler otomatik olarak toprak analizi formuna doldurulur VEYA doğrudan analiz yapılır
4. Sonuç sayfası: Akış 3 ile aynı

### Akış 5: Ekili Tarla Bakım Tavsiyesi
1. Tarla "planted" statüsündeyse detay sayfasında mevcut durum gösterilir
2. Toprak + hava verileri baz alınarak bakım tavsiyeleri listelenir
3. "Sulama gerekli", "Gübreleme zamanı" gibi AI tavsiyeleri kartlar halinde

### Akış 6: Geçmiş Analizler
1. Menüden "Geçmiş" sayfasına gider
2. Tüm yapılan analizlerin listesi (tarih, tarla, önerilen ürün, skor)
3. Detaya tıklayınca analiz sonucu tekrar görüntülenir

### Akış 7: Fiyat Tablosu
1. Profil veya ayrı sayfa üzerinden TMO fiyatlarını görüntüler
2. Admin kullanıcı fiyatları güncelleyebilir (Django admin veya özel form)

---

## 9. ML MODELİ DETAYLARI

### Eğitim Pipeline:
```python
# ml/trainer.py
1. CSV yükle (pandas)
2. Türkiye mahsullerini filtrele (TURKEY_CROPS listesi)
3. Feature engineering (gerekirse)
4. Train/test split (%80/%20)
5. Model: RandomForestClassifier veya GradientBoostingClassifier
6. Eğit + accuracy raporu
7. joblib ile kaydet → ml/saved_models/crop_model.pkl
```

### Tahmin Pipeline:
```python
# ml/predictor.py
1. Kayıtlı modeli yükle (uygulama başlangıcında bir kez)
2. Input: [N, P, K, temperature, humidity, ph, rainfall]
3. predict_proba() ile tüm sınıfların olasılıklarını al
4. Top 3 ürünü döndür: [(crop_name, confidence), ...]
5. Her ürün için prices.json'dan fiyat, yield_data.json'dan verim çek
6. Tahmini kazanç = verim * fiyat * (tarla_alanı / 10)  # dekar→hektar
```

### Bakım Tavsiyesi Mantığı:
```python
# Rule-based system (v1'de ML değil, kural tabanlı)
if soil.humidity < 30:
    → "Toprak nemi kritik seviyede. Acil sulama gerekli." (priority: critical)
if soil.ph < 5.5:
    → "Toprak asitliği yüksek. Kireçleme önerilir." (priority: high)
if soil.nitrogen < 20:
    → "Azot seviyesi düşük. Azotlu gübre uygulanmalı." (priority: medium)
# ... vb. kural seti
```

---

## 10. UI / TEMPLATE DETAYLARI

### Tasarım Sistemi:
- **CSS Framework:** Bootstrap 5 (CDN)
- **İkonlar:** Bootstrap Icons veya Font Awesome
- **Dinamik Güncelleme:** HTMX (sayfa yenilemeden AJAX-benzeri işlemler)
- **Renk Paleti:**
  - Primary: `#2E7D32` (koyu yeşil)
  - Secondary: `#4CAF50` (açık yeşil)
  - Warning: `#FF9800` (turuncu)
  - Danger: `#D32F2F` (kırmızı)
  - Background: `#F5F5F5`
  - Surface: `#FFFFFF`

### Sayfa Listesi:
| URL Pattern | Sayfa | Template |
|-------------|-------|----------|
| `/accounts/login/` | Giriş | accounts/login.html |
| `/accounts/register/` | Kayıt | accounts/register.html |
| `/` | Dashboard | dashboard/index.html |
| `/fields/` | Tarla Listesi | fields/list.html |
| `/fields/<id>/` | Tarla Detay | fields/detail.html |
| `/fields/create/` | Tarla Ekleme | fields/form.html |
| `/fields/<id>/analyze/` | Toprak Analizi | analysis/form.html |
| `/fields/<id>/simulate/` | Simülasyon (POST) | JSON → redirect |
| `/analysis/<id>/result/` | Analiz Sonucu | analysis/result.html |
| `/analysis/history/` | Geçmiş | analysis/history.html |
| `/prices/` | Fiyat Tablosu | prices/list.html |
| `/profile/` | Profil | accounts/profile.html |

---

## 11. .env DOSYASI ÖRNEĞİ
```
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
DATABASE_URL=postgres://postgres:password@localhost:5432/akilli_tarim
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 12. requirements.txt
```
Django>=5.0,<6.0
psycopg2-binary>=2.9
django-environ>=0.11
scikit-learn>=1.4
pandas>=2.2
numpy>=1.26
joblib>=1.3
django-htmx>=1.17
django-crispy-forms>=2.1
crispy-bootstrap5>=2024.2
pytest-django>=4.8
gunicorn>=22.0
```

---

## 13. GÜVENLİK KONTROL LİSTESİ
- [ ] SECRET_KEY `.env`'de
- [ ] DEBUG production'da False
- [ ] CSRF middleware aktif
- [ ] `@login_required` tüm korumalı view'larda
- [ ] SQL injection yok (ORM kullan, raw SQL yazma)
- [ ] XSS koruması (Django auto-escape aktif)
- [ ] Kullanıcı sadece kendi tarlalarını görebilir (queryset filtreleme)

---

## ÖNEMLİ NOT

Bu prompt, projenin tüm sınırlarını ve gereksinimlerini tanımlar. Antigravity:
1. Bu dosyayı referans alarak çalışacak
2. YOL HARİTASI'ndaki (aşağıdaki dosya) görevleri sırayla uygulayacak
3. Her tamamlanan görevi `projeakisi.md`'ye loglayacak
4. Kapsam dışı feature eklenmeyecek (YAGNI)
5. Çalışan kodu bozmayacak

