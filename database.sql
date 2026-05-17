-- Akıllı Tarım Sistemi Veritabanı Şeması (Python ile uyumlu)

-- Sensör verilerini saklayan tablo
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    sensor_type VARCHAR(50),      -- Örn: 'nem', 'sicaklik'
    value FLOAT,                  -- Ölçülen değer
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Pompa veya fan işlemlerini saklayan tablo
CREATE TABLE device_logs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    device_name VARCHAR(50),      -- Örn: 'su_pompasi'
    status VARCHAR(20),           -- Örn: 'ACIK', 'KAPALI'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
