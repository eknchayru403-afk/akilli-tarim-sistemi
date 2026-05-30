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

---
## 6 Haftalık Görev Dağılım Tabloları

Bu bölümde projenin 6 haftalık sürecindeki detaylı görev dağılımı, üye sorumlulukları ve iş durumları tablolar halinde sunulmuştur.

### 📅 1. Hafta (Başlangıç ve Altyapı)
| Üye | Görev Başlığı | Durum | Tahmini Süre | Gerçekleşen |
| :--- | :--- | :--- | :---: | :---: |
| **Hayrunnisa Ekinci** | Sistem Mimarisi ve Gereksinim Analizi Dokümanının Hazırlanması | Tamamlandı | - | - |
| **Betül Bilhan** | MQTT Broker Kurulumu ve Sensör Veri Akışı Protokolünün Belirlenmesi | Tamamlandı | - | - |
| **İrfan Duman** | Django Proje Yapısı ve Geliştirme Ortamının Kurulumu | Tamamlandı | - | - |
| **İsmet Mert Uysal** | TensorFlow Ortamının Kurulumu ve Tarımsal Veri Seti Araştırması | Tamamlandı | - | - |
| **Wessam Alhamidi** | API Endpoint Planlaması ve Django REST Framework Kurulumu | Tamamlandı | - | - |
| **Ahmed Osman Alsotef** | PostgreSQL Veritabanı Şeması ve Bağlantı Konfigürasyonu | Tamamlandı | - | - |

### 📅 2. Hafta (Optimizasyon ve Performans)
| Üye | Görev Başlığı | Durum | Tahmini Süre | Gerçekleşen |
| :--- | :--- | :--- | :---: | :---: |
| **Hayrunnisa Ekinci** | Hızlı Veri Seri Hale Getirme/Seri Halden Çıkarma Kütüphanesini Entegre Et | Tamamlandı | - | - |
| **Betül Bilhan** | Veritabanı Bağlantı Havuzu Testlerini Gerçekleştir | Tamamlandı | - | - |
| **İrfan Duman** | Veri Erişim Katmanını Optimize Et | Tamamlandı | - | - |
| **İsmet Mert Uysal** | Önbellek Tutarlılığı Mekanizmasını Test Et | Tamamlandı | - | - |
| **Wessam Alhamidi** | Günlükleme (Logging) Mekanizmasını İyileştir | Tamamlandı | - | - |
| **Ahmed Osman Alsotef** | Bellek Yönetimi Optimizasyonlarını Uygula | Tamamlandı | - | - |

### 📅 3. Hafta (Tasarım ve Modelleme)
| Üye | Görev Başlığı | Durum | Tahmini Süre | Gerçekleşen |
| :--- | :--- | :--- | :---: | :---: |
| **Hayrunnisa Ekinci** | Mobil Uygulama Arayüz Tasarımı | Tamamlandı | - | - |
| **Betül Bilhan** | Tahminleme Algoritması Tasarımı | Tamamlandı | - | - |
| **İrfan Duman** | Veritabanı Şema Tasarımı | Tamamlandı | - | - |
| **İsmet Mert Uysal** | MQTT Entegrasyon Mimarisi Tasarımı | Tamamlandı | - | - |
| **Wessam Alhamidi** | Raporlama ve Analiz Modülü Tasarımı | Tamamlandı | - | - |
| **Ahmed Osman Alsotef** | Web Arayüzü Wireframe Tasarımı | Tamamlandı | - | - |

### 📅 4. Hafta (Geliştirme ve Entegrasyon)
| Üye | Görev Başlığı | Durum | Tahmini Süre | Gerçekleşen |
| :--- | :--- | :--- | :---: | :---: |
| **Hayrunnisa Ekinci** | Tarla Yönetim Dashboard'u ve Gerçek Zamanlı Veri Görselleştirme | Tamamlandı | - | - |
| **Betül Bilhan** | Django REST Framework ile Sensör ve Tahmin API Endpoint'leri | Tamamlandı | - | - |
| **İrfan Duman** | MQTT Broker Entegrasyonu ve Gerçek Zamanlı Sensör Veri Akışı | Tamamlandı | - | - |
| **İsmet Mert Uysal** | PostgreSQL Zaman Serisi Veri Yapısı ve Sorgu Optimizasyonu | Tamamlandı | - | - |
| **Wessam Alhamidi** | Python Tabanlı Gübreleme Optimizasyon Algoritması Geliştirme | Tamamlandı | - | - |
| **Ahmed Osman Alsotef** | TensorFlow ile LSTM Tabanlı Sulama İhtiyacı Tahmin Modeli | Tamamlandı | - | - |

### 📅 5. Hafta (Gelişmiş Özellikler ve Güvenlik)
| Üye | Görev Başlığı | Durum | Tahmini Süre | Gerçekleşen |
| :--- | :--- | :--- | :---: | :---: |
| **Hayrunnisa Ekinci** | Gerçek Zamanlı Sensör Verisi Görselleştirme Dashboard'u Geliştirme | Tamamlandı | - | - |
| **Betül Bilhan** | Django ile PDF ve Excel Formatında Tarımsal Raporlama Modülü | Tamamlandı | - | - |
| **İrfan Duman** | TensorFlow Sulama Tahmin Modelinde Hiperparametre Optimizasyonu | Tamamlandı | - | - |
| **İsmet Mert Uysal** | PostgreSQL Zaman Serisi Verileri İçin Tablo Partitioning ve Index Optimizasyonu | Tamamlandı | - | - |
| **Wessam Alhamidi** | Mobil Uygulama Entegrasyonu için JWT Tabanlı API Güvenlik Katmanı | Tamamlandı | - | - |
| **Ahmed Osman Alsotef** | MQTT Sensör Akışında Çok Kanallı Anomali Tespiti | Tamamlandı | - | - |

### 📅 6. Hafta (Test, Dokümantasyon ve Kapanış)
| Üye | Görev Başlığı | Durum | Tahmini Süre | Gerçekleşen |
| :--- | :--- | :--- | :---: | :---: |
| **Hayrunnisa Ekinci** | Raporlama Araçları Veri Doğruluğu Kontrolü ve Kapanış Sunumu Tasarımı | Tamamlandı | - | - |
| **Betül Bilhan** | Tahminleme Algoritmaları Performans Optimizasyonu ve Dokümantasyonu | Tamamlandı | - | - |
| **İrfan Duman** | Veri Toplama Modülü Son Test ve Kapanış Dokümantasyonu | Tamamlandı | - | - |
| **İsmet Mert Uysal** | Mobil Uygulama Entegrasyonu Son Testleri ve Kullanıcı Kılavuzu Hazırlama | Tamamlandı | - | - |
| **Wessam Alhamidi** | Proje Genel Dokümantasyonunun Tamamlanması ve Son Kontroller | Tamamlandı | - | - |
| **Ahmed Osman Alsotef** | Web Arayüzü Kullanıcı Deneyimi (UX) Testleri ve Kapanış Raporu | Tamamlandı | - | - |
