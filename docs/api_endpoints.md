# ATYS — REST API Endpoint Referansı

**Base URL:** `http://localhost:8000/api/v1/`  
**Auth:** JWT Bearer Token (`Authorization: Bearer <access_token>`)  
**Format:** JSON (`Content-Type: application/json`)

---

## 🔐 Kimlik Doğrulama

| Method | Endpoint | Auth | Açıklama |
|--------|----------|------|----------|
| `POST` | `/api/v1/token/` | ❌ | Username + password ile access/refresh token al |
| `POST` | `/api/v1/token/refresh/` | ❌ | Refresh token ile yeni access token al |
| `POST` | `/api/v1/token/verify/` | ❌ | Token geçerliliğini doğrula |

### Token Alma — `POST /api/v1/token/`

**İstek:**
```json
{
  "username": "ahmet_farmer",
  "password": "gizlisifre123"
}
```

**Yanıt (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

> Access token süresi: **60 dakika** | Refresh token süresi: **7 gün**

### Token Yenileme — `POST /api/v1/token/refresh/`

**İstek:**
```json
{ "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Yanıt (200 OK):**
```json
{ "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

---

## 🌾 Tarla Yönetimi (`/api/v1/fields/`)

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/v1/fields/` | Kullanıcının tarlalarını listele |
| `POST` | `/api/v1/fields/` | Yeni tarla oluştur |
| `GET` | `/api/v1/fields/{id}/` | Tarla detayı |
| `PUT` | `/api/v1/fields/{id}/` | Tarla güncelle (tam) |
| `PATCH` | `/api/v1/fields/{id}/` | Tarla güncelle (kısmi) |
| `DELETE` | `/api/v1/fields/{id}/` | Tarla sil |
| `GET` | `/api/v1/fields/{id}/analyses/` | Tarlaya ait toprak analizleri |
| `GET` | `/api/v1/fields/{id}/sensors/` | Tarlaya ait sensör verileri |
| `GET` | `/api/v1/fields/{id}/predictions/` | Tarlaya ait tahmin sonuçları |

### Filtreler (`GET /api/v1/fields/`)

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `status` | string | `empty` veya `planted` |
| `soil_type` | string | `killi`, `kumlu`, `tinli`, `killi_tinli`, `kumlu_tinli`, `limolu` |
| `name` | string | İsme göre kısmi arama |
| `created_after` | datetime | Bu tarihten sonra oluşturulanlar |
| `created_before` | datetime | Bu tarihten önce oluşturulanlar |
| `ordering` | string | `created_at`, `area_decar`, `name` (başına `-` ekle: ters sıra) |
| `page`, `page_size` | int | Sayfalama (max 100) |

### Yeni Tarla — `POST /api/v1/fields/`

**İstek:**
```json
{
  "name": "Kuzey Tarla",
  "location": "Konya, Türkiye",
  "area_decar": 50.00,
  "soil_type": "tinli",
  "status": "empty",
  "current_crop": ""
}
```

**Yanıt (201 Created):**
```json
{
  "id": 1,
  "user": { "id": 1, "username": "ahmet", "first_name": "Ahmet", "last_name": "Yılmaz", "city": "Konya" },
  "name": "Kuzey Tarla",
  "location": "Konya, Türkiye",
  "area_decar": "50.00",
  "area_hectare": 5.0,
  "soil_type": "tinli",
  "soil_type_display": "Tınlı",
  "status": "empty",
  "status_display": "Boş",
  "current_crop": "",
  "created_at": "2025-05-19T20:00:00Z",
  "updated_at": "2025-05-19T20:00:00Z"
}
```

---

## 📡 Sensör Verileri (`/api/v1/sensors/`)

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/v1/sensors/` | Tüm sensör verilerini listele |
| `POST` | `/api/v1/sensors/` | Yeni sensör verisi oluştur |
| `GET` | `/api/v1/sensors/{id}/` | Sensör verisi detayı |
| `PUT` | `/api/v1/sensors/{id}/` | Sensör verisi güncelle |
| `PATCH` | `/api/v1/sensors/{id}/` | Sensör verisi kısmi güncelle |
| `DELETE` | `/api/v1/sensors/{id}/` | Sensör verisi sil |
| `POST` | `/api/v1/sensors/data/` | **Hızlı sensör veri gönderme** |
| `GET` | `/api/v1/sensors/latest/` | Her tarladan en son okuma |
| `GET` | `/api/v1/sensors/readings/` | Ham MQTT okumaları (read-only) |

### Sensör Verisi Gönder — `POST /api/v1/sensors/data/`

**İstek:**
```json
{
  "field": 1,
  "humidity": 65.5,
  "temperature": 22.3,
  "soil_moisture": 40.0,
  "plant_water_consumption": 3.5,
  "soil_ph": 6.8,
  "light_intensity": 12000
}
```

**Yanıt (201 Created):**
```json
{
  "id": 42,
  "field": 1,
  "field_name": "Kuzey Tarla",
  "field_location": "Konya, Türkiye",
  "humidity": "65.50",
  "temperature": "22.30",
  "soil_moisture": "40.00",
  "plant_water_consumption": "3.50",
  "soil_ph": "6.80",
  "light_intensity": "12000.00",
  "created_at": "2025-05-19T20:00:00Z",
  "updated_at": "2025-05-19T20:00:00Z"
}
```

### Alan Validasyonları

| Alan | Kural |
|------|-------|
| `humidity` | `0 ≤ değer ≤ 100` |
| `temperature` | `-50 ≤ değer ≤ 60` |
| `soil_ph` | `0 ≤ değer ≤ 14` |
| `field` | Tarla istek sahibine ait olmalı |

### Filtreler (`GET /api/v1/sensors/`)

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `field_id` | int | Tarla ID'si |
| `min_humidity` / `max_humidity` | float | Nem aralığı |
| `min_temperature` / `max_temperature` | float | Sıcaklık aralığı |
| `min_soil_ph` / `max_soil_ph` | float | pH aralığı |
| `date_from` / `date_to` | datetime | Tarih aralığı |
| `ordering` | string | `created_at`, `temperature`, `humidity`, `soil_ph` |

---

## 🧪 Toprak Analizi (`/api/v1/soil-analyses/`)

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/v1/soil-analyses/` | Toprak analizlerini listele |
| `POST` | `/api/v1/soil-analyses/` | Yeni toprak analizi oluştur |
| `GET` | `/api/v1/soil-analyses/{id}/` | Analiz detayı |
| `PUT/PATCH` | `/api/v1/soil-analyses/{id}/` | Analiz güncelle |
| `DELETE` | `/api/v1/soil-analyses/{id}/` | Analiz sil |

### Yeni Toprak Analizi — `POST /api/v1/soil-analyses/`

**İstek:**
```json
{
  "field": 1,
  "nitrogen": 85.0,
  "phosphorus": 42.0,
  "potassium": 43.0,
  "temperature": 21.5,
  "humidity": 72.0,
  "ph": 6.5,
  "rainfall": 202.0,
  "source": "manual"
}
```

**`source` değerleri:** `manual`, `simulation`, `mqtt`

---

## 🌱 Tahmin Sonuçları (`/api/v1/predictions/`)

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/v1/predictions/` | Tüm tahminleri listele |
| `GET` | `/api/v1/predictions/{id}/` | Tahmin detayı |

> ⚠️ **Read-only:** Tahminler ML model tarafından üretilir, doğrudan oluşturulamaz/silinemez.

### Yanıt Örneği

```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "analysis": 5,
      "analysis_date": "2025-05-15T10:30:00Z",
      "field_name": "Kuzey Tarla",
      "crop_name": "rice",
      "crop_name_tr": "Pirinç",
      "confidence": "87.50",
      "estimated_yield_kg": "4500.00",
      "estimated_revenue_tl": "135000.00",
      "rank": 1,
      "created_at": "2025-05-15T10:30:00Z"
    }
  ]
}
```

### Filtreler

| Parametre | Açıklama |
|-----------|----------|
| `field_id` | Tarla ID |
| `analysis_id` | Analiz ID |
| `crop_name` | Ürün adı (kısmi arama) |
| `min_confidence` | Minimum güven skoru (%) |
| `date_from`, `date_to` | Tarih aralığı |
| `ordering` | `created_at`, `confidence`, `rank` |

---

## 🩺 Bakım Tavsiyeleri (`/api/v1/care/`)

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/v1/care/` | Tüm bakım tavsiyelerini listele |
| `GET` | `/api/v1/care/{id}/` | Tavsiye detayı |
| `PATCH` | `/api/v1/care/{id}/` | Tavsiyeyi tamamlandı işaretle |

### Tamamlandı İşaretle — `PATCH /api/v1/care/{id}/`

**İstek:**
```json
{ "is_done": true }
```

---

## 📦 Sayfalama Yapısı

Tüm liste yanıtları aşağıdaki formatta döner:

```json
{
  "count": 150,
  "total_pages": 8,
  "current_page": 1,
  "page_size": 20,
  "next": "http://localhost:8000/api/v1/sensors/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

---

## ❗ Hata Yanıtları

| HTTP Kodu | Durum | Açıklama |
|-----------|-------|----------|
| `400` | Bad Request | Validasyon hatası (eksik/hatalı alan) |
| `401` | Unauthorized | Token eksik veya geçersiz |
| `403` | Forbidden | Kaynağa erişim yetkisi yok (başka kullanıcının kaynağı) |
| `404` | Not Found | Kaynak bulunamadı |
| `405` | Method Not Allowed | İzin verilmeyen HTTP metodu |
| `429` | Too Many Requests | Rate limit aşıldı |
| `500` | Server Error | Sunucu hatası |

### 400 Örneği (Validasyon Hatası)

```json
{
  "humidity": ["Nem değeri 0-100 arasında olmalıdır."],
  "soil_ph": ["pH değeri 0-14 arasında olmalıdır."]
}
```

### 401 Örneği

```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 🧪 Postman ile Test

1. [Postman koleksiyonunu](../postman/ATYS_API.postman_collection.json) Postman'e import edin
2. Collection Variables'da `BASE_URL`'yi ayarlayın (`http://localhost:8000`)
3. **"🔐 Kimlik Doğrulama > Token Al"** isteğini çalıştırın — token otomatik kaydedilir
4. Diğer istekleri test edin

---

*Son güncelleme: 2026-05-19 | ATYS API v1*
