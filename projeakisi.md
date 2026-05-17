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
