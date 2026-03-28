-- ============================================================
--  Akıllı Tarım Yönetim Sistemi — PostgreSQL Veritabanı Şeması
--  Teknoloji: PostgreSQL 15+
--  Hazırlayan: ATS Ekibi
-- ============================================================

-- Gerekli uzantılar
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- ENUM TİPLERİ
-- ============================================================

CREATE TYPE kullanici_rol AS ENUM (
    'admin',
    'scrum_master',
    'arastirmaci',
    'gelistirici',
    'gozlemci'
);

CREATE TYPE kullanici_durum AS ENUM (
    'aktif',
    'pasif',
    'cevrimici',
    'cevrimdisi',
    'askida'
);

CREATE TYPE sensor_tip AS ENUM (
    'nem',
    'sicaklik',
    'ph',
    'yagis',
    'isik',
    'toprak_nemi',
    'co2',
    'ruzgar'
);

CREATE TYPE sensor_durum AS ENUM (
    'aktif',
    'pasif',
    'baglanti_yok',
    'hata',
    'bakimda'
);

CREATE TYPE plan_durum AS ENUM (
    'planlandı',
    'devam_ediyor',
    'tamamlandı',
    'iptal_edildi',
    'beklemede'
);

CREATE TYPE plan_kaynak AS ENUM (
    'manuel',
    'yapay_zeka',
    'zamanlayici'
);

CREATE TYPE bildirim_tip AS ENUM (
    'kritik_uyari',
    'uyari',
    'bilgi',
    'sistem',
    'gorev'
);

CREATE TYPE bildirim_oncelik AS ENUM (
    'dusuk',
    'orta',
    'yuksek',
    'kritik'
);

CREATE TYPE tahmin_turu AS ENUM (
    'sulama_ihtiyaci',
    'gubreleme_ihtiyaci',
    'hasat_zamani',
    'hastalik_riski',
    'verim_tahmini',
    'hava_durumu'
);

-- ============================================================
-- 1. KULLANICILAR
-- ============================================================

CREATE TABLE kullanicilar (
    id                UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    ad_soyad          VARCHAR(120)    NOT NULL,
    email             VARCHAR(254)    NOT NULL UNIQUE,
    sifre_hash        TEXT            NOT NULL,
    rol               kullanici_rol   NOT NULL DEFAULT 'gozlemci',
    durum             kullanici_durum NOT NULL DEFAULT 'pasif',
    profil_foto_url   TEXT,
    telefon           VARCHAR(20),
    olusturma_tarihi  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    guncelleme_tarihi TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    son_giris         TIMESTAMPTZ
);

COMMENT ON TABLE kullanicilar IS 'Sisteme erişim yetkisi olan tüm kullanıcılar';
COMMENT ON COLUMN kullanicilar.sifre_hash IS 'bcrypt ile hashlenmiş parola';
COMMENT ON COLUMN kullanicilar.rol IS 'Kullanıcının sistem içindeki rolü';

CREATE INDEX idx_kullanicilar_email  ON kullanicilar(email);
CREATE INDEX idx_kullanicilar_rol    ON kullanicilar(rol);
CREATE INDEX idx_kullanicilar_durum  ON kullanicilar(durum);

-- ============================================================
-- 2. TARLALAR
-- ============================================================

