-- Akıllı Tarım Sistemi Veritabanı Şeması

-- Sensörlerden gelen verileri (nem, sıcaklık vb.) saklamak için tablo
CREATE TABLE sensor_readings (
    id INT PRIMARY KEY AUTO_INCREMENT,           -- Her kayıt için benzersiz kimlik
    sensor_type VARCHAR(50) NOT NULL,            -- Sensör tipi (Örn: Toprak Nemi, Hava Sıcaklığı)
    value DOUBLE NOT NULL,                       -- Ölçülen değer
    unit VARCHAR(10),                           -- Ölçüm birimi (Örn: %, °C)
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Kaydın oluşturulduğu tarih ve saat
);

-- Cihazların (Su pompası, Fan vb.) durumlarını takip etmek için tablo
CREATE TABLE device_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_name VARCHAR(50),                     -- Cihaz adı (Örn: Su Pompası)
    action VARCHAR(20),                          -- Yapılan işlem (AÇIK / KAPALI)
    triggered_by VARCHAR(50),                    -- İşlemi kim tetikledi (Otomatik / Manuel)
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
