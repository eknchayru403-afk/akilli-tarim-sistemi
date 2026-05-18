-- sensor_readings: deklaratif aylık RANGE partitioning (tek seferlik dönüşüm)

DO $$
DECLARE
    is_partitioned BOOLEAN;
    legacy_name TEXT;
BEGIN
    SELECT (c.relkind = 'p') INTO is_partitioned
    FROM pg_class c
    WHERE c.relname = 'sensor_readings';

    IF is_partitioned THEN
        RAISE NOTICE 'sensor_readings zaten partitioned.';
        RETURN;
    END IF;

    -- Eski Django tablo adı
    IF to_regclass('sensor_readings') IS NULL AND to_regclass('iot_sensorreading') IS NOT NULL THEN
        ALTER TABLE iot_sensorreading RENAME TO sensor_readings;
    END IF;

    IF to_regclass('sensor_readings') IS NULL THEN
        RAISE EXCEPTION 'sensor_readings tablosu bulunamadı.';
    END IF;

    legacy_name := 'sensor_readings_legacy_' || to_char(clock_timestamp(), 'YYYYMMDDHH24MISS');
    EXECUTE format('ALTER TABLE sensor_readings RENAME TO %I', legacy_name);

    CREATE TABLE sensor_readings (
        id UUID NOT NULL,
        field_id BIGINT NOT NULL,
        sensor_id UUID NOT NULL,
        message_id UUID NOT NULL,
        value NUMERIC(12, 4) NOT NULL,
        unit VARCHAR(20) NOT NULL,
        raw_payload JSONB NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        received_at TIMESTAMPTZ NOT NULL,
        CONSTRAINT sensor_readings_pkey PRIMARY KEY (id, timestamp),
        CONSTRAINT sensor_readings_message_ts_key UNIQUE (message_id, timestamp),
        CONSTRAINT sensor_readings_field_id_fkey
            FOREIGN KEY (field_id) REFERENCES fields_field(id) ON DELETE CASCADE,
        CONSTRAINT sensor_readings_sensor_id_fkey
            FOREIGN KEY (sensor_id) REFERENCES iot_sensor(id) ON DELETE CASCADE
    ) PARTITION BY RANGE (timestamp);

    PERFORM sr_ensure_monthly_partitions(6);

    EXECUTE format(
        'INSERT INTO sensor_readings (
            id, field_id, sensor_id, message_id, value, unit, raw_payload, timestamp, received_at
        )
        SELECT
            id,
            field_id,
            sensor_id,
            message_id,
            value,
            unit,
            raw_payload,
            timestamp,
            received_at
        FROM %I',
        legacy_name
    );

    EXECUTE format('DROP TABLE %I', legacy_name);

    -- İndeksler (partition parent üzerinde)
    CREATE INDEX idx_sr_field_timestamp_btree ON sensor_readings (field_id, timestamp);
    CREATE INDEX idx_sr_field_id_btree ON sensor_readings (field_id);
    CREATE INDEX idx_sr_sensor_timestamp ON sensor_readings (sensor_id, timestamp);
    CREATE INDEX idx_sr_timestamp_brin ON sensor_readings USING BRIN (timestamp)
        WITH (pages_per_range = 128);
END;
$$;
