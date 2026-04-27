# Proje Akışı ve Haftalık İlerleme

Bu dosya, ekibimizin haftalık ilerlemesini ve görev dağılımlarını takip etmek için oluşturulmuştur.

## 1. Hafta (9 - 15 Mart)
* **[Hayrunnisa Ekinci] (Scrum Master):** GitHub reposu oluşturuldu, `projeakisi.md` dosyası hazırlandı ve iş akışı planlandı.Proje yönetimi ve işbirliği için kullanılacak araç olan Jira kuruldu. Ekip üyelerinin bu aracı nasıl kullanacağı ile ilgili kullanım kılavuzu hazırlandı.
* **[Betül Bilhan]:** Proje için en uygun teknolojiler araştırıldı, rapor hazırlandı ve öneriler sunuldu. 
* **[İrfan Duman]:** (Görev bekleniyor)
* **[Ahmed Osman]:** (Görev bekleniyor)
* **[İsmet Mert Uysal]:** (Görev bekleniyor)

---
## 3. Hafta (22 - 28 Mart)
[Hayrunnisa Ekinci] (Scrum Master): - Sensör verilerini analiz eden ve tarımsal faaliyetleri (sulama, havalandırma) optimize eden karar destek algoritması geliştirildi.
Hocanın direktifi doğrultusunda projenin çalışabilirliğini kanıtlayan sanal tarla simülasyonu (Java) kodlandı ve GitHub'a yüklendi.
Hafta dökümanları Hafta_1 klasörü altında arşivlenerek repo düzeni sağlandı.

[Betül Bilhan]: (Görev bekleniyor)
[İrfan Duman]: (Görev bekleniyor)
[Ahmed Osman]: (Görev bekleniyor)
[İsmet Mert Uysal]: (Görev bekleniyor)
[Wessam Alhamidi]: (Görev bekleniyor)

---
## Proje Teknoloji Kararı (21 Nisan 2025)

### Kesinleşen Tech Stack:
- **Backend:** Python + Django 5.x
- **Veritabanı:** PostgreSQL 15+
- **ML:** Scikit-learn (RandomForest)
- **Frontend:** Django Templates + Bootstrap 5 + HTMX
- **Veri:** Kaggle Crop Recommendation CSV (Türkiye filtreli) + statik prices.json

### Elenen Teknolojiler:
- ~~TensorFlow~~ (Scikit-learn yeterli)
- ~~FastAPI~~ (Django tercih edildi — hocanın talebi)
- ~~Flutter~~ (İlk fazda kapsam dışı)
- ~~MQTT~~ (Fiziksel sensör yok)
- ~~Spring Boot / Java~~ (Python/Django'ya geçildi)

### Oluşturulan Dosyalar:
- `ANTIGRAVITY_PROMPT.md` — Antigravity AI agent için kapsamlı referans prompt
- `YOL_HARITASI.md` — 7 fazlı detaylı görev planı (Faz 0–6)

### Antigravity Görev Talimatı:
Antigravity, `ANTIGRAVITY_PROMPT.md` dosyasını referans alarak `YOL_HARITASI.md`'deki görevleri sırayla uygulayacak. Her görev tamamlandığında bu dosyaya (`projeakisi.md`) log düşecek.

---
## Antigravity v1 İmplementasyonu (21 Nisan 2026)

### FAZ 0 — Proje Altyapısı ✅
- Django 5.x projesi `backend/config` olarak oluşturuldu
- `django-environ` ile `.env` yönetimi entegre edildi
- 5 Django app oluşturuldu: `accounts`, `fields`, `analysis`, `weather`, `dashboard`
- SQLite veritabanı konfigüre edildi (MySQL geçiş hazır)
- Tüm bağımlılıklar `requirements.txt`'e yazılıp kuruldu

### FAZ 1 — Veritabanı Modelleri ✅
- `CustomUser(AbstractUser)` — şehir, telefon alanları ile
- `TimeStampedModel` abstract base class (DRY prensibi)
- `Field` modeli — tarla CRUD, toprak tipi, durum yönetimi
- `SoilAnalysis` — N, P, K, sıcaklık, nem, pH, yağış
- `CropRecommendation` — ML sonuçları (güven skoru, verim, kazanç)
- `CareRecommendation` — kural tabanlı bakım tavsiyeleri
- `CropPrice` — statik ürün fiyatları
- Tüm modellere `__str__`, admin registration eklendi

### FAZ 2 — Veri Katmanı ✅
- `ml/constants.py` — Türkiye mahsul mapping, eşik değerleri
- `ml/data_loader.py` — CSV yükleme + filtreleme + sentetik veri (buğday/ayçiçeği)
- `data/prices.json` — 12 ürün TL/kg fiyatları
- `data/yield_data.json` — Hektar verim katsayıları
- `load_prices` management command — JSON → DB (12 ürün yüklendi)
- `SimulationService` — CSV'den rastgele sensör verisi simülasyonu

### FAZ 3 — Makine Öğrenmesi ✅
- `ml/trainer.py` — RandomForestClassifier (accuracy: %99)
- `ml/predictor.py` — CropPredictor (Singleton + predict_proba)
- `CareAdvisor` — kural tabanlı bakım tavsiye motoru (nem, pH, N, P, K, sıcaklık, yağış)
- `train_model` management command

### FAZ 4 — Backend Views ✅
- Auth: Login, Register, Logout, Profile
- Dashboard: Stat kartları, hava durumu, uyarılar, son analizler
- Field CRUD: List, Detail, Create, Update, Delete
- Analysis: Manuel giriş, simülasyon, sonuç, geçmiş, ürün ekme
- Price: Fiyat tablosu
- Weather: Statik hava durumu (12 şehir)

### FAZ 5 — Frontend Templates ✅
- `base.html` — Bootstrap 5 + HTMX + sidebar navigasyon
- Modern yeşil tema (primary: #2E7D32, Inter font)
- Auth sayfaları (login/register — gradient arka plan)
- Dashboard (stat kartlar, hava widget, tarla grid, uyarılar)
- Tarla sayfaları (detay, form, silme onay)
- Analiz sayfaları (form, sonuç kartları, geçmiş tablosu)
- Fiyat tablosu, hava durumu sayfası
- Responsive tasarım (mobil sidebar toggle)