CREATE TABLE tarlalar (
    id                UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    kullanici_id      UUID         NOT NULL REFERENCES kullanicilar(id) ON DELETE RESTRICT,
    ad                VARCHAR(120) NOT NULL,
    alan_dekar        NUMERIC(10,2) NOT NULL CHECK (alan_dekar > 0),
    konum_lat         NUMERIC(9,6),
    konum_lon         NUMERIC(9,6),
    konum_adi         VARCHAR(200),
    mahsul_turu       VARCHAR(100),
    toprak_tipi       VARCHAR(80),
    sulama_sistemi    VARCHAR(80),
    aktif             BOOLEAN      NOT NULL DEFAULT TRUE,
    olusturma_tarihi  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    guncelleme_tarihi TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE tarlalar IS 'Sisteme kayıtlı tarım alanları';
COMMENT ON COLUMN tarlalar.kullanici_id IS 'Tarlayı yöneten birincil kullanıcı';
COMMENT ON COLUMN tarlalar.alan_dekar IS 'Tarla alanı dekar cinsinden';

CREATE INDEX idx_tarlalar_kullanici ON tarlalar(kullanici_id);
CREATE INDEX idx_tarlalar_aktif     ON tarlalar(aktif);

-- ============================================================
-- 3. SENSORLER
-- ============================================================

CREATE TABLE sensorler (
    id                UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    tarla_id          UUID          NOT NULL REFERENCES tarlalar(id) ON DELETE CASCADE,
    ad                VARCHAR(120)  NOT NULL,
    tip               sensor_tip    NOT NULL,
    konum_adi         VARCHAR(200),
    konum_lat         NUMERIC(9,6),
    konum_lon         NUMERIC(9,6),
    durum             sensor_durum  NOT NULL DEFAULT 'pasif',
    mac_adresi        VARCHAR(17)   UNIQUE,
    firmware_versiyon VARCHAR(20),
    baglanti_protokol VARCHAR(20)   DEFAULT 'MQTT',
    son_veri_zamani   TIMESTAMPTZ,
    olusturma_tarihi  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    guncelleme_tarihi TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sensorler IS 'Tarla bazlı IoT sensör envanter';
COMMENT ON COLUMN sensorler.mac_adresi IS 'Sensörün fiziksel MAC adresi (benzersiz)';
COMMENT ON COLUMN sensorler.baglanti_protokol IS 'MQTT, HTTP, LoRa vb.';

CREATE INDEX idx_sensorler_tarla  ON sensorler(tarla_id);
CREATE INDEX idx_sensorler_tip    ON sensorler(tip);
CREATE INDEX idx_sensorler_durum  ON sensorler(durum);

-- ============================================================
-- 4. SENSÖR VERİLERİ (zaman serisi)
-- ============================================================

CREATE TABLE sensor_verileri (
    id             UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id      UUID          NOT NULL REFERENCES sensorler(id) ON DELETE CASCADE,
    deger          NUMERIC(12,4) NOT NULL,
    birim          VARCHAR(20)   NOT NULL,
    ham_veri       JSONB,
    olcum_zamani   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sensor_verileri IS 'Sensörlerden gelen ham ölçüm verileri (zaman serisi)';
COMMENT ON COLUMN sensor_verileri.ham_veri IS 'Sensörden gelen tam JSON paketi';

CREATE INDEX idx_sensor_verileri_sensor  ON sensor_verileri(sensor_id);
CREATE INDEX idx_sensor_verileri_zaman   ON sensor_verileri(olcum_zamani DESC);
CREATE INDEX idx_sensor_verileri_birlesik ON sensor_verileri(sensor_id, olcum_zamani DESC);

-- Son 90 günlük veriyi sık sorgulayan sorgular için bölümlenmiş index
CREATE INDEX idx_sensor_verileri_son_90gun
    ON sensor_verileri(sensor_id, olcum_zamani DESC)
    WHERE olcum_zamani >= NOW() - INTERVAL '90 days';

-- ============================================================
-- 5. SULAMA PLANLARI
-- ============================================================

CREATE TABLE sulama_planlari (
    id                UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    tarla_id          UUID          NOT NULL REFERENCES tarlalar(id) ON DELETE CASCADE,
    kullanici_id      UUID          NOT NULL REFERENCES kullanicilar(id) ON DELETE RESTRICT,
    baslangic_zamani  TIMESTAMPTZ   NOT NULL,
    bitis_zamani      TIMESTAMPTZ,
    miktar_litre      NUMERIC(10,2) CHECK (miktar_litre >= 0),
    durum             plan_durum    NOT NULL DEFAULT 'planlandı',
    kaynak            plan_kaynak   NOT NULL DEFAULT 'manuel',
    sulama_yontemi    VARCHAR(80),
    notlar            TEXT,
    olusturma_tarihi  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    guncelleme_tarihi TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_sulama_zaman CHECK (bitis_zamani IS NULL OR bitis_zamani > baslangic_zamani)
);

COMMENT ON TABLE sulama_planlari IS 'Tarla bazlı sulama program ve kayıtları';
COMMENT ON COLUMN sulama_planlari.kaynak IS 'Planı kimin/neyin oluşturduğu';

CREATE INDEX idx_sulama_tarla    ON sulama_planlari(tarla_id);
CREATE INDEX idx_sulama_kullanici ON sulama_planlari(kullanici_id);
CREATE INDEX idx_sulama_durum    ON sulama_planlari(durum);
CREATE INDEX idx_sulama_zaman    ON sulama_planlari(baslangic_zamani);

-- ============================================================
-- 6. GÜBRELEME PLANLARI
-- ============================================================

CREATE TABLE gubreleme_planlari (
    id                UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    tarla_id          UUID          NOT NULL REFERENCES tarlalar(id) ON DELETE CASCADE,
    kullanici_id      UUID          NOT NULL REFERENCES kullanicilar(id) ON DELETE RESTRICT,
    gubre_turu        VARCHAR(100)  NOT NULL,
    uygulama_yontemi  VARCHAR(80),
    miktar_kg         NUMERIC(10,3) NOT NULL CHECK (miktar_kg > 0),
    planlanan_tarih   DATE          NOT NULL,
    uygulanan_tarih   DATE,
    durum             plan_durum    NOT NULL DEFAULT 'planlandı',
    kaynak            plan_kaynak   NOT NULL DEFAULT 'manuel',
    notlar            TEXT,
    olusturma_tarihi  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    guncelleme_tarihi TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE gubreleme_planlari IS 'Tarla bazlı gübreleme program ve kayıtları';

CREATE INDEX idx_gubreleme_tarla      ON gubreleme_planlari(tarla_id);
CREATE INDEX idx_gubreleme_kullanici  ON gubreleme_planlari(kullanici_id);
CREATE INDEX idx_gubreleme_durum      ON gubreleme_planlari(durum);
CREATE INDEX idx_gubreleme_tarih      ON gubreleme_planlari(planlanan_tarih);

-- ============================================================
-- 7. İLAÇLAMA PLANLARI
-- ============================================================

CREATE TABLE ilacalama_planlari (
    id                UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    tarla_id          UUID          NOT NULL REFERENCES tarlalar(id) ON DELETE CASCADE,
    kullanici_id      UUID          NOT NULL REFERENCES kullanicilar(id) ON DELETE RESTRICT,
    ilac_adi          VARCHAR(150)  NOT NULL,
    etken_madde       VARCHAR(150),
    doz_lt_per_dekar  NUMERIC(8,4)  NOT NULL CHECK (doz_lt_per_dekar > 0),
    toplam_doz_lt     NUMERIC(10,3),
    hedef_hastalik    VARCHAR(200),
    planlanan_tarih   DATE          NOT NULL,
    uygulanan_tarih   DATE,
    durum             plan_durum    NOT NULL DEFAULT 'planlandı',
    kaynak            plan_kaynak   NOT NULL DEFAULT 'manuel',
    guvenli_bekleme_gun INTEGER     CHECK (guvenli_bekleme_gun >= 0),
    notlar            TEXT,
    olusturma_tarihi  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    guncelleme_tarihi TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ilacalama_planlari IS 'Tarla bazlı ilaçlama program ve kayıtları';
COMMENT ON COLUMN ilacalama_planlari.guvenli_bekleme_gun IS 'İlaçlama sonrası hasat güvenlik süresi (gün)';

CREATE INDEX idx_ilacalama_tarla      ON ilacalama_planlari(tarla_id);
CREATE INDEX idx_ilacalama_kullanici  ON ilacalama_planlari(kullanici_id);
CREATE INDEX idx_ilacalama_durum      ON ilacalama_planlari(durum);
CREATE INDEX idx_ilacalama_tarih      ON ilacalama_planlari(planlanan_tarih);

-- ============================================================
-- 8. BİLDİRİMLER
-- ============================================================

CREATE TABLE bildirimler (
    id                UUID               PRIMARY KEY DEFAULT uuid_generate_v4(),
    kullanici_id      UUID               NOT NULL REFERENCES kullanicilar(id) ON DELETE CASCADE,
    sensor_id         UUID               REFERENCES sensorler(id) ON DELETE SET NULL,
    tarla_id          UUID               REFERENCES tarlalar(id) ON DELETE SET NULL,
    tip               bildirim_tip       NOT NULL DEFAULT 'bilgi',
    oncelik           bildirim_oncelik   NOT NULL DEFAULT 'orta',
    baslik            VARCHAR(255)       NOT NULL,
    mesaj             TEXT               NOT NULL,
    okundu            BOOLEAN            NOT NULL DEFAULT FALSE,
    okunma_zamani     TIMESTAMPTZ,
    olusturma_tarihi  TIMESTAMPTZ        NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE bildirimler IS 'Kullanıcıya gönderilen sistem bildirimleri ve uyarılar';

CREATE INDEX idx_bildirimler_kullanici ON bildirimler(kullanici_id);
CREATE INDEX idx_bildirimler_sensor    ON bildirimler(sensor_id);
CREATE INDEX idx_bildirimler_okundu    ON bildirimler(kullanici_id, okundu) WHERE okundu = FALSE;
CREATE INDEX idx_bildirimler_oncelik   ON bildirimler(oncelik);
CREATE INDEX idx_bildirimler_tarih     ON bildirimler(olusturma_tarihi DESC);

-- ============================================================
-- 9. YAPAY ZEKA TAHMİNLERİ
-- ============================================================

CREATE TABLE ai_tahminler (
    id                UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    tarla_id          UUID          NOT NULL REFERENCES tarlalar(id) ON DELETE CASCADE,
    sensor_id         UUID          REFERENCES sensorler(id) ON DELETE SET NULL,
    model_turu        VARCHAR(80)   NOT NULL,
    model_versiyonu   VARCHAR(20),
    tahmin_turu       tahmin_turu   NOT NULL,
    tahmin_zamani     TIMESTAMPTZ,
    sonuc             JSONB         NOT NULL,
    guven_skoru       NUMERIC(5,4)  CHECK (guven_skoru BETWEEN 0 AND 1),
    kullanildi        BOOLEAN       NOT NULL DEFAULT FALSE,
    olusturma_tarihi  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ai_tahminler IS 'TensorFlow modelleri tarafından üretilen tarım tahminleri';
COMMENT ON COLUMN ai_tahminler.sonuc IS 'Tahmin çıktısı (JSON formatında, modele göre değişir)';
COMMENT ON COLUMN ai_tahminler.guven_skoru IS '0.0 ile 1.0 arasında model güven skoru';

CREATE INDEX idx_ai_tarla        ON ai_tahminler(tarla_id);
CREATE INDEX idx_ai_tahmin_turu  ON ai_tahminler(tahmin_turu);
CREATE INDEX idx_ai_tarih        ON ai_tahminler(olusturma_tarihi DESC);
CREATE INDEX idx_ai_sonuc        ON ai_tahminler USING GIN(sonuc);

-- ============================================================
-- 10. AKTİVİTE LOGLARI
-- ============================================================

CREATE TABLE aktivite_loglari (
    id               UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    kullanici_id     UUID         REFERENCES kullanicilar(id) ON DELETE SET NULL,
    eylem            VARCHAR(100) NOT NULL,
    tablo_adi        VARCHAR(80),
    kayit_id         UUID,
    eski_deger       JSONB,
    yeni_deger       JSONB,
    ip_adresi        INET,
    kullanici_ajan   TEXT,
    olusturma_tarihi TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE aktivite_loglari IS 'Kullanıcı eylemlerinin denetim kaydı';
COMMENT ON COLUMN aktivite_loglari.eski_deger IS 'Güncelleme öncesi kayıt durumu';
COMMENT ON COLUMN aktivite_loglari.yeni_deger IS 'Güncelleme sonrası kayıt durumu';

CREATE INDEX idx_log_kullanici ON aktivite_loglari(kullanici_id);
CREATE INDEX idx_log_tarih     ON aktivite_loglari(olusturma_tarihi DESC);
CREATE INDEX idx_log_tablo     ON aktivite_loglari(tablo_adi);

-- ============================================================
-- TRIGGER: guncelleme_tarihi otomatik güncelleme
-- ============================================================

CREATE OR REPLACE FUNCTION guncelleme_tarihi_yukle()
RETURNS TRIGGER AS $$
BEGIN
    NEW.guncelleme_tarihi = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_kullanicilar_guncelle
    BEFORE UPDATE ON kullanicilar
    FOR EACH ROW EXECUTE FUNCTION guncelleme_tarihi_yukle();

CREATE TRIGGER trg_tarlalar_guncelle
    BEFORE UPDATE ON tarlalar
    FOR EACH ROW EXECUTE FUNCTION guncelleme_tarihi_yukle();

CREATE TRIGGER trg_sensorler_guncelle
    BEFORE UPDATE ON sensorler
    FOR EACH ROW EXECUTE FUNCTION guncelleme_tarihi_yukle();

CREATE TRIGGER trg_sulama_guncelle
    BEFORE UPDATE ON sulama_planlari
    FOR EACH ROW EXECUTE FUNCTION guncelleme_tarihi_yukle();

CREATE TRIGGER trg_gubreleme_guncelle
    BEFORE UPDATE ON gubreleme_planlari
    FOR EACH ROW EXECUTE FUNCTION guncelleme_tarihi_yukle();

CREATE TRIGGER trg_ilacalama_guncelle
    BEFORE UPDATE ON ilacalama_planlari
    FOR EACH ROW EXECUTE FUNCTION guncelleme_tarihi_yukle();

-- ============================================================
-- TRIGGER: okundu güncellendiğinde okunma_zamani ata
-- ============================================================

CREATE OR REPLACE FUNCTION bildirim_okunma_zamani()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.okundu = TRUE AND OLD.okundu = FALSE THEN
        NEW.okunma_zamani = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_bildirim_okundu
    BEFORE UPDATE ON bildirimler
    FOR EACH ROW EXECUTE FUNCTION bildirim_okunma_zamani();

-- ============================================================
-- VIEW: sensörlerin son ölçüm değerleri
-- ============================================================

CREATE VIEW v_sensor_son_degerler AS
SELECT
    s.id           AS sensor_id,
    s.ad           AS sensor_adi,
    s.tip,
    s.durum,
    t.ad           AS tarla_adi,
    sv.deger,
    sv.birim,
    sv.olcum_zamani,
    NOW() - sv.olcum_zamani AS gecen_sure
FROM sensorler s
JOIN tarlalar t ON t.id = s.tarla_id
LEFT JOIN LATERAL (
    SELECT deger, birim, olcum_zamani
    FROM sensor_verileri
    WHERE sensor_id = s.id
    ORDER BY olcum_zamani DESC
    LIMIT 1
) sv ON TRUE;

-- ============================================================
-- VIEW: tarla özet istatistikleri
-- ============================================================

CREATE VIEW v_tarla_ozet AS
SELECT
    t.id,
    t.ad,
    t.alan_dekar,
    t.mahsul_turu,
    COUNT(DISTINCT s.id)  AS aktif_sensor_sayisi,
    COUNT(DISTINCT sp.id) FILTER (WHERE sp.durum = 'planlandı') AS bekleyen_sulama,
    COUNT(DISTINCT gp.id) FILTER (WHERE gp.durum = 'planlandı') AS bekleyen_gubreleme,
    COUNT(DISTINCT ip.id) FILTER (WHERE ip.durum = 'planlandı') AS bekleyen_ilacalama
FROM tarlalar t
LEFT JOIN sensorler s       ON s.tarla_id = t.id AND s.durum = 'aktif'
LEFT JOIN sulama_planlari sp ON sp.tarla_id = t.id
LEFT JOIN gubreleme_planlari gp ON gp.tarla_id = t.id
LEFT JOIN ilacalama_planlari ip ON ip.tarla_id = t.id
WHERE t.aktif = TRUE
GROUP BY t.id, t.ad, t.alan_dekar, t.mahsul_turu;

-- ============================================================
-- ÖRNEK VERİ: Sistem kullanıcıları (projeakisi.md'den)
-- ============================================================

INSERT INTO kullanicilar (ad_soyad, email, sifre_hash, rol, durum) VALUES
    ('Hayrunnisa Ekinci', 'hayrunnisa@ats.com', crypt('ATS2026!', gen_salt('bf')), 'scrum_master', 'aktif'),
    ('Betül Bilhan',      'betul@ats.com',      crypt('ATS2026!', gen_salt('bf')), 'arastirmaci',  'aktif'),
    ('İrfan Duman',       'irfan@ats.com',      crypt('ATS2026!', gen_salt('bf')), 'gelistirici',  'aktif'),
    ('Ahmed Osman',       'ahmed@ats.com',      crypt('ATS2026!', gen_salt('bf')), 'gelistirici',  'pasif'),
    ('İsmet Mert Uysal',  'ismet@ats.com',      crypt('ATS2026!', gen_salt('bf')), 'gelistirici',  'aktif');

-- ============================================================
-- ÖRNEK VERİ: Tarlalar
-- ============================================================

INSERT INTO tarlalar (kullanici_id, ad, alan_dekar, konum_adi, mahsul_turu, toprak_tipi, sulama_sistemi)
SELECT id, 'Tarla A — Kuzey', 45.50, 'Elazığ / Baskil', 'Buğday', 'Killi-tınlı', 'Damla sulama'
FROM kullanicilar WHERE email = 'hayrunnisa@ats.com';

INSERT INTO tarlalar (kullanici_id, ad, alan_dekar, konum_adi, mahsul_turu, toprak_tipi, sulama_sistemi)
SELECT id, 'Tarla B — Güney', 32.75, 'Elazığ / Sivrice', 'Mısır', 'Kumlu-tınlı', 'Yağmurlama'
FROM kullanicilar WHERE email = 'hayrunnisa@ats.com';

-- ============================================================
-- ÖRNEK VERİ: Sensörler
-- ============================================================

INSERT INTO sensorler (tarla_id, ad, tip, konum_adi, durum, baglanti_protokol)
SELECT id, 'Nem Sensörü 1', 'nem',      'Tarla A — Kuzey', 'aktif', 'MQTT' FROM tarlalar WHERE ad = 'Tarla A — Kuzey';
INSERT INTO sensorler (tarla_id, ad, tip, konum_adi, durum, baglanti_protokol)
SELECT id, 'Sıcaklık S. 2', 'sicaklik', 'Tarla B — Güney', 'aktif', 'MQTT' FROM tarlalar WHERE ad = 'Tarla B — Güney';
INSERT INTO sensorler (tarla_id, ad, tip, konum_adi, durum, baglanti_protokol)
SELECT id, 'PH Sensörü 3',  'ph',       'Tarla A — Merkez', 'aktif', 'MQTT' FROM tarlalar WHERE ad = 'Tarla A — Kuzey';
INSERT INTO sensorler (tarla_id, ad, tip, konum_adi, durum, baglanti_protokol)
SELECT id, 'Yağış S. 4',    'yagis',    'İstasyon 1', 'baglanti_yok', 'MQTT' FROM tarlalar WHERE ad = 'Tarla B — Güney';
