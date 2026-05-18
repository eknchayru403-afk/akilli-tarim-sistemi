# Sensör Okuma Analitiği — Performans Raporu

**Oluşturulma:** 2026-05-18T18:51:24.547066+00:00  
**Veritabanı:** sqlite (C:\Users\mert\akilli-tarim-sistemi\backend\db.sqlite3)  
**Tarih aralığı:** 2026-04-18T18:51:24.547066+00:00 → 2026-05-18T18:51:24.547066+00:00  

## 1. İndeks ve partitioning

| Öğe | Açıklama |
|-----|----------|
| `idx_reading_sensor_measured_at` | B-tree `(sensor_id, measured_at)` — sensör + zaman aralığı |
| `idx_reading_measured_sensor` | B-tree `(measured_at, sensor_id)` — zaman öncelikli tarama |
| `idx_reading_measured_at_brin` | BRIN `(measured_at)` — PostgreSQL geniş aralık taraması |
| Aylık partition | `iot_sensorreading_YYYY_MM` — `setup_sensor_partitions` |

## 2. Analitik sorgular (Django ORM)

### 2.1 Sensör tipine göre avg / min / max

```python
SensorAnalyticsService.aggregate_by_sensor_type(start=..., end=...)
```

**Süre:** 7.17 ms  
**Satır:** 4 sensör tipi  

| sensor_type | avg | min | max | count |
|-------------|-----|-----|-----|-------|
| nem | 50.4604802970297 | 10.0462000000000 | 89.9827000000000 | 1010 |
| ph | 49.8929505060728 | 10.1003000000000 | 89.9694000000000 | 988 |
| sicaklik | 50.8879108445297 | 10.0230000000000 | 89.9796000000000 | 1042 |
| yagis | 51.0412923326133 | 10.0547000000000 | 89.9103000000000 | 926 |

**EXPLAIN:**

```text
9 | 0 | 0 | SEARCH iot_sensorreading USING INDEX idx_reading_measured_sensor (measured_at>? AND measured_at<?)
19 | 0 | 0 | SEARCH iot_sensor USING INDEX sqlite_autoindex_iot_sensor_1 (id=?)
24 | 0 | 0 | USE TEMP B-TREE FOR GROUP BY
```

### 2.2 Filtre: sensor_type = `nem`

**Süre:** 3.04 ms  

```text
6 | 0 | 0 | SEARCH iot_sensorreading USING INDEX idx_reading_measured_sensor (measured_at>? AND measured_at<?)
16 | 0 | 0 | SEARCH iot_sensor USING INDEX sqlite_autoindex_iot_sensor_1 (id=?)
```

### 2.3 Genel özet (tüm tipler)

**Süre:** 2.71 ms  
- avg: 50.5670095814424  
- min: 10.0230000000000  
- max: 89.9827000000000  
- count: 3966  

## 3. Referans SQL

```sql
SELECT
    s.sensor_type,
    AVG(r.value)   AS avg_value,
    MIN(r.value)   AS min_value,
    MAX(r.value)   AS max_value,
    COUNT(*)       AS reading_count
FROM iot_sensorreading r
INNER JOIN iot_sensor s ON s.id = r.sensor_id
WHERE r.measured_at >= %(start)s
  AND r.measured_at < %(end)s
  
GROUP BY s.sensor_type
ORDER BY s.sensor_type;
```

## 4. PostgreSQL — beklenen EXPLAIN ANALYZE planı

Docker PostgreSQL ile (`DB_ENGINE=django.db.backends.postgresql`):

```bash
docker compose up -d postgres
cd backend
set DB_ENGINE=django.db.backends.postgresql
python manage.py migrate
python manage.py benchmark_sensor_analytics --seed 50000
python manage.py setup_sensor_partitions --convert
python manage.py setup_sensor_partitions --months-ahead 6
```

**Beklenen plan (aggregate_by_sensor_type, partitioned tablo):**

```text
Aggregate  (cost=... rows=8 width=...)
  ->  Hash Join  (cost=... rows=... width=...)
        Hash Cond: (r.sensor_id = s.id)
        ->  Append  (cost=0.00..rows=...)   -- yalnızca ilgili aylık partition'lar
              ->  Seq Scan on iot_sensorreading_2026_04 r
                    Filter: (measured_at >= ... AND measured_at < ...)
              ->  Seq Scan on iot_sensorreading_2026_05 r
                    Filter: (measured_at >= ... AND measured_at < ...)
        ->  Hash
              ->  Seq Scan on iot_sensor s
```

Partition pruning sayesinde `measured_at` aralığı daraldıkça taranan veri hacmi düşer.  
Sensör bazlı sorgularda `idx_reading_sensor_measured_at` → **Bitmap Index Scan** veya **Index Scan** beklenir.

## 5. Komutlar

```bash
python manage.py setup_sensor_partitions --months-ahead 6
python manage.py setup_sensor_partitions --convert  # tek seferlik PG dönüşüm
python manage.py benchmark_sensor_analytics --seed 50000
```
