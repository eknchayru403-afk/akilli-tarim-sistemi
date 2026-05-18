-- sensor_readings: BRIN (timestamp) + B-tree (field_id, timestamp)

DROP INDEX IF EXISTS idx_reading_measured_at_brin;
DROP INDEX IF EXISTS idx_sr_timestamp_brin;
DROP INDEX IF EXISTS idx_sr_field_id_btree;
DROP INDEX IF EXISTS idx_sr_field_timestamp_btree;

-- BRIN: geniş zaman aralığı taramaları (düşük depolama)
CREATE INDEX idx_sr_timestamp_brin
    ON sensor_readings USING BRIN (timestamp)
    WITH (pages_per_range = 128);

-- B-tree: tarla + zaman aralığı (en sık sorgu kalıbı)
CREATE INDEX idx_sr_field_timestamp_btree
    ON sensor_readings (field_id, timestamp);

-- B-tree: yalnızca field_id (tarla bazlı sayım / join)
CREATE INDEX idx_sr_field_id_btree
    ON sensor_readings (field_id);
