-- Aylık RANGE partitioning: sensor_readings (partition key: timestamp)

CREATE OR REPLACE FUNCTION sr_create_monthly_partition(p_month DATE)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    partition_name TEXT;
    range_start DATE;
    range_end DATE;
BEGIN
    range_start := date_trunc('month', p_month)::DATE;
    range_end := (range_start + INTERVAL '1 month')::DATE;
    partition_name := format('sensor_readings_%s', to_char(range_start, 'YYYY_MM'));

    IF to_regclass(partition_name) IS NOT NULL THEN
        RETURN;
    END IF;

    EXECUTE format(
        'CREATE TABLE %I PARTITION OF sensor_readings
         FOR VALUES FROM (%L) TO (%L)',
        partition_name,
        range_start,
        range_end
    );
END;
$$;

CREATE OR REPLACE FUNCTION sr_ensure_monthly_partitions(months_ahead INT DEFAULT 6)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN -2..months_ahead LOOP
        PERFORM sr_create_monthly_partition(
            (date_trunc('month', CURRENT_DATE) + (i || ' months')::INTERVAL)::DATE
        );
    END LOOP;
END;
$$;

-- Geriye dönük uyumluluk (eski fonksiyon adları)
CREATE OR REPLACE FUNCTION iot_create_sensor_reading_partition(p_month DATE)
RETURNS VOID LANGUAGE sql AS $$
    SELECT sr_create_monthly_partition(p_month);
$$;

CREATE OR REPLACE FUNCTION iot_ensure_sensor_reading_partitions(months_ahead INT DEFAULT 6)
RETURNS VOID LANGUAGE sql AS $$
    SELECT sr_ensure_monthly_partitions(months_ahead);
$$;
