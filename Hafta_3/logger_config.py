"""
==========================================================
 Akıllı Tarım Yönetim Sistemi — Merkezi Günlükleme Yapılandırması
 Hazırlayan: ATYS Ekibi
==========================================================

Bu modül, projedeki tüm Python dosyaları için merkezi ve tutarlı
bir günlükleme (logging) altyapısı sağlar.

Özellikler:
  - Yapılandırılabilir log seviyeleri (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Konsol + dönen dosya (RotatingFileHandler) çift çıktı
  - Türkçe zaman damgası ve renklendirme (konsol)
  - Gereksiz günlüklerin filtrelenmesi
  - Performans dostu: lazy formatting, düşük seviye kontrolü
  - Ortam değişkenleri ile seviye yönetimi (LOG_LEVEL)
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ==========================================================
# SABİTLER
# ==========================================================

# Log dosyalarının tutulacağı dizin
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

# Varsayılan ayarlar
DEFAULT_LOG_LEVEL = "INFO"
MAX_LOG_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_BACKUP_COUNT = 3                   # En fazla 3 yedek dosya
LOG_FILE_NAME = "atys.log"

# Ortam değişkeninden seviye okuma (üretim/geliştirme esnekliği)
LOG_LEVEL = os.environ.get("ATYS_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()


# ==========================================================
# RENKLI KONSOL FORMATLAYICI
# ==========================================================

class RenkliFormatter(logging.Formatter):
    """
    Konsol çıktısını log seviyesine göre ANSI renkleriyle biçimlendirir.
    Dosya handler'ları için kullanılMAZ (renk kodları dosyada okunmaz).
    """

    # ANSI renk kodları
    RENKLER = {
        logging.DEBUG:    "\033[36m",   # Cyan
        logging.INFO:     "\033[32m",   # Yeşil
        logging.WARNING:  "\033[33m",   # Sarı
        logging.ERROR:    "\033[31m",   # Kırmızı
        logging.CRITICAL: "\033[1;31m", # Kalın Kırmızı
    }
    SIFIRLA = "\033[0m"

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record):
        renk = self.RENKLER.get(record.levelno, self.SIFIRLA)
        # Seviye adını renklendir
        orijinal_seviye = record.levelname
        record.levelname = f"{renk}{orijinal_seviye}{self.SIFIRLA}"
        sonuc = super().format(record)
        record.levelname = orijinal_seviye  # Diğer handler'ları etkilememesi için geri al
        return sonuc


# ==========================================================
# TEKİL ÖLÇÜM FİLTRESİ (Performans optimizasyonu)
# ==========================================================

class TekrarFiltresi(logging.Filter):
    """
    Aynı mesajın belirli bir süre içinde tekrar loglanmasını engeller.
    Sensör okumalarında saniyede onlarca aynı mesaj üretilmesinin önüne geçer.

    Parametreler:
        bekleme_suresi (int): Aynı mesajın tekrar loglanması için gereken
                              minimum süre (saniye). Varsayılan: 5
    """

    def __init__(self, bekleme_suresi=5):
        super().__init__()
        self._son_mesajlar = {}
        self._bekleme_suresi = bekleme_suresi

    def filter(self, record):
        mesaj_anahtari = f"{record.name}:{record.getMessage()}"
        simdi = datetime.now().timestamp()

        son_zaman = self._son_mesajlar.get(mesaj_anahtari, 0)
        if simdi - son_zaman < self._bekleme_suresi:
            return False  # Filtrele (loglanmasın)

        self._son_mesajlar[mesaj_anahtari] = simdi

        # Bellek taşmasını önle — 1000'den fazla anahtar birikirse temizle
        if len(self._son_mesajlar) > 1000:
            esik = simdi - self._bekleme_suresi * 2
            self._son_mesajlar = {
                k: v for k, v in self._son_mesajlar.items() if v > esik
            }

        return True


# ==========================================================
# SEVİYE BAZLI FİLTRE
# ==========================================================

class SeviyeFiltresi(logging.Filter):
    """
    Belirli bir seviyenin altındaki mesajları filtreler.
    Üretim ortamında DEBUG mesajlarının dosyaya yazılmasını engeller.
    """

    def __init__(self, minimum_seviye=logging.INFO):
        super().__init__()
        self._minimum_seviye = minimum_seviye

    def filter(self, record):
        return record.levelno >= self._minimum_seviye


# ==========================================================
# ANA LOGGER OLUŞTURUCU
# ==========================================================

def logger_olustur(modul_adi: str, dosyaya_yaz: bool = True) -> logging.Logger:
    """
    Verilen modül adı için yapılandırılmış bir Logger nesnesi döndürür.

    Parametreler:
        modul_adi  (str):  Logger'ın adı (genellikle __name__).
        dosyaya_yaz (bool): True ise log dosyasına da yazar. Varsayılan: True.

    Dönüş:
        logging.Logger: Yapılandırılmış logger nesnesi.

    Kullanım Örneği:
        >>> from logger_config import logger_olustur
        >>> logger = logger_olustur(__name__)
        >>> logger.info("Sistem başlatıldı")
        >>> logger.warning("Nem seviyesi düşük: %s%%", nem)
        >>> logger.error("Sensör bağlantı hatası", exc_info=True)
    """
    logger = logging.getLogger(modul_adi)

    # Aynı logger için tekrar handler eklenmesini önle
    if logger.handlers:
        return logger

    # Seviye ayarla
    seviye = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(seviye)

    # ----------------------------------------------------------
    # KONSOL HANDLER (renkli, okunabilir)
    # ----------------------------------------------------------
    konsol_format = (
        "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
    )
    konsol_handler = logging.StreamHandler(sys.stderr)
    konsol_handler.setLevel(seviye)
    konsol_handler.setFormatter(
        RenkliFormatter(fmt=konsol_format, datefmt="%H:%M:%S")
    )
    # Tekrar filtresini konsola ekle
    konsol_handler.addFilter(TekrarFiltresi(bekleme_suresi=3))
    logger.addHandler(konsol_handler)

    # ----------------------------------------------------------
    # DOSYA HANDLER (yapılandırılmış, dönen dosya)
    # ----------------------------------------------------------
    if dosyaya_yaz:
        os.makedirs(LOG_DIR, exist_ok=True)
        dosya_yolu = os.path.join(LOG_DIR, LOG_FILE_NAME)

        dosya_format = (
            "%(asctime)s | %(levelname)-8s | %(name)-25s | "
            "%(funcName)s:%(lineno)d | %(message)s"
        )
        dosya_handler = RotatingFileHandler(
            dosya_yolu,
            maxBytes=MAX_LOG_FILE_BYTES,
            backupCount=MAX_BACKUP_COUNT,
            encoding="utf-8",
        )
        dosya_handler.setLevel(logging.DEBUG)  # Dosyaya her şey yazılsın
        dosya_handler.setFormatter(
            logging.Formatter(fmt=dosya_format, datefmt="%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(dosya_handler)

    # Üst logger'a yayılmayı engelle (çift çıktı önleme)
    logger.propagate = False

    return logger


# ==========================================================
# PERFORMANS ÖLÇÜM YARDIMCISI
# ==========================================================

class PerformansOlcer:
    """
    Bir kod bloğunun çalışma süresini loglar.
    Context manager olarak kullanılır.

    Kullanım:
        >>> with PerformansOlcer(logger, "Sensör veri okuma"):
        ...     # yavaş işlem
        ...     pass
    """

    def __init__(self, logger_ref: logging.Logger, islem_adi: str):
        self._logger = logger_ref
        self._islem_adi = islem_adi
        self._baslangic = None

    def __enter__(self):
        self._baslangic = datetime.now()
        self._logger.debug("[SURE][BASLANGIC] %s", self._islem_adi)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        gecen_sure = (datetime.now() - self._baslangic).total_seconds()
        if gecen_sure > 2.0:
            self._logger.warning(
                "[SURE][YAVAS] %s - %.3f sn (esik: 2s)", self._islem_adi, gecen_sure
            )
        else:
            self._logger.info(
                "[SURE][BITIS] %s - %.3f sn", self._islem_adi, gecen_sure
            )
        return False  # İstisnaları yutma
