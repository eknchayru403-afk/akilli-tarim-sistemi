-- BRIN index: düşük depolama maliyetiyle geniş zaman aralığı taramaları
CREATE INDEX IF NOT EXISTS idx_reading_measured_at_brin
    ON iot_sensorreading USING BRIN (measured_at)
    WITH (pages_per_range = 128);
