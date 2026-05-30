# sensor_readings — Partitioning Raporu (Şablon)

Bu rapor PostgreSQL bağlantısı olmadan oluşturuldu.

Tam EXPLAIN ANALYZE karşılaştırması için:

```bash
docker compose up -d postgres
DB_ENGINE=django.db.backends.postgresql python manage.py migrate
python manage.py setup_sensor_partitions --convert
python manage.py compare_sensor_reading_plans
```

Beklenen indeksler: `idx_sr_timestamp_brin`, `idx_sr_field_timestamp_btree`.