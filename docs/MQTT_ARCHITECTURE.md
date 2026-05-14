# MQTT Mimarisi ve Topic Hiyerarşisi Dokümantasyonu

## Genel Bakış

Akıllı Tarım Yönetim Sistemi (ATYS), sensör verilerinin gerçek zamanlı iletimi için **MQTT (Message Queuing Telemetry Transport)** protokolünü kullanır. Hafif, düşük bant genişliği gerektiren bu protokol, IoT sensörlerinden gelen verilerin hızlı ve güvenilir şekilde iletilmesini sağlar.

## Mimari Diyagram

```
┌─────────────────┐     MQTT Publish      ┌──────────────────┐
│  IoT Sensörleri  │ ──────────────────▶  │   MQTT Broker    │
│  (Simülatör)     │                      │  (HiveMQ Public) │
└─────────────────┘                      └────────┬─────────┘
                                                   │
                                          MQTT Subscribe
                                                   │
                                         ┌─────────▼──────────┐
                                         │   MQTT Listener     │
                                         │  (Django Command)   │
                                         └─────────┬──────────┘
                                                   │
                                          Channels Group Send
                                                   │
                                         ┌─────────▼──────────┐
                                         │  WebSocket Consumer │
                                         │  (SensorConsumer)   │
                                         └─────────┬──────────┘
                                                   │
                                             WebSocket
                                                   │
                                         ┌─────────▼──────────┐
                                         │   Web Dashboard     │
                                         │  (Gerçek Zamanlı)   │
                                         └────────────────────┘
```

## Broker Bilgileri

| Parametre | Değer |
|-----------|-------|
| Broker | HiveMQ Public Broker |
| Host | `broker.hivemq.com` |
| Port | `1883` (TCP) |
| Keepalive | `60` saniye |
| Kimlik Doğrulama | Yok (Public) |
| TLS/SSL | Yok (Geliştirme ortamı) |

> **Not:** Prodüksiyon ortamında yerel Mosquitto broker kullanılması ve TLS şifreleme eklenmesi önerilir.

## Topic Hiyerarşisi

```
atys/                              ← Kök topic (proje prefix'i)
│
├── sensors/                       ← Toplu sensör verisi
│   ├── humidity                   ← Nem verisi (%)
│   ├── temperature                ← Hava sıcaklığı (°C)
│   ├── soil_moisture              ← Toprak nemi (%)
│   └── ph                         ← Toprak pH değeri
│
├── commands/                      ← Cihaz kontrol komutları
│   └── irrigation                 ← Sulama sistemi açma/kapama
│
└── status/                        ← Cihaz durum bildirimleri
    └── device                     ← Cihaz bağlantı durumu
```

### Wildcard Kullanımı

| Pattern | Açıklama |
|---------|----------|
| `atys/sensors/#` | Tüm sensör topic'lerine abone ol |
| `atys/+/humidity` | Herhangi bir kategorideki nem verisi |
| `atys/#` | ATYS altındaki tüm mesajlar |

## Mesaj Formatları

### Sensör Verisi (Ayrı Topic)

Topic: `atys/sensors/humidity`

```json
{
    "field_id": 1,
    "timestamp": 1715680000.0,
    "value": 65.4
}
```

### Sensör Verisi (Toplu)

Topic: `atys/sensors`

```json
{
    "field_id": 1,
    "timestamp": 1715680000.0,
    "soil_moisture": 55.2,
    "air_temperature": 24.5,
    "humidity": 65.4,
    "ph_level": 6.8,
    "irrigation_status": 1
}
```

### Sulama Komutu

Topic: `atys/commands/irrigation`

```json
{
    "field_id": 1,
    "command": "start",
    "duration_minutes": 30,
    "timestamp": 1715680000.0
}
```

## QoS (Quality of Service) Seviyeleri

| Seviye | Adı | Kullanım |
|--------|-----|----------|
| 0 | At most once | Sensör verileri (kayıp tolere edilebilir) |
| 1 | At least once | Sulama komutları (güvenilir teslimat) |
| 2 | Exactly once | Kritik alarm bildirimleri |

## Django Management Komutları

### Sensör Simülatörü
```bash
python manage.py mqtt_simulator --interval 5
```
- Her `interval` saniyede bir tüm tarlalar için simüle edilmiş sensör verisi yayınlar
- Hem toplu (`atys/sensors`) hem ayrı topic'lere (`atys/sensors/humidity` vb.) yayın yapar

### MQTT Listener
```bash
python manage.py mqtt_listener
```
- `atys/sensors/#` wildcard ile tüm sensör topic'lerini dinler
- Gelen mesajları Django Channels grubuna (`sensor_data`) iletir
- WebSocket consumer aracılığıyla dashboard'a ulaştırır

## Test Scriptleri

### Publisher Test (Django bağımsız)
```bash
cd backend/mqtt
python publisher_test.py
```

### Subscriber Test (Django bağımsız)
```bash
cd backend/mqtt
python subscriber_test.py
```

## Konfigürasyon

Tüm MQTT ayarları `backend/mqtt/config.py` dosyasında merkezi olarak tanımlanmıştır:

```python
from mqtt.config import (
    MQTT_BROKER_HOST,      # Broker adresi
    MQTT_BROKER_PORT,      # Broker portu
    TOPIC_SENSORS,         # Sensör topic dict'i
    TOPIC_SENSORS_WILDCARD # Wildcard pattern
)
```

## Veri Akış Süreci

1. **Simülatör/Sensör** → MQTT mesajını broker'a yayınlar
2. **Broker** → Mesajı abone olan istemcilere dağıtır
3. **MQTT Listener** → Mesajı alır, JSON parse eder
4. **Django Channels** → `sensor_data` grubuna `group_send` ile iletir
5. **SensorConsumer** → WebSocket üzerinden tarayıcıya gönderir
6. **Dashboard** → JavaScript ile gerçek zamanlı güncelleme yapar
