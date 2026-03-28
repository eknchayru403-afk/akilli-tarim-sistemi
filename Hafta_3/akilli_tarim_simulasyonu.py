import random
import time
from datetime import datetime

# ==========================================================
# Proje: Akıllı Tarım Yönetim Sistemi (ATYS)
# Görev: Sensör Veri Analizi ve Karar Destek Algoritması (Python)
# Hazırlayan: Hayrunnisa Ekinci (Scrum Master)
# ==========================================================

def simulasyon_baslat():
    print(f"--- ATYS Simülasyonu Başlatıldı: {datetime.now()} ---")
    print("Teknoloji Yığını: Python, TensorFlow Hazırlık Modülü\n")

    # 5 Döngülük Örnek Veri Analizi
    for i in range(1, 6):
        # Sanal Sensör Verileri (Hocanın istediği Django/PostgreSQL entegrasyonuna uygun)
        sicaklik = round(random.uniform(18.0, 42.0), 2)
        nem = round(random.uniform(15.0, 85.0), 2)
        isik_lux = random.randint(100, 1000)

        print(f"ÖLÇÜM {i}: [Sıcaklık: {sicaklik}°C] [Nem: %{nem}] [Işık: {isik_lux} Lux]")

        # KARAR VE OPTİMİZASYON ALGORİTMASI
        if nem < 30.0:
            if sicaklik > 35.0:
                print(">> KARAR: Kritik Sıcaklık! Evaporasyon riski var. Sulama ertelendi, fanlar açıldı.")
            else:
                print(">> KARAR: Toprak Nem Seviyesi Düşük. Akıllı Sulama Pompası AKTİF.")
        
        elif nem > 75.0:
            print(">> KARAR: Yüksek Nem Algılandı. Mantar riskini önlemek için havalandırma AÇILDI.")
        
        else:
            print(">> DURUM: Bitki değerleri optimal seviyede. Kaynak tasarrufu moduna geçildi.")

        print("-" * 50)
        time.sleep(1)  # Simülasyon hızı

if __name__ == "__main__":
    simulasyon_baslat()
